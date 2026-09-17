def test_database_initializes(tmp_path, monkeypatch):
    database_path = tmp_path / "nexus.db"
    monkeypatch.setattr("app.database.db.DB_PATH", database_path)

    from app.database.db import get_conn, init_db

    init_db()
    connection = get_conn()
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    connection.close()
    assert {"cases", "entities", "relationships", "evidence", "anomalies"}.issubset(tables)