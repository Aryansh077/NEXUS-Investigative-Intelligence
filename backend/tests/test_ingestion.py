import json

from app.database.db import get_conn, init_db
from app.services.ingestion.pipeline import ingest_file


def test_json_ingestion_creates_evidence_and_relationships(tmp_path, monkeypatch):
    database_path = tmp_path / "ingestion.db"
    monkeypatch.setattr("app.database.db.DB_PATH", database_path)
    init_db()
    connection = get_conn()
    connection.execute(
        "INSERT INTO cases(id,title,description,status,created_at) VALUES (?,?,?,?,?)",
        ("CASE-JSON", "JSON test", "", "Active", "2026-09-18T00:00:00Z"),
    )
    connection.commit()
    connection.close()

    source = tmp_path / "records.json"
    source.write_text(
        json.dumps(
            [
                {
                    "caller": "9876500001",
                    "receiver": "9876500002",
                    "timestamp": "2026-05-01T10:00",
                }
            ]
        ),
        encoding="utf-8",
    )
    result = ingest_file("CASE-JSON", str(source), "records.json")
    assert result["type"] == "json"
    assert result["relationships"] == 1

    connection = get_conn()
    assert connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0] == 1
    assert connection.execute("SELECT COUNT(*) FROM relationships").fetchone()[0] == 1
    connection.close()