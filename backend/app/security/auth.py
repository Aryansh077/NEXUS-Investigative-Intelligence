import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from .hashing import verify_password, hash_password

SECRET_KEY = os.getenv("NEXUS_JWT_SECRET", "nexus-super-secret-key-sih-2026-investigative")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DEMO_USERS = {
    "admin": {
        "id": "USR-001",
        "username": "admin",
        "password_hash": hash_password("nexus-admin"),
        "role": "admin",
        "full_name": "System Administrator",
    },
    "investigator": {
        "id": "USR-002",
        "username": "investigator",
        "password_hash": hash_password("nexus-demo"),
        "role": "investigator",
        "full_name": "Lead Cyber Investigator",
    },
    "analyst": {
        "id": "USR-003",
        "username": "analyst",
        "password_hash": hash_password("nexus-analyst"),
        "role": "analyst",
        "full_name": "Financial Intelligence Analyst",
    },
    "viewer": {
        "id": "USR-004",
        "username": "viewer",
        "password_hash": hash_password("nexus-viewer"),
        "role": "viewer",
        "full_name": "Case Observer",
    },
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(username: str, password: str) -> Optional[dict]:
    # Check demo users dictionary first for quick zero-setup auth
    user = DEMO_USERS.get(username)
    if user and verify_password(password, user["password_hash"]):
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
        }
    return None

# Backward compatibility hook
def authenticate(username: str, password: str) -> bool:
    return authenticate_user(username, password) is not None
