from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
from ..services.ingestion.pipeline import ingest_file

router = APIRouter()

@router.post("/{case_id}")
async def upload(case_id: str, file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    allowed = {".csv", ".json", ".txt", ".pdf", ".docx"}
    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type: {suffix}")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    result = ingest_file(case_id, temp_path, file.filename or "upload")
    return result
