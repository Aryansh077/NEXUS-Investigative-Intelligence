from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..services.financial.tracer import trace_money_flow_for_complaint
from ..services.financial.upi_tracer import trace_upi_fraud

router = APIRouter()

@router.get("/flow/{complaint_id}")
def get_money_flow(complaint_id: str, db: Session = Depends(get_db)):
    result = trace_money_flow_for_complaint(db, complaint_id)
    if "error" in result and result.get("nodes") == []:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/upi-trace/{query}")
def get_upi_trace(query: str, db: Session = Depends(get_db)):
    """
    Traces UPI fraud by complaint_id, UPI ID (VPA), or account number.
    Returns the VPA hop chain, linked accounts, cash-out points,
    and a generated NPCI Section 91 CrPC fast-freeze intimation docket.
    """
    try:
        return trace_upi_fraud(db, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UPI trace failed: {str(e)}")

@router.get("/upi-trace")
def get_upi_trace_query(q: str = Query("C1001"), db: Session = Depends(get_db)):
    return trace_upi_fraud(db, q)
