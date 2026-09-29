#!/usr/bin/env python3
"""
NEXUS-PREDICT: Realistic Synthetic Data & Ground Truth Generator
Generates realistic, completely fictional Indian cybercrime complaints, accounts,
multi-hop transaction chains, ATM master data, cash withdrawals, and ground truth
evaluation benchmarks for cash-out prediction.
"""

import json
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

# Deterministic seed for reproducible evaluation
random.seed(42)

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data" / "synthetic"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Masters & Reference Data
# ---------------------------------------------------------------------------

CRIME_CATEGORIES = [
    "Investment Scam",
    "Digital Arrest / Impersonation",
    "Part-Time Job Scam",
    "Phishing / APK Fraud",
    "Card Skimming / OTP Fraud",
    "Loan App Extortion",
]

BANKS = [
    ("State Bank of India", "SBIN0001234"),
    ("HDFC Bank", "HDFC0000456"),
    ("ICICI Bank", "ICIC0000789"),
    ("Punjab National Bank", "PUNB0002345"),
    ("Axis Bank", "UTIB0000678"),
    ("Bank of Baroda", "BARB0003456"),
    ("Canara Bank", "CNRB0004567"),
    ("Kotak Mahindra Bank", "KKBK0005678"),
]

LOCATIONS_MASTER = [
    # Delhi-NCR
    {"cluster_id": "DEL-CP", "name": "Connaught Place Financial Circle", "district": "New Delhi", "city": "Delhi", "lat": 28.6315, "lon": 77.2167, "risk_tier": "HIGH"},
    {"cluster_id": "DEL-NP", "name": "Nehru Place Commercial Corridor", "district": "South Delhi", "city": "Delhi", "lat": 28.5492, "lon": 77.2533, "risk_tier": "CRITICAL"},
    {"cluster_id": "DEL-ROH", "name": "Rohini Sector 7 & 8 Cluster", "district": "North West Delhi", "city": "Delhi", "lat": 28.7041, "lon": 77.1025, "risk_tier": "HIGH"},
    {"cluster_id": "NCR-NOI18", "name": "Noida Sector 18 Commercial Hub", "district": "Gautam Buddha Nagar", "city": "Noida", "lat": 28.5708, "lon": 77.3261, "risk_tier": "CRITICAL"},
    {"cluster_id": "NCR-GURG", "name": "Cyber City & DLF Phase 2", "district": "Gurugram", "city": "Gurugram", "lat": 28.4907, "lon": 77.0898, "risk_tier": "MEDIUM"},

    # Mumbai
    {"cluster_id": "MUM-BKC", "name": "Bandra Kurla Complex Tech Zone", "district": "Mumbai Suburban", "city": "Mumbai", "lat": 19.0657, "lon": 72.8685, "risk_tier": "HIGH"},
    {"cluster_id": "MUM-AND", "name": "Andheri West Lokhandwala Hub", "district": "Mumbai Suburban", "city": "Mumbai", "lat": 19.1363, "lon": 72.8277, "risk_tier": "CRITICAL"},
    {"cluster_id": "MUM-DAD", "name": "Dadar TT Circle Corridor", "district": "Mumbai City", "city": "Mumbai", "lat": 19.0178, "lon": 72.8478, "risk_tier": "MEDIUM"},

    # Pune
    {"cluster_id": "PUN-HINJ", "name": "Hinjewadi Phase 1 & 2 Junction", "district": "Pune", "city": "Pune", "lat": 18.5913, "lon": 73.7389, "risk_tier": "HIGH"},
    {"cluster_id": "PUN-KOTH", "name": "Kothrud Paud Road Corridor", "district": "Pune", "city": "Pune", "lat": 18.5074, "lon": 73.8077, "risk_tier": "MEDIUM"},

    # Bengaluru
    {"cluster_id": "BLR-KOR", "name": "Koramangala 80ft Road Cluster", "district": "Bengaluru Urban", "city": "Bengaluru", "lat": 12.9352, "lon": 77.6245, "risk_tier": "CRITICAL"},
    {"cluster_id": "BLR-IND", "name": "Indiranagar 100ft Road Belt", "district": "Bengaluru Urban", "city": "Bengaluru", "lat": 12.9784, "lon": 77.6408, "risk_tier": "HIGH"},
]

NAMES_FIRST = ["Rajesh", "Sunil", "Pooja", "Vikram", "Anjali", "Ramesh", "Kavita", "Deepak", "Aakash", "Sneha", "Mohit", "Priyanka", "Suresh", "Meena", "Arun", "Divya"]
NAMES_LAST = ["Sharma", "Verma", "Gupta", "Patel", "Mehta", "Singh", "Joshi", "Yadav", "Nair", "Iyer", "Rao", "Choudhury", "Bose", "Kulkarni"]

