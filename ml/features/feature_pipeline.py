"""
Spatio-Temporal & Financial Feature Engineering Pipeline
Constructs feature matrices for (Complaint, Candidate Location) pairs
combining temporal, financial, geospatial, and historical graph signals.
"""

from typing import Dict, List, Any, Tuple
import math
from datetime import datetime
import pandas as pd
import numpy as np

FEATURE_NAMES = [
    "fraud_amount_log",
    "incident_hour",
    "is_weekend",
    "hours_since_incident",
    "tx_velocity_max",
    "tx_hop_count",
    "cluster_crime_density",
    "cluster_atm_count",
    "distance_to_complaint_km",
    "historical_cluster_recurrence",
    "syndicate_cluster_affinity",
    "time_window_risk_alignment"
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two coordinates in kilometers."""
    R = 6371.0  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def extract_pair_features(
    complaint: Dict[str, Any],
    candidate_cluster: Dict[str, Any],
    case_context: Dict[str, Any],
    atms_in_cluster: int,
    historical_cluster_counts: Dict[str, int]
) -> Dict[str, float]:
    """
    Computes numerical feature dictionary for one (complaint, candidate_cluster) observation.
    """
    # 1. Temporal signals
    c_time = datetime.fromisoformat(complaint["incident_timestamp"])
    incident_hour = c_time.hour
    is_weekend = 1.0 if c_time.weekday() >= 5 else 0.0
    hours_since_incident = min(24.0, max(0.5, complaint.get("hours_elapsed", 2.0)))

    # 2. Financial signals
    fraud_amt = float(complaint.get("fraud_amount", 50000.0))
    fraud_amount_log = math.log10(max(100.0, fraud_amt))
    tx_velocity_max = float(complaint.get("max_velocity", 0.85))
    tx_hop_count = float(complaint.get("hop_count", 2.0))

    # 3. Geospatial signals
    c_lat = float(complaint.get("latitude") or candidate_cluster.get("center_lat", 28.6))
    c_lon = float(complaint.get("longitude") or candidate_cluster.get("center_lon", 77.2))
    t_lat = float(candidate_cluster.get("center_lat", 28.6))
    t_lon = float(candidate_cluster.get("center_lon", 77.2))
    dist_km = haversine_distance(c_lat, c_lon, t_lat, t_lon)

    crime_density = float(candidate_cluster.get("historical_crime_density", 0.5))
    atm_count = float(atms_in_cluster)

    # 4. Historical recurrence & syndicate affinity
    total_cluster_hist = sum(historical_cluster_counts.values()) or 1
    recurrence = historical_cluster_counts.get(candidate_cluster["cluster_id"], 0) / total_cluster_hist

    primary_cluster = case_context.get("primary_cluster")
    syndicate_affinity = 1.0 if candidate_cluster["cluster_id"] == primary_cluster else 0.1

    # Night/evening cash-out alignment (between 18:00 and 02:00)
    expected_cashout_hour = (incident_hour + int(hours_since_incident)) % 24
    is_night_window = 1.0 if (expected_cashout_hour >= 18 or expected_cashout_hour <= 2) else 0.35

    return {
        "fraud_amount_log": round(fraud_amount_log, 3),
        "incident_hour": float(incident_hour),
        "is_weekend": is_weekend,
        "hours_since_incident": round(hours_since_incident, 2),
        "tx_velocity_max": round(tx_velocity_max, 2),
        "tx_hop_count": tx_hop_count,
        "cluster_crime_density": round(crime_density, 3),
        "cluster_atm_count": atm_count,
        "distance_to_complaint_km": round(dist_km, 2),
        "historical_cluster_recurrence": round(recurrence, 4),
        "syndicate_cluster_affinity": syndicate_affinity,
        "time_window_risk_alignment": is_night_window
    }
