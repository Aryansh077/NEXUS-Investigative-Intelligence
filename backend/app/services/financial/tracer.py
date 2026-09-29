"""
Financial & Money-Flow Tracer Engine
Traces multi-hop transaction laundering chains, calculates transaction velocities,
identifies mule accounts, and produces Cytoscape-formatted graph topology.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ...database.models import Transaction, Account, Withdrawal, ATM, Complaint, Case

def trace_money_flow_for_complaint(db: Session, complaint_id: str) -> Dict[str, Any]:
    """
    Traces the entire money-flow graph starting from the victim's complaint:
    Victim Account -> Layer 1 Mule -> Layer 2 Mules -> Cash Withdrawal at ATM.
    """
    complaint = db.query(Complaint).filter_by(id=complaint_id).first()
    if not complaint:
        return {"error": f"Complaint {complaint_id} not found", "nodes": [], "edges": []}

    # Fetch all transactions linked to this complaint or case
    txs = db.query(Transaction).filter_by(complaint_id=complaint_id).order_by(Transaction.hop_level, Transaction.timestamp).all()
    if not txs:
        # Fallback to case transactions if complaint-level linkage is sparse
        txs = db.query(Transaction).filter_by(case_id=complaint.case_id).order_by(Transaction.hop_level, Transaction.timestamp).all()

    # Fetch withdrawals
    withdrawals = db.query(Withdrawal).filter_by(complaint_id=complaint_id).all()
    if not withdrawals:
        withdrawals = db.query(Withdrawal).filter_by(case_id=complaint.case_id).all()

    nodes_dict: Dict[str, Dict[str, Any]] = {}
    edges_list: List[Dict[str, Any]] = []

    # Helper to add node
    def add_node(node_id: str, label: str, node_type: str, metadata: Dict[str, Any]):
        if node_id not in nodes_dict:
            nodes_dict[node_id] = {
                "data": {
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    **metadata
                }
            }

    # 1. Add Victim Node
    victim_acc_id = complaint.victim_account or f"VIC-{complaint.id}"
    add_node(
        victim_acc_id,
        f"Victim: {complaint.victim_name}\n₹{complaint.fraud_amount:,.0f}",
        "VICTIM",
        {"role": "Victim", "amount": complaint.fraud_amount, "city": complaint.city, "risk": "LOW"}
    )

    # 2. Add Transaction Hops & Accounts
    total_flow_amount = 0.0
    for tx in txs:
        total_flow_amount += tx.amount
        sender_acc = db.query(Account).filter_by(account_number=tx.sender_account).first()
        receiver_acc = db.query(Account).filter_by(account_number=tx.receiver_account).first()

        sender_label = f"{tx.sender_account}\n({sender_acc.holder_name if sender_acc else 'Unknown'})"
        receiver_label = f"{tx.receiver_account}\n({receiver_acc.holder_name if receiver_acc else 'Mule L' + str(tx.hop_level)})"

        sender_type = sender_acc.role if sender_acc else ("VICTIM" if tx.hop_level == 1 else "MULE")
        receiver_type = receiver_acc.role if receiver_acc else f"MULE_L{tx.hop_level}"

        add_node(
            tx.sender_account,
            sender_label,
            sender_type,
            {"bank": sender_acc.bank_name if sender_acc else "Bank", "risk": sender_acc.risk_tier if sender_acc else "HIGH"}
        )
        add_node(
            tx.receiver_account,
            receiver_label,
            receiver_type,
            {"bank": receiver_acc.bank_name if receiver_acc else "Bank", "risk": receiver_acc.risk_tier if receiver_acc else "HIGH"}
        )

        edge_id = f"edge-{tx.id}"
        edges_list.append({
            "data": {
                "id": edge_id,
                "source": tx.sender_account,
                "target": tx.receiver_account,
                "amount": tx.amount,
                "label": f"₹{tx.amount:,.0f} ({tx.channel})",
                "timestamp": tx.timestamp,
                "velocity": tx.velocity_score,
                "hop": tx.hop_level,
            }
        })

    # 3. Add Withdrawal Nodes & ATM Clusters
    total_withdrawn = 0.0
    for w in withdrawals:
        total_withdrawn += w.amount
        atm = db.query(ATM).filter_by(atm_id=w.atm_id).first()
        atm_node_id = f"ATM-{w.atm_id}"
        atm_label = f"{w.atm_id}\n{atm.location_name if atm else w.cluster_id}"

        add_node(
            atm_node_id,
            atm_label,
            "ATM_CASHOUT",
            {
                "atm_id": w.atm_id,
                "cluster_id": w.cluster_id,
                "lat": w.latitude,
                "lon": w.longitude,
                "risk": "CRITICAL"
            }
        )

        edge_id = f"edge-w-{w.id}"
        edges_list.append({
            "data": {
                "id": edge_id,
                "source": w.account_number,
                "target": atm_node_id,
                "amount": w.amount,
                "label": f"Cash Out: ₹{w.amount:,.0f}",
                "timestamp": w.timestamp,
                "type": "CASH_WITHDRAWAL"
            }
        })

    # 4. Summary Metrics
    disbursed_ratio = round((total_withdrawn / complaint.fraud_amount) * 100, 1) if complaint.fraud_amount else 0.0

    return {
        "complaint_id": complaint.id,
        "case_id": complaint.case_id,
        "crime_category": complaint.crime_category,
        "victim_reported_loss": complaint.fraud_amount,
        "total_transferred": total_flow_amount,
        "total_withdrawn_cash": total_withdrawn,
        "cash_out_liquidation_percentage": disbursed_ratio,
        "hop_count": len(txs),
        "nodes": list(nodes_dict.values()),
        "edges": edges_list
    }
