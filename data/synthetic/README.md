# Synthetic Test Data

All files in this directory are fictional demonstration data. They do not
represent real people, phone records, financial records, or investigations.

## Files

- `people.csv`: stable demo people, aliases, phone numbers, accounts, and vehicles.
- `cdr/cdr_may.csv`: synthetic call records used for graph and anomaly features.
- `financial/transactions.csv`: synthetic account transfers.
- `vehicles.csv`: synthetic vehicle ownership and location records.
- `locations.csv`: synthetic person-location events.
- `surveillance/*.txt`: synthetic narrative reports for NLP extraction.
- `fir/FIR_1023.txt`: synthetic FIR-style narrative.

## Load the complete demo

From the repository root:

```powershell
python scripts/generate_data.py
python scripts/seed_database.py
```

The seed script loads the CDR, financial, vehicle, location, surveillance, and FIR files into
`CASE-1023`. It resets that synthetic case first, so repeated runs are safe.

Individual CSV/JSON/TXT/PDF/DOCX files can also be uploaded from the Evidence
screen or through `POST /api/ingestion/CASE-1023`.