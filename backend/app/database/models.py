"""
SQLAlchemy Models for NEXUS-PREDICT
Supports PostgreSQL + PostGIS with transparent SQLite fallback.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(32), default="investigator")  # admin, investigator, analyst, viewer
    full_name = Column(String(128))
    email = Column(String(128))
    is_active = Column(Boolean, default=True)
    created_at = Column(String(64), default=utc_now_iso)

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    description = Column(Text)
    category = Column(String(64), default="Cybercrime")
    syndicate_name = Column(String(128))
    city = Column(String(64))
    primary_cluster = Column(String(64))
    status = Column(String(32), default="Active")
    created_at = Column(String(64), default=utc_now_iso)

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    victim_name = Column(String(128), nullable=False)
    victim_phone = Column(String(32))
    victim_account = Column(String(64))
    crime_category = Column(String(64), nullable=False)
    fraud_amount = Column(Float, nullable=False)
    incident_timestamp = Column(String(64), nullable=False)
    narrative = Column(Text)
    status = Column(String(32), default="Investigating")
    city = Column(String(64))
    created_at = Column(String(64), default=utc_now_iso)

class Account(Base):
    __tablename__ = "accounts"

    account_number = Column(String(64), primary_key=True)
    holder_name = Column(String(128), nullable=False)
    bank_name = Column(String(128), nullable=False)
    ifsc = Column(String(32))
    account_type = Column(String(32), default="SAVINGS")
    role = Column(String(32), default="MULE_L1")  # VICTIM, MULE_L1, MULE_L2, BENEFICIARY
    city = Column(String(64))
    upi_id = Column(String(128))
    risk_tier = Column(String(32), default="MEDIUM")
    created_date = Column(String(64))
    status = Column(String(32), default="ACTIVE")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    complaint_id = Column(String(64), ForeignKey("complaints.id"), index=True)
    sender_account = Column(String(64), nullable=False)
    receiver_account = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String(64), nullable=False, index=True)
    channel = Column(String(32), default="IMPS")
    hop_level = Column(Integer, default=1)
    status = Column(String(32), default="COMPLETED")
    velocity_score = Column(Float, default=0.5)

class Location(Base):
    __tablename__ = "locations"

    cluster_id = Column(String(64), primary_key=True)
    cluster_name = Column(String(128), nullable=False)
    district = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    risk_tier = Column(String(32), default="MEDIUM")
    historical_crime_density = Column(Float, default=0.5)

class ATM(Base):
    __tablename__ = "atms"

    atm_id = Column(String(64), primary_key=True)
    cluster_id = Column(String(64), ForeignKey("locations.cluster_id"), nullable=False, index=True)
    bank_name = Column(String(128), nullable=False)
    ifsc = Column(String(32))
    location_name = Column(String(256), nullable=False)
    district = Column(String(64))
    city = Column(String(64))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    daily_cash_limit = Column(Float, default=50000.0)
    is_operational = Column(String(16), default="YES")
    cctv_available = Column(String(16), default="YES")
    historical_fraud_count = Column(Integer, default=0)

class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    complaint_id = Column(String(64), ForeignKey("complaints.id"), index=True)
    account_number = Column(String(64), nullable=False)
    atm_id = Column(String(64), ForeignKey("atms.atm_id"), nullable=False, index=True)
    cluster_id = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(String(64), nullable=False, index=True)
    card_id = Column(String(64))
    latitude = Column(Float)
    longitude = Column(Float)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    complaint_id = Column(String(64), ForeignKey("complaints.id"), nullable=False, index=True)
    cluster_id = Column(String(64), nullable=False)
    atm_id = Column(String(64))
    risk_score = Column(Float, nullable=False)  # 0 to 100
    rank = Column(Integer, nullable=False)
    window_start = Column(String(64), nullable=False)
    window_end = Column(String(64), nullable=False)
    model_version = Column(String(32), default="v1.0.0")
    model_name = Column(String(64), default="LightGBM-CashoutPredictor")
    features_json = Column(Text, default="{}")
    explanation_json = Column(Text, default="{}")
    status = Column(String(32), default="Active")
    created_at = Column(String(64), default=utc_now_iso)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    complaint_id = Column(String(64), ForeignKey("complaints.id"), index=True)
    prediction_id = Column(String(64), ForeignKey("predictions.id"), index=True)
    cluster_id = Column(String(64), nullable=False)
    risk_score = Column(Float, nullable=False)
    severity = Column(String(32), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    message = Column(Text, nullable=False)
    status = Column(String(32), default="New")  # New, Acknowledged, Investigating, Resolved, Dismissed
    assigned_to = Column(String(64))
    created_at = Column(String(64), default=utc_now_iso)
    updated_at = Column(String(64), default=utc_now_iso)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    record_type = Column(String(32), nullable=False)
    title = Column(String(256), nullable=False)
    content = Column(Text)
    timestamp = Column(String(64))
    source_file = Column(String(256))
    hash = Column(String(64))  # SHA-256
    uploader = Column(String(64), default="investigator")
    created_at = Column(String(64), default=utc_now_iso)

class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(String(64), primary_key=True)
    model_name = Column(String(64), nullable=False)
    model_version = Column(String(32), nullable=False)
    metrics_json = Column(Text, default="{}")
    trained_at = Column(String(64), default=utc_now_iso)
    parameters_json = Column(Text, default="{}")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(64), primary_key=True)
    prediction_id = Column(String(64), ForeignKey("predictions.id"), nullable=False)
    complaint_id = Column(String(64), nullable=False)
    predicted_cluster = Column(String(64), nullable=False)
    actual_cluster = Column(String(64))
    distance_error_km = Column(Float)
    time_error_hours = Column(Float)
    top_k_hit = Column(Boolean, default=False)
    reviewed_by = Column(String(64), default="investigator")
    comments = Column(Text)
    created_at = Column(String(64), default=utc_now_iso)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    case_id = Column(String(64))
    target_id = Column(String(64))
    details_json = Column(Text, default="{}")
    timestamp = Column(String(64), default=utc_now_iso)

# Existing entities/relationships support for backward compatibility with graph visualizer
class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    type = Column(String(32), nullable=False)
    name = Column(String(256), nullable=False)
    metadata_json = Column(Text, default="{}")

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    source_id = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=False)
    type = Column(String(32), nullable=False)
    confidence = Column(Float, default=0.5)
    timestamp = Column(String(64))
    source_record = Column(String(256))
    verification = Column(String(32), default="pending")
    metadata_json = Column(Text, default="{}")

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String(64), primary_key=True)
    case_id = Column(String(64), ForeignKey("cases.id"), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False)
    score = Column(Float)
    severity = Column(String(32))
    reason = Column(Text)
    created_at = Column(String(64), default=utc_now_iso)
    verification = Column(String(32), default="pending")
    reviewed_by = Column(String(64))
    reviewed_at = Column(String(64))
    review_note = Column(Text)
