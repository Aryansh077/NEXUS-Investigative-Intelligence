from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database.connection import get_db
from ..database.models import Location, ATM, Prediction, Alert, Case, Complaint

router = APIRouter()

@router.get("/")
def get_heatmap_data(
    city: Optional[str] = None,
    risk_level: Optional[str] = None,
    case_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns spatial clusters, ATM nodes, calibrated risk scores,
    and active predictions for the Leaflet GIS Heatmap.
    """
    loc_query = db.query(Location)
    if city:
        loc_query = loc_query.filter_by(city=city)
    if risk_level:
        loc_query = loc_query.filter_by(risk_tier=risk_level.upper())
    
    locations = loc_query.all()
    atms = db.query(ATM).all()
    predictions = db.query(Prediction).filter_by(status="Active").order_by(Prediction.created_at.desc()).all()
    alerts = db.query(Alert).filter(Alert.status.in_(["New", "Acknowledged", "Investigating"])).all()

    # Map predictions by cluster
    pred_by_cluster = {}
    for p in predictions:
        if p.cluster_id not in pred_by_cluster:
            pred_by_cluster[p.cluster_id] = p

    # Map alerts by cluster
    alert_by_cluster = {}
    for a in alerts:
        alert_by_cluster[a.cluster_id] = a

    # Map ATMs by cluster
    atms_by_cluster = {}
    for a in atms:
        atms_by_cluster.setdefault(a.cluster_id, []).append({
            "atm_id": a.atm_id,
            "bank_name": a.bank_name,
            "location_name": a.location_name,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "is_operational": a.is_operational,
            "cctv_available": a.cctv_available,
            "historical_fraud_count": a.historical_fraud_count
        })

    cluster_features = []
    for loc in locations:
        pred = pred_by_cluster.get(loc.cluster_id)
        alert = alert_by_cluster.get(loc.cluster_id)
        cluster_atms = atms_by_cluster.get(loc.cluster_id, [])

        effective_risk = pred.risk_score if pred else (loc.historical_crime_density * 75.0)

        cluster_features.append({
            "cluster_id": loc.cluster_id,
            "cluster_name": loc.cluster_name,
            "city": loc.city,
            "district": loc.district,
            "latitude": loc.center_lat,
            "longitude": loc.center_lon,
            "risk_tier": loc.risk_tier,
            "crime_density": loc.historical_crime_density,
            "risk_score": round(effective_risk, 1),
            "atm_count": len(cluster_atms),
            "atms": cluster_atms,
            "has_prediction": pred is not None,
            "prediction_window": f"{pred.window_start[-8:-3]}–{pred.window_end[-8:-3]}" if pred else None,
            "has_active_alert": alert is not None,
            "alert_severity": alert.severity if alert else None
        })

    return {
        "total_clusters": len(cluster_features),
        "total_atms": len(atms),
        "clusters": cluster_features
    }
