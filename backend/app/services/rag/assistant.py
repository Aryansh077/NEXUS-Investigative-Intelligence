"""
Grounded RAG Investigation Assistant
Provides strictly grounded, evidence-backed answers for cybercrime cases,
predictions, money flows, and evidence without hallucinations.
If supporting information cannot be found, returns: 'No supporting record was found.'
"""

import json
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ...database.models import Complaint, Case, Transaction, Prediction, Alert, Evidence, Account

def build_case_knowledge_base(db: Session, case_id: str) -> List[Dict[str, Any]]:
    """
    Constructs indexed chunks of evidence and case facts for grounded retrieval.
    """
    chunks = []
    
    # 1. Case details
    case = db.query(Case).filter_by(id=case_id).first()
    if case:
        chunks.append({
            "chunk_id": f"CHUNK-CASE-{case.id}",
            "type": "CASE_METADATA",
            "text": f"Case {case.id}: {case.title}. Category: {case.category}. Syndicate: {case.syndicate_name}. City: {case.city}. Primary Cash-out Corridor: {case.primary_cluster}. Status: {case.status}.",
            "case_id": case.id
        })

    # 2. Complaints
    complaints = db.query(Complaint).filter_by(case_id=case_id).all()
    for c in complaints:
        chunks.append({
            "chunk_id": f"CHUNK-CMP-{c.id}",
            "type": "COMPLAINT",
            "text": f"Complaint {c.id}: Victim {c.victim_name} reported fraud loss of INR {c.fraud_amount:,.0f} on {c.incident_timestamp}. Crime category: {c.crime_category}. City: {c.city}. Narrative: {c.narrative}",
            "complaint_id": c.id,
            "amount": c.fraud_amount
        })

    # 3. Transactions
    txs = db.query(Transaction).filter_by(case_id=case_id).all()
    for tx in txs:
        chunks.append({
            "chunk_id": f"CHUNK-TX-{tx.id}",
            "type": "TRANSACTION",
            "text": f"Transaction {tx.id}: Hop Level {tx.hop_level}, Sender Account {tx.sender_account} transferred INR {tx.amount:,.0f} to Receiver {tx.receiver_account} via {tx.channel} on {tx.timestamp}. Velocity Score: {tx.velocity_score}.",
            "tx_id": tx.id,
            "amount": tx.amount
        })

    # 4. Predictions & Alerts
    preds = db.query(Prediction).filter_by(case_id=case_id).all()
    for p in preds:
        expl = json.loads(p.explanation_json) if p.explanation_json else {}
        chunks.append({
            "chunk_id": f"CHUNK-PRED-{p.id}",
            "type": "PREDICTION",
            "text": f"Prediction {p.id}: Complaint {p.complaint_id} ranked location {p.cluster_id} with calibrated Risk Score {p.risk_score:.0f}/100 (Rank #{p.rank}). Prediction window: {p.window_start} to {p.window_end}. Model: {p.model_name} ({p.model_version}). Explanation: {expl.get('summary', '')}",
            "prediction_id": p.id,
            "risk_score": p.risk_score
        })

    # 5. Evidence
    evidence_items = db.query(Evidence).filter_by(case_id=case_id).all()
    for ev in evidence_items:
        chunks.append({
            "chunk_id": f"CHUNK-EV-{ev.id}",
            "type": "EVIDENCE",
            "text": f"Evidence Record {ev.id}: Title: '{ev.title}'. Record type: {ev.record_type}. SHA-256 Hash: {ev.hash}. Source file: {ev.source_file}. Recorded at: {ev.timestamp}.",
            "evidence_id": ev.id,
            "hash": ev.hash
        })

    return chunks

def retrieve_grounded_context(chunks: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Keyword and token-overlap retrieval for local grounded RAG.
    """
    query_tokens = set(query.lower().replace("?", "").replace(",", "").split())
    scored = []
    
    for c in chunks:
        text_tokens = set(c["text"].lower().split())
        overlap = len(query_tokens.intersection(text_tokens))
        if overlap > 0:
            scored.append((overlap, c))

    scored.sort(key=lambda x: -x[0])
    return [item[1] for item in scored[:top_k]]

def ask_investigation_assistant(db: Session, case_id: str, question: str) -> Dict[str, Any]:
    """
    Answers questions using ONLY verified local case chunks.
    Never invents facts. Returns 'No supporting record was found.' if ungrounded.
    """
    chunks = build_case_knowledge_base(db, case_id)
    if not chunks:
        return {
            "question": question,
            "answer": "No supporting record was found for this case.",
            "grounded": False,
            "sources": []
        }

    relevant_chunks = retrieve_grounded_context(chunks, question, top_k=4)
    if not relevant_chunks:
        return {
            "question": question,
            "answer": "No supporting record was found in the indexed case evidence matching your query.",
            "grounded": False,
            "sources": []
        }

    # Synthesize grounded answer
    sources = []
    for c in relevant_chunks:
        sources.append({
            "chunk_id": c["chunk_id"],
            "type": c["type"],
            "snippet": c["text"][:140] + "..."
        })

    q_lower = question.lower()
    
    # 1. Why was location ranked high / explanation
    if "why" in q_lower or "ranked" in q_lower or "explain" in q_lower or "prediction" in q_lower:
        pred_chunk = next((c for c in relevant_chunks if c["type"] == "PREDICTION"), None)
        if pred_chunk:
            return {
                "question": question,
                "answer": f"Grounded Finding from ML Model: {pred_chunk['text']}",
                "grounded": True,
                "sources": sources
            }

    # 2. Evidence question
    if "evidence" in q_lower or "hash" in q_lower or "integrity" in q_lower:
        ev_chunks = [c for c in relevant_chunks if c["type"] == "EVIDENCE"]
        if ev_chunks:
            items_str = "\n".join([f"• {c['text']}" for c in ev_chunks])
            return {
                "question": question,
                "answer": f"Grounded Evidence Records Found:\n{items_str}",
                "grounded": True,
                "sources": sources
            }

    # 3. Transaction / Money-Flow question
    if "transaction" in q_lower or "amount" in q_lower or "transfer" in q_lower or "mule" in q_lower:
        tx_chunks = [c for c in relevant_chunks if c["type"] == "TRANSACTION"]
        if tx_chunks:
            tx_str = "\n".join([f"• {c['text']}" for c in tx_chunks])
            return {
                "question": question,
                "answer": f"Grounded Transaction Audit Trail:\n{tx_str}",
                "grounded": True,
                "sources": sources
            }

    # 4. General synthesis from top chunks
    answer_body = "\n".join([f"• {c['text']}" for c in relevant_chunks[:3]])
    return {
        "question": question,
        "answer": f"According to verified case records:\n{answer_body}",
        "grounded": True,
        "sources": sources
    }