def generate_name():
    return f"{random.choice(NAMES_FIRST)} {random.choice(NAMES_LAST)}"

def generate_phone():
    return f"9{random.randint(100000000, 999999999)}"

def generate_upi(name, bank_code="okhdfcbank"):
    clean = name.lower().replace(" ", "")[:10] + str(random.randint(10, 99))
    return f"{clean}@{bank_code}"

# ---------------------------------------------------------------------------
# 1. Generate Locations & ATMs
# ---------------------------------------------------------------------------

def generate_atms_and_locations():
    locations_rows = []
    atms_rows = []
    atm_id_counter = 100

    for loc in LOCATIONS_MASTER:
        locations_rows.append({
            "cluster_id": loc["cluster_id"],
            "cluster_name": loc["name"],
            "district": loc["district"],
            "city": loc["city"],
            "center_lat": loc["lat"],
            "center_lon": loc["lon"],
            "risk_tier": loc["risk_tier"],
            "historical_crime_density": round(random.uniform(0.55, 0.98), 3),
        })

        # Generate 4 to 6 ATMs per cluster with small spatial jitter (~100m to 800m)
        num_atms = random.randint(4, 6)
        for i in range(num_atms):
            atm_id_counter += 1
            atm_id = f"ATM-{atm_id_counter}"
            bank_name, ifsc = random.choice(BANKS)
            # 0.001 deg is approx 110 meters
            lat_jitter = random.uniform(-0.006, 0.006)
            lon_jitter = random.uniform(-0.006, 0.006)
            lat = round(loc["lat"] + lat_jitter, 6)
            lon = round(loc["lon"] + lon_jitter, 6)

            atms_rows.append({
                "atm_id": atm_id,
                "cluster_id": loc["cluster_id"],
                "bank_name": bank_name,
                "ifsc": ifsc,
                "location_name": f"{bank_name} ATM, {loc['name']} Branch #{i+1}",
                "district": loc["district"],
                "city": loc["city"],
                "latitude": lat,
                "longitude": lon,
                "daily_cash_limit": random.choice([25000, 40000, 50000, 100000]),
                "is_operational": "YES",
                "cctv_available": random.choice(["YES", "YES", "NO"]),
                "historical_fraud_count": random.randint(3, 38),
            })

    return locations_rows, atms_rows

# ---------------------------------------------------------------------------
# 2. Generate Cases, Complaints, Accounts, Transactions, Withdrawals & Ground Truth
# ---------------------------------------------------------------------------

