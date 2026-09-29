from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from ..database.connection import get_db
from ..services.rag.assistant import ask_investigation_assistant
from ..security.audit import log_action

router = APIRouter()

class RagQuestionRequest(BaseModel):
    case_id: str
    question: str

@router.post("/ask")
def query_investigation_assistant(payload: RagQuestionRequest, db: Session = Depends(get_db)):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    result = ask_investigation_assistant(db, payload.case_id, payload.question)
    log_action("investigator", "RAG_QUERY", payload.case_id, details_json=payload.question[:80])
    return result
