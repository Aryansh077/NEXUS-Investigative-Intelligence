import re

PATTERNS = {
    "PERSON": r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b",
    "VEHICLE": r"\b[A-Z]{2}\d{2}[A-Z]{1,3}\d{3,4}\b",
    "PHONE": r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
    "MONEY": r"(?:₹|Rs\.?\s*)[\d,]+",
    "DATE": r"\b(?:\d{1,2}[-/]){2}\d{2,4}\b|\b\d{1,2}\s+(?:May|June|July|August|September|October|November|December|January|February|March|April)\b"
}

def extract_from_text(text: str):
    entities = []
    seen = set()
    for typ, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text):
            val = m.group(0).strip()
            if (typ,val) not in seen:
                seen.add((typ,val))
                entities.append({"type": typ, "text": val})

    relationships = []
    # Lightweight prototype relation extraction for common sentences.
    for m in re.finditer(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:called|contacted)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text):
        relationships.append({"source":m.group(1),"target":m.group(2),"type":"CALLED"})
    for m in re.finditer(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:met|was seen with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text):
        relationships.append({"source":m.group(1),"target":m.group(2),"type":"SEEN_WITH"})
    return {"entities": entities, "relationships": relationships}
