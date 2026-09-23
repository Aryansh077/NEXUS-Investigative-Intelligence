from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import os
from ..services.ingestion.pipeline import ingest_file
from ..database.db import get_conn

router = APIRouter()

@router.post("/{case_id}")
async def upload(case_id: str, file: UploadFile = File(...)):
    conn = get_conn()
    exists = conn.execute("SELECT 1 FROM cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    if not exists:
        raise HTTPException(404, "Case not found")
    suffix = Path(file.filename or "").suffix.lower()
    allowed = {".csv", ".json", ".txt", ".pdf", ".docx"}
    if suffix not in allowed:
        raise HTTPException(400, f"Unsupported file type: {suffix}")
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(413, "File exceeds the 25 MB prototype limit")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        temp_path = tmp.name
    try:
        return ingest_file(case_id, temp_path, file.filename or "upload")
    finally:
        os.unlink(temp_path)