def generate_cybercrime_data(atms_rows):
    cases_rows = []
    complaints_rows = []
    accounts_rows = []
    transactions_rows = []
    withdrawals_rows = []
    ground_truth = []

    # Map ATMs by cluster
    atms_by_cluster = {}
    for atm in atms_rows:
        atms_by_cluster.setdefault(atm["cluster_id"], []).append(atm)

    account_registry = {}
    tx_counter = 10000
    w_counter = 5000

    def get_or_create_account(acc_num, name, role="MULE_L1", city="Delhi", bank_tuple=None):
        if acc_num not in account_registry:
            if bank_tuple is None:
                bank_tuple = random.choice(BANKS)
            account_registry[acc_num] = {
                "account_number": acc_num,
                "holder_name": name,
                "bank_name": bank_tuple[0],
                "ifsc": bank_tuple[1],
                "account_type": "SAVINGS" if "VICTIM" in role else "CURRENT",
                "role": role,
                "city": city,
                "upi_id": generate_upi(name, bank_tuple[0].split()[0].lower()),
                "risk_tier": "HIGH" if "MULE" in role else "LOW",
                "created_date": (datetime(2026, 1, 10) + timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
                "status": "FROZEN_POST_CRIME" if random.random() < 0.3 else "ACTIVE",
            }
        return account_registry[acc_num]

    # Pre-populate recurring mule accounts (organized cyber rings reuse mule rings)
    syndicates = [
        {"syndicate_id": "SYN-NCR-01", "name": "ViperNet NCR Ring", "primary_cluster": "DEL-NP", "alt_cluster": "NCR-NOI18", "city": "Delhi"},
        {"syndicate_id": "SYN-NCR-02", "name": "Falcon Rohini Group", "primary_cluster": "DEL-ROH", "alt_cluster": "DEL-CP", "city": "Delhi"},
        {"syndicate_id": "SYN-MUM-01", "name": "Apex Mumbai Laundering Ring", "primary_cluster": "MUM-AND", "alt_cluster": "MUM-BKC", "city": "Mumbai"},
        {"syndicate_id": "SYN-PUN-01", "name": "Sahyadri Pune Syndicate", "primary_cluster": "PUN-HINJ", "alt_cluster": "PUN-KOTH", "city": "Pune"},
        {"syndicate_id": "SYN-BLR-01", "name": "Silicon Route Cyber Cell", "primary_cluster": "BLR-KOR", "alt_cluster": "BLR-IND", "city": "Bengaluru"},
    ]

    for syn in syndicates:
        syn["mules_l1"] = []
        syn["mules_l2"] = []
        for i in range(2):
            acc_no = f"ACC-{syn['syndicate_id']}-L1-0{i+1}"
            holder = generate_name()
            get_or_create_account(acc_no, holder, role="MULE_L1", city=syn["city"])
            syn["mules_l1"].append(acc_no)
        for i in range(3):
            acc_no = f"ACC-{syn['syndicate_id']}-L2-0{i+1}"
            holder = generate_name()
            get_or_create_account(acc_no, holder, role="MULE_L2", city=syn["city"])
            syn["mules_l2"].append(acc_no)

    # Generate 15 distinct cases with 50 complaints total
    complaint_counter = 1000
    base_date = datetime(2026, 5, 1, 9, 30)

    for case_idx in range(1, 16):
        case_id = f"CASE-{1020 + case_idx}"
        syn = random.choice(syndicates)
        crime_cat = random.choice(CRIME_CATEGORIES)
        case_start = base_date + timedelta(days=(case_idx * 7) + random.randint(0, 3))

        case_record = {
            "case_id": case_id,
            "title": f"Operation {syn['name'].split()[0]}: {crime_cat} Infiltration",
            "category": crime_cat,
            "syndicate_name": syn["name"],
            "city": syn["city"],
            "primary_cluster": syn["primary_cluster"],
            "status": "Active" if case_idx > 10 else "Closed",
            "created_at": case_start.isoformat(),
        }
        cases_rows.append(case_record)

        # 2 to 4 complaints per case
        num_complaints = random.randint(2, 4)
        for c_idx in range(num_complaints):
            complaint_counter += 1
            complaint_id = f"C{complaint_counter}"
            c_time = case_start + timedelta(days=c_idx * 2, hours=random.randint(1, 8), minutes=random.randint(5, 50))
            fraud_amount = random.choice([120000, 185000, 240000, 350000, 500000, 750000, 1200000])

            victim_name = generate_name()
            victim_acc = f"ACC-VIC-{complaint_id}"
            get_or_create_account(victim_acc, victim_name, role="VICTIM", city=syn["city"])

            victim_phone = generate_phone()

            complaint_text = (
                f"Complaint registered by {victim_name} (Phone: {victim_phone}). Victim reported being defrauded "
                f"of INR {fraud_amount:,} under the pretext of {crime_cat}. "
                f"Victim transferred funds from account {victim_acc} to beneficiary account. "
                f"Suspect demanded urgent liquidation. Immediate interdiction requested."
            )

            complaints_rows.append({
                "complaint_id": complaint_id,
                "case_id": case_id,
                "victim_name": victim_name,
                "victim_phone": victim_phone,
                "victim_account": victim_acc,
                "crime_category": crime_cat,
                "fraud_amount": fraud_amount,
                "incident_timestamp": c_time.isoformat(),
                "narrative": complaint_text,
                "status": "Investigating",
                "city": syn["city"],
            })

            # ---------------------------------------------------------------
            # Multi-Hop Money Flow
            # Hop 1: Victim -> L1 Mule Account
            # ---------------------------------------------------------------
            l1_acc = random.choice(syn["mules_l1"])
            tx_counter += 1
            hop1_time = c_time + timedelta(minutes=random.randint(8, 25))
            transactions_rows.append({
                "transaction_id": f"TX-{tx_counter}",
                "case_id": case_id,
                "complaint_id": complaint_id,
                "sender_account": victim_acc,
                "receiver_account": l1_acc,
                "amount": fraud_amount,
                "timestamp": hop1_time.isoformat(),
                "channel": random.choice(["IMPS", "UPI"]),
                "hop_level": 1,
                "status": "COMPLETED",
                "velocity_score": round(random.uniform(0.85, 0.98), 2),
            })

            # Hop 2: L1 Mule -> 2 L2 Mule Accounts (Smurfing / Layering)
            l2_accs = random.sample(syn["mules_l2"], 2)
            amt_split1 = int(fraud_amount * random.uniform(0.48, 0.55) / 1000) * 1000
            amt_split2 = fraud_amount - amt_split1

            hop2_time1 = hop1_time + timedelta(minutes=random.randint(15, 40))
            tx_counter += 1
            transactions_rows.append({
                "transaction_id": f"TX-{tx_counter}",
                "case_id": case_id,
                "complaint_id": complaint_id,
                "sender_account": l1_acc,
                "receiver_account": l2_accs[0],
                "amount": amt_split1,
                "timestamp": hop2_time1.isoformat(),
                "channel": "IMPS",
                "hop_level": 2,
                "status": "COMPLETED",
                "velocity_score": round(random.uniform(0.75, 0.92), 2),
            })

            hop2_time2 = hop1_time + timedelta(minutes=random.randint(20, 50))
            tx_counter += 1
            transactions_rows.append({
                "transaction_id": f"TX-{tx_counter}",
                "case_id": case_id,
                "complaint_id": complaint_id,
                "sender_account": l1_acc,
                "receiver_account": l2_accs[1],
                "amount": amt_split2,
                "timestamp": hop2_time2.isoformat(),
                "channel": "IMPS",
                "hop_level": 2,
                "status": "COMPLETED",
                "velocity_score": round(random.uniform(0.72, 0.90), 2),
            })

            # ---------------------------------------------------------------
            # Cash Withdrawals (Cash-out at ATM Cluster)
            # ---------------------------------------------------------------
            # 75% probability target cluster is primary_cluster, 25% alt_cluster
            target_cluster = syn["primary_cluster"] if random.random() < 0.75 else syn["alt_cluster"]
            candidate_atms = atms_by_cluster.get(target_cluster, [])
            selected_atm = random.choice(candidate_atms)

            # Cash-out occurs 1.5 to 5 hours after last transaction hop
            cashout_delta_hours = round(random.uniform(1.5, 5.0), 2)
            withdrawal_time = hop2_time2 + timedelta(hours=cashout_delta_hours)

            # Cash is drawn in 2 to 4 ATM swipes
            num_swipes = random.randint(2, 4)
            card_id = f"CARD-MULE-{random.randint(1000, 9999)}"
            per_swipe = min(40000, int((fraud_amount * 0.7) / num_swipes / 500) * 500)

            actual_total_withdrawn = 0
            for s_idx in range(num_swipes):
                w_counter += 1
                w_time = withdrawal_time + timedelta(minutes=s_idx * random.randint(3, 7))
                actual_total_withdrawn += per_swipe
                withdrawals_rows.append({
                    "withdrawal_id": f"W-{w_counter}",
                    "case_id": case_id,
                    "complaint_id": complaint_id,
                    "account_number": l2_accs[0] if s_idx % 2 == 0 else l2_accs[1],
                    "atm_id": selected_atm["atm_id"],
                    "cluster_id": target_cluster,
                    "amount": per_swipe,
                    "timestamp": w_time.isoformat(),
                    "card_id": card_id,
                    "latitude": selected_atm["latitude"],
                    "longitude": selected_atm["longitude"],
                })

            # Ground Truth entry for objective model evaluation
            window_start = (withdrawal_time - timedelta(hours=1)).strftime("%H:00")
            window_end = (withdrawal_time + timedelta(hours=3)).strftime("%H:00")

            ground_truth.append({
                "complaint_id": complaint_id,
                "case_id": case_id,
                "fraud_amount": fraud_amount,
                "incident_timestamp": c_time.isoformat(),
                "actual_cluster_id": target_cluster,
                "actual_atm_id": selected_atm["atm_id"],
                "actual_latitude": selected_atm["latitude"],
                "actual_longitude": selected_atm["longitude"],
                "actual_withdrawal_start": withdrawal_time.isoformat(),
                "actual_amount_withdrawn": actual_total_withdrawn,
                "time_to_cashout_hours": cashout_delta_hours,
                "prediction_window": f"{window_start}–{window_end}",
                "syndicate_id": syn["syndicate_id"],
            })

    return cases_rows, complaints_rows, list(account_registry.values()), transactions_rows, withdrawals_rows, ground_truth

# ---------------------------------------------------------------------------
# File Exporters
# ---------------------------------------------------------------------------

def write_csv(filename, rows):
    if not rows:
        return
    path = DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [+] Wrote {len(rows):4d} records to {path.name}")

def write_json(filename, data):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  [+] Wrote {len(data):4d} evaluation records to {path.name}")

def main():
    print("=" * 60)
    print("NEXUS-PREDICT: Generating Synthetic Cybercrime Dataset...")
    print("=" * 60)

    locs, atms = generate_atms_and_locations()
    cases, complaints, accounts, txs, withdrawals, ground_truth = generate_cybercrime_data(atms)

    write_csv("locations.csv", locs)
    write_csv("atms.csv", atms)
    write_csv("cases.csv", cases)
    write_csv("complaints.csv", complaints)
    write_csv("accounts.csv", accounts)
    write_csv("transactions.csv", txs)
    write_csv("withdrawals.csv", withdrawals)
    write_json("ground_truth.json", ground_truth)

    print("=" * 60)
    print("Dataset generation complete. Ground truth benchmark established.")
    print("=" * 60)

if __name__ == "__main__":
    main()
