from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
import json

from ..database.connection import get_db
from ..database.models import Complaint, Case, Transaction, Withdrawal
from ..services.nlp.cyber_extractor import extract_cybercrime_entities
from ..security.audit import log_action

router = APIRouter()

class ComplaintCreateRequest(BaseModel):
    case_id: str
    victim_name: str
    victim_phone: Optional[str] = None
    victim_account: Optional[str] = None
    narrative: str
    city: Optional[str] = "Delhi"
    fraud_amount: Optional[float] = None
    crime_category: Optional[str] = None

@router.get("/")
def list_complaints(
    case_id: Optional[str] = None,
    city: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if case_id:
        query = query.filter_by(case_id=case_id)
    if city:
        query = query.filter_by(city=city)
    if category:
        query = query.filter_by(crime_category=category)
    
    complaints = query.order_by(Complaint.incident_timestamp.desc()).limit(limit).all()
    return [{
        "id": c.id,
        "case_id": c.case_id,
        "victim_name": c.victim_name,
        "victim_phone": c.victim_phone,
        "victim_account": c.victim_account,
        "crime_category": c.crime_category,
        "fraud_amount": c.fraud_amount,
        "incident_timestamp": c.incident_timestamp,
        "narrative": c.narrative,
        "status": c.status,
        "city": c.city,
    } for c in complaints]

@router.get("/{complaint_id}")
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter_by(id=complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    txs = db.query(Transaction).filter_by(complaint_id=c.id).all()
    withdrawals = db.query(Withdrawal).filter_by(complaint_id=c.id).all()
    
    # Run NLP on narrative
    nlp_res = extract_cybercrime_entities(c.narrative or "")

    return {
        "complaint": {
            "id": c.id,
            "case_id": c.case_id,
            "victim_name": c.victim_name,
            "victim_phone": c.victim_phone,
            "victim_account": c.victim_account,
            "crime_category": c.crime_category,
            "fraud_amount": c.fraud_amount,
            "incident_timestamp": c.incident_timestamp,
            "narrative": c.narrative,
            "status": c.status,
            "city": c.city,
        },
        "transactions_count": len(txs),
        "withdrawals_count": len(withdrawals),
        "nlp_extraction": nlp_res
    }

@router.post("/")
def create_complaint(payload: ComplaintCreateRequest, db: Session = Depends(get_db)):
    # Run NLP extraction on the narrative automatically
    nlp_analysis = extract_cybercrime_entities(payload.narrative)
    
    category = payload.crime_category or nlp_analysis.get("primary_crime_category", "Investment Scam")
    amount = payload.fraud_amount
    if amount is None or amount <= 0:
        # Extract from NLP entities
        for ent in nlp_analysis.get("entities", []):
            if ent["type"] == "FRAUD_AMOUNT":
                amount = float(ent["value"])
                break
        if not amount:
            amount = 150000.0  # reasonable fallback

    complaint_count = db.query(Complaint).count()
    cid = f"C{1001 + complaint_count}"
    now_iso = datetime.now(timezone.utc).isoformat()

    new_comp = Complaint(
        id=cid,
        case_id=payload.case_id,
        victim_name=payload.victim_name,
        victim_phone=payload.victim_phone or "9876543210",
        victim_account=payload.victim_account or f"ACC-VIC-{cid}",
        crime_category=category,
        fraud_amount=amount,
        incident_timestamp=now_iso,
        narrative=payload.narrative,
        status="Investigating",
        city=payload.city or "Delhi",
    )
    db.add(new_comp)
    db.commit()
    log_action("investigator", "CREATE_COMPLAINT", payload.case_id, cid)

    return {
        "ok": True,
        "complaint_id": cid,
        "crime_category": category,
        "fraud_amount": amount,
        "nlp_extraction": nlp_analysis
    }
