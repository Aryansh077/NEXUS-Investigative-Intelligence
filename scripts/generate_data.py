from pathlib import Path
import csv, random, json
from datetime import datetime, timedelta

random.seed(42)

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"synthetic"
for d in ["fir","cdr","financial","surveillance","reports"]:
    (DATA/d).mkdir(parents=True,exist_ok=True)

people=[
    ("P001","Rahul Sharma","R. Sharma"),
    ("P002","Amit Verma","A. Verma"),
    ("P003","Sameer Khan","S. Khan"),
    ("P004","Neha Patil","N. Patil"),
    ("P005","Vikram Joshi","V. Joshi"),
    ("P006","Priya Mehta","P. Mehta"),
    ("P007","Arjun Rao","A. Rao"),
    ("P008","Karan Shah","K. Shah"),
]
phones={"P001":"9876500001","P002":"9876500002","P003":"9876500003","P004":"9876500004","P005":"9876500005","P006":"9876500006","P007":"9876500007","P008":"9876500008"}
accounts={f"P00{i}":f"ACC00{i}" for i in range(1,9)}
vehicles={"P001":"MH12AB1234","P002":"MH14CD5678","P003":"MH12EF9012","P004":"MH12GH3456","P005":"MH14JK7890","P006":"MH12LM1234","P007":"MH14NP5678","P008":"MH12QR9012"}
start=datetime(2026,5,1)

with (DATA/"people.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(["person_id","name","alias","phone","account","vehicle"])
    for person_id, name, alias in people:
        w.writerow([person_id, name, alias, phones[person_id], accounts[person_id], vehicles[person_id]])

with (DATA/"cdr"/"cdr_may.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(["call_id","caller","receiver","timestamp","duration","cell_tower"])
    pairs=[("P001","P002"),("P002","P003"),("P003","P005"),("P005","P007"),("P007","P008"),("P001","P004")]
    n=1
    for day in range(30):
        for a,b in pairs:
            if random.random()<0.55:
                t=start+timedelta(days=day,hours=random.randint(8,23),minutes=random.randint(0,59))
                w.writerow([f"C{n:04}",phones[a],phones[b],t.isoformat(timespec="minutes"),random.randint(30,700),f"T{random.randint(1,6):03}"]); n+=1
    # create a burst for P002
    for i in range(35):
        t=start+timedelta(days=20,hours=9+i%12,minutes=i%60)
        w.writerow([f"C{n:04}",phones["P002"],phones["P005"],t.isoformat(timespec="minutes"),random.randint(30,600),"T004"]); n+=1

with (DATA/"financial"/"transactions.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(["transaction_id","sender","receiver","amount","timestamp","location"])
    tx=[("P002","P003",82000),("P003","P005",78000),("P001","P004",12000),("P005","P007",54000)]
    for i,(a,b,amt) in enumerate(tx,1):
        t=start+timedelta(days=10+i)
        w.writerow([f"TX{i:03}",accounts[a],accounts[b],amt,t.isoformat(timespec="minutes"),"Pune"])

with (DATA/"surveillance"/"report_01.txt").open("w",encoding="utf8") as f:
    f.write("On 16 May 2026 Rahul Sharma met Amit Verma near Phoenix Mall. Vehicle MH12AB1234 was observed nearby. On 20 May 2026 Amit Verma met Sameer Khan near Location X.")

with (DATA/"surveillance"/"report_02.txt").open("w",encoding="utf8") as f:
    f.write("On 22 May 2026 Sameer Khan was seen with Vikram Joshi near Location X. The vehicle MH12EF9012 was present.")

with (DATA/"vehicles.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(["vehicle_id","registration","owner","timestamp","location"])
    for i,(p,v) in enumerate(vehicles.items(),1):
        w.writerow([f"V{i:03}",v,phones.get(p,""),(start+timedelta(days=15)).isoformat(timespec="minutes"),"Pune"])

with (DATA/"locations.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f); w.writerow(["event_id","person","location","timestamp"])
    for i,p in enumerate(["P001","P002","P003","P005","P007"],1):
        w.writerow([f"L{i:03}",p,"Pune", (start+timedelta(days=16+i)).isoformat(timespec="minutes")])

with (DATA/"fir"/"FIR_1023.txt").open("w",encoding="utf8") as f:
    f.write("Case FIR-1023. Rahul Sharma and Amit Verma were reported near Phoenix Mall on 16 May 2026. Further records may contain related communication, financial and vehicle events.")

print(f"Synthetic data generated in {DATA}")
