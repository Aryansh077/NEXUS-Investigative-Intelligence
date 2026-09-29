from pathlib import Path
import csv, random, json
from datetime import datetime, timedelta

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"

# Definition of 3 distinct, isolated synthetic cases
CASES_DATA = [
    {
        "case_id": "CASE-1023",
        "title": "Operation Meridian",
        "desc": "Telecom and financial coordination ring tracking fund transfers, CDR calls, and vehicle logistics in Pune.",
        "folder": "case_1023",
        "city": "Pune",
        "start_date": datetime(2026, 5, 1),
        "people": [
            ("P001", "Rahul Sharma", "R. Sharma", "Primary Coordinator"),
            ("P002", "Amit Verma", "A. Verma", "Field Operative"),
            ("P003", "Sameer Khan", "S. Khan", "Logistics Handler"),
            ("P004", "Neha Patil", "N. Patil", "Financial Custodian"),
            ("P005", "Vikram Joshi", "V. Joshi", "Technical Associate"),
            ("P006", "Priya Mehta", "P. Mehta", "Transport Operator"),
            ("P007", "Arjun Rao", "A. Rao", "Regional Contact"),
            ("P008", "Karan Shah", "K. Shah", "Asset Holder"),
        ],
        "phone_prefix": "987650000",
        "acc_prefix": "ACC-1023-0",
        "veh_prefix": "MH12AB",
        "locations": ["Phoenix Mall, Pune", "Sector 62 Warehouse", "Kothrud Terminal", "Hinjewadi IT Park", "Swargate Depot"],
        "call_pairs": [("P001", "P002"), ("P002", "P003"), ("P003", "P005"), ("P005", "P007"), ("P007", "P008"), ("P001", "P004")],
        "tx_pairs": [("P002", "P003", 82000), ("P003", "P005", 78000), ("P001", "P004", 12000), ("P005", "P007", 54000)],
        "fir_text": "Case FIR-1023. Rahul Sharma and Amit Verma were observed coordinating asset movements near Phoenix Mall, Pune. Intercepted logs indicate suspicious telecommunication surges and high-velocity fund routing.",
        "surv_texts": [
            "On 16 May 2026 Rahul Sharma met Amit Verma near Phoenix Mall, Pune. Transport vehicle MH12AB1201 was observed on site.",
            "On 20 May 2026 Amit Verma met Sameer Khan at Sector 62 Warehouse. Telecom handset 9876500002 registered active cell tower pings nearby."
        ]
    },
    {
        "case_id": "CASE-1024",
        "title": "Operation CyberShield",
        "desc": "Ransomware extortion and illicit cryptocurrency liquidation syndicate operating across Delhi/NCR.",
        "folder": "case_1024",
        "city": "Delhi",
        "start_date": datetime(2026, 6, 1),
        "people": [
            ("P101", "Rohan Kapoor", "R. Kapoor", "Cryptocurrency Broker"),
            ("P102", "Ananya Sen", "A. Sen", "Malware Developer"),
            ("P103", "Deepak Malhotra", "D. Malhotra", "Mule Account Networker"),
            ("P104", "Tanya Singhania", "T. Singhania", "Shell Corp Director"),
            ("P105", "Kabir Varma", "K. Varma", "Server Infrastructure Host"),
            ("P106", "Meera Nair", "M. Nair", "Escrow Intermediary"),
            ("P107", "Aditya Saxena", "A. Saxena", "VPN Gateway Operator"),
            ("P108", "Ritu Choudhury", "R. Choudhury", "Digital Assets Cashier"),
        ],
        "phone_prefix": "981100010",
        "acc_prefix": "ACC-1024-0",
        "veh_prefix": "DL01XY",
        "locations": ["Cyber Hub Gurugram", "Nehru Place Tech Hub", "Noida Sector 18", "Connaught Place Financial Tower", "Aerocity Tech Center"],
        "call_pairs": [("P101", "P102"), ("P102", "P105"), ("P103", "P104"), ("P105", "P107"), ("P106", "P108"), ("P101", "P103")],
        "tx_pairs": [("P101", "P102", 145000), ("P102", "P105", 92000), ("P103", "P104", 310000), ("P106", "P108", 87000)],
        "fir_text": "Case FIR-1024. Cyber Crime Division initiated inquiry into unauthorized corporate infrastructure intrusion. Target Rohan Kapoor and developer Ananya Sen were identified as key nodes in rapid wallet transfers.",
        "surv_texts": [
            "On 08 June 2026 Rohan Kapoor was logged entering Cyber Hub Gurugram driving luxury sedan DL01XY9901.",
            "On 14 June 2026 Ananya Sen and Kabir Varma were surveilled at Nehru Place Tech Hub exchanging encrypted hard drive storage."
        ]
    },
    {
        "case_id": "CASE-1025",
        "title": "Operation BlueHarbor",
        "desc": "Maritime freight diversion and cross-border shell account settlement syndicate in Mumbai.",
        "folder": "case_1025",
        "city": "Mumbai",
        "start_date": datetime(2026, 7, 1),
        "people": [
            ("P201", "Tariq Merchant", "T. Merchant", "Customs Clearance Agent"),
            ("P202", "Zoya Fernandez", "Z. Fernandez", "Freight Forwarder"),
            ("P203", "Salim Patel", "S. Patel", "Dock Logistics Coordinator"),
            ("P204", "Farhan Qureshi", "F. Qureshi", "Offshore Wire Facilitator"),
            ("P205", "Bilal Ansari", "B. Ansari", "Container Depot Manager"),
            ("P206", "Natasha D'Souza", "N. D'Souza", "Import Compliance Auditor"),
            ("P207", "Imtiaz Sheikh", "I. Sheikh", "Harbor Security Contact"),
            ("P208", "Devendra Kulkarni", "D. Kulkarni", "Shell Entity Signatory"),
        ],
        "phone_prefix": "982000020",
        "acc_prefix": "ACC-1025-0",
        "veh_prefix": "MH01BK",
        "locations": ["Nhava Sheva Port, Mumbai", "Ballard Estate Customs House", "Nariman Point Commercial Hub", "Bandra Kurla Complex", "Wadala Freight Terminal"],
        "call_pairs": [("P201", "P202"), ("P202", "P203"), ("P203", "P205"), ("P204", "P208"), ("P205", "P207"), ("P201", "P204")],
        "tx_pairs": [("P201", "P204", 450000), ("P204", "P208", 380000), ("P202", "P203", 115000), ("P205", "P207", 65000)],
        "fir_text": "Case FIR-1025. Directorate of Revenue Intelligence registered formal investigation regarding misdeclared maritime cargo manifest at Nhava Sheva. Customs Agent Tariq Merchant and freight coordinator Zoya Fernandez flagged.",
        "surv_texts": [
            "On 05 July 2026 Tariq Merchant met Farhan Qureshi at Ballard Estate Customs House. Commercial vehicle MH01BK7701 was recorded entering terminal.",
            "On 11 July 2026 Salim Patel was observed inspecting container storage yard at Wadala Freight Terminal alongside Bilal Ansari."
        ]
    }
]

