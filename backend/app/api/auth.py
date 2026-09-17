from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..security.auth import authenticate
from ..security.audit import log_action

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(payload: LoginRequest):
    if not authenticate(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    log_action(payload.username, "login")
    return {"token": "demo-local-token", "username": payload.username, "role": "investigator"}


@router.post("/logout")
def logout(payload: LoginRequest):
    log_action(payload.username, "logout")
    return {"ok": True}
