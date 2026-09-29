from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..database.models import User
from ..security.rbac import ROLES

router = APIRouter()

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{
        "id": u.id,
        "username": u.username,
        "role": u.role,
        "full_name": u.full_name,
        "email": u.email,
        "is_active": u.is_active,
        "permissions": list(ROLES.get(u.role, set())),
        "created_at": u.created_at
    } for u in users]
