from fastapi import APIRouter
from pydantic import BaseModel
from ..services.copilot.engine import answer_question

router = APIRouter()

class AskRequest(BaseModel):
    case_id: str
    question: str

@router.post("/ask")
def ask(payload: AskRequest):
    return answer_question(payload.case_id, payload.question)
