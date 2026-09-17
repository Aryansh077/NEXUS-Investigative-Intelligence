from fastapi import APIRouter
from ..services.anomaly.detector import detect_case_anomalies

router = APIRouter()

@router.get("/{case_id}")
def anomalies(case_id: str):
    return detect_case_anomalies(case_id)
