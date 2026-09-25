import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"backend"))
from app.database.db import init_db, get_conn
from app.services.ingestion.pipeline import ingest_file
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
init_db()
conn=get_conn()
case_id = "CASE-1023"
# The demo seed is a reproducible reset for the synthetic case.
for table in ("anomalies", "relationships", "evidence", "entities"):
    conn.execute(f"DELETE FROM {table} WHERE case_id=?", (case_id,))
conn.execute("INSERT OR REPLACE INTO cases(id,title,description,status,created_at) VALUES (?,?,?,?,?)",
             (case_id,"Operation Meridian","Synthetic multi-source investigation demonstrating communication, finance, vehicle and location relationships.","Active",datetime.now(timezone.utc).isoformat()))
conn.commit(); conn.close()

data=ROOT/"data"/"synthetic"
files=(
    [data/"people.csv"]
    + list((data/"cdr").glob("*.csv"))
    + list((data/"financial").glob("*.csv"))
    + [data/"vehicles.csv", data/"locations.csv"]
    + list((data/"surveillance").glob("*.txt"))
    + list((data/"fir").glob("*.txt"))
)
for p in files:
    try:
        print("Ingesting",p.name, ingest_file(case_id,str(p),p.name))
    except Exception as e:
        print("ERROR",p,e)

# Seed people explicitly so names appear even if CSV schemas differ.
people=[
("P001","Rahul Sharma"),("P002","Amit Verma"),("P003","Sameer Khan"),("P004","Neha Patil"),
("P005","Vikram Joshi"),("P006","Priya Mehta"),("P007","Arjun Rao"),("P008","Karan Shah")]
conn=get_conn()
for eid,name in people:
    conn.execute("INSERT OR IGNORE INTO entities(id,case_id,type,name,metadata_json) VALUES (?,?,?,?,?)",(eid,case_id,"PERSON",name,"{}"))
conn.commit(); conn.close()
print(f"Database seeded. Case: {case_id}")
