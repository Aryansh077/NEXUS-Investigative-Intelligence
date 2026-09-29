from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from ..security.auth import authenticate_user, create_access_token, decode_access_token, DEMO_USERS
from ..security.rbac import ROLES
from ..security.audit import log_action

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    log_action(user["username"], "LOGIN")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "token": token,  # backward compatibility with existing frontend
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "permissions": list(ROLES.get(user["role"], set()))
    }

@router.get("/me")
def get_current_user_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        # Return investigator fallback for demo
        return {
            "username": "investigator",
            "role": "investigator",
            "full_name": "Lead Cyber Investigator",
            "permissions": list(ROLES.get("investigator", set()))
        }
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    uname = payload.get("sub", "investigator")
    user = DEMO_USERS.get(uname, {
        "username": uname,
        "role": payload.get("role", "investigator"),
        "full_name": uname.capitalize()
    })
    return {
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "permissions": list(ROLES.get(user["role"], set()))
    }

@router.post("/logout")
def logout(payload: Optional[LoginRequest] = None):
    uname = payload.username if payload else "user"
    log_action(uname, "LOGOUT")
    return {"ok": True}
