# Synthetic Test Data

All files in this directory are fictional demonstration data. They do not
represent real people, phone records, financial records, or investigations.

## Case-Isolated Datasets

Each case has completely unique, isolated evidence files, identities, phone numbers, vehicles, bank accounts, and geographic locations with zero overlap:

### 1. `CASE-1023` — Operation Meridian (`data/synthetic/case_1023/`)
- **Focus:** Telecommunications & Hawala money routing in Pune.
- **Key Targets:** Rahul Sharma, Amit Verma, Sameer Khan, Neha Patil, Vikram Joshi, Priya Mehta, Arjun Rao, Karan Shah.
- **Identifiers:** Phones `9876500001-8`, Accounts `ACC-1023-01-8`, Vehicles `MH12AB*`.
- **Files:** `people.csv`, `cdr/cdr_records.csv`, `financial/transactions.csv`, `vehicles.csv`, `locations.csv`, `fir/FIR_CASE_1023.txt`, `surveillance/*.txt`.

### 2. `CASE-1024` — Operation CyberShield (`data/synthetic/case_1024/`)
- **Focus:** Ransomware extortion & cryptocurrency liquidation across Delhi/NCR.
- **Key Targets:** Rohan Kapoor, Ananya Sen, Deepak Malhotra, Tanya Singhania, Kabir Varma, Meera Nair, Aditya Saxena, Ritu Choudhury.
- **Identifiers:** Phones `9811000101-8`, Accounts `ACC-1024-01-8`, Vehicles `DL01XY*`.
- **Files:** `people.csv`, `cdr/cdr_records.csv`, `financial/transactions.csv`, `vehicles.csv`, `locations.csv`, `fir/FIR_CASE_1024.txt`, `surveillance/*.txt`.

### 3. `CASE-1025` — Operation BlueHarbor (`data/synthetic/case_1025/`)
- **Focus:** Maritime freight diversion & shell entity banking in Mumbai.
- **Key Targets:** Tariq Merchant, Zoya Fernandez, Salim Patel, Farhan Qureshi, Bilal Ansari, Natasha D'Souza, Imtiaz Sheikh, Devendra Kulkarni.
- **Identifiers:** Phones `9820000201-8`, Accounts `ACC-1025-01-8`, Vehicles `MH01BK*`.
- **Files:** `people.csv`, `cdr/cdr_records.csv`, `financial/transactions.csv`, `vehicles.csv`, `locations.csv`, `fir/FIR_CASE_1025.txt`, `surveillance/*.txt`.

## Regenerate & Seed Database

From the repository root:

```powershell
python scripts/generate_data.py
python scripts/seed_database.py
```