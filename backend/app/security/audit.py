from datetime import datetime, timezone
from ..database.db import get_conn, init_db

def log_action(
    username: str,
    action: str,
    case_id: str | None = None,
    target_id: str | None = None,
    details_json: str | None = None
):
    init_db()
    conn = get_conn()
    conn.execute(
        "INSERT INTO audit_logs(username, action, case_id, target_id, details_json, timestamp) VALUES (?,?,?,?,?,?)",
        (username, action, case_id, target_id, details_json or "{}", datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()