# Generate synthetic evidence datasets for each case
for c in CASES_DATA:
    case_folder = DATA / c["folder"]
    (case_folder / "cdr").mkdir(parents=True, exist_ok=True)
    (case_folder / "financial").mkdir(parents=True, exist_ok=True)
    (case_folder / "surveillance").mkdir(parents=True, exist_ok=True)
    (case_folder / "fir").mkdir(parents=True, exist_ok=True)

    people_map = {}
    phones_map = {}
    accs_map = {}
    vehs_map = {}

    for idx, (pid, name, alias, role) in enumerate(c["people"], 1):
        phone = f"{c['phone_prefix']}{idx}"
        acc = f"{c['acc_prefix']}{idx}"
        veh = f"{c['veh_prefix']}{1000 + idx*111}"
        people_map[pid] = (name, alias, role)
        phones_map[pid] = phone
        accs_map[pid] = acc
        vehs_map[pid] = veh

    # 1. People Registry CSV
    with (case_folder / "people.csv").open("w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["person_id", "name", "alias", "phone", "account", "vehicle", "role"])
        for pid, name, alias, role in c["people"]:
            w.writerow([pid, name, alias, phones_map[pid], accs_map[pid], vehs_map[pid], role])

    # 2. CDR Call Records CSV
    with (case_folder / "cdr" / "cdr_records.csv").open("w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["call_id", "caller", "receiver", "timestamp", "duration", "cell_tower"])
        n = 1
        for day in range(25):
            for a, b in c["call_pairs"]:
                if random.random() < 0.6:
                    t = c["start_date"] + timedelta(days=day, hours=random.randint(8, 23), minutes=random.randint(0, 59))
                    w.writerow([f"C{n:04}", phones_map[a], phones_map[b], t.isoformat(timespec="minutes"), random.randint(30, 600), f"T{random.randint(1, 6):03}"])
                    n += 1
        # Add high-frequency communication burst
        for i in range(20):
            t = c["start_date"] + timedelta(days=15, hours=10 + i % 10, minutes=i % 60)
            w.writerow([f"C{n:04}", phones_map[c["call_pairs"][0][0]], phones_map[c["call_pairs"][0][1]], t.isoformat(timespec="minutes"), random.randint(45, 500), "T002"])
            n += 1

    # 3. Financial Transactions CSV
    with (case_folder / "financial" / "transactions.csv").open("w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["transaction_id", "sender", "receiver", "amount", "timestamp", "location"])
        for i, (a, b, amt) in enumerate(c["tx_pairs"], 1):
            t = c["start_date"] + timedelta(days=5 + i * 2)
            w.writerow([f"TX{i:03}", accs_map[a], accs_map[b], amt, t.isoformat(timespec="minutes"), c["city"]])

    # 4. Vehicles CSV
    with (case_folder / "vehicles.csv").open("w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["vehicle_id", "registration", "owner", "timestamp", "location"])
        for i, (pid, v) in enumerate(vehs_map.items(), 1):
            w.writerow([f"V{i:03}", v, phones_map[pid], (c["start_date"] + timedelta(days=10)).isoformat(timespec="minutes"), c["city"]])

    # 5. Locations CSV
    with (case_folder / "locations.csv").open("w", newline="", encoding="utf8") as f:
        w = csv.writer(f)
        w.writerow(["event_id", "person", "location", "timestamp"])
        for i, (pid, name, _, _) in enumerate(c["people"][:5], 1):
            loc = c["locations"][i % len(c["locations"])]
            w.writerow([f"L{i:03}", pid, loc, (c["start_date"] + timedelta(days=12 + i)).isoformat(timespec="minutes")])

    # 6. FIR Document
    with (case_folder / "fir" / f"FIR_{c['case_id'].replace('-', '_')}.txt").open("w", encoding="utf8") as f:
        f.write(c["fir_text"])

    # 7. Surveillance Reports
    for s_idx, s_text in enumerate(c["surv_texts"], 1):
        with (case_folder / "surveillance" / f"surveillance_report_0{s_idx}.txt").open("w", encoding="utf8") as f:
            f.write(s_text)

print(f"Successfully generated distinct synthetic case datasets for {len(CASES_DATA)} cases in {DATA}")
