import re

DISEASE_KEYWORDS = [
    "non-small cell lung cancer",
    "metastatic prostate cancer",
    "her2 positive breast cancer",
    "type 2 diabetes mellitus",
    "type 2 diabetes",
    "hypertension"
]

def extract_entities(text: str) -> dict:
    out = {
        "age": None,
        "sex": None,
        "pregnant": False,
        "creatinine": None,
        "egfr": None,
        "diagnosis": None
    }

    if not text:
        return out

    m = re.search(r"(\d+)[-\s]*year[-\s]*old", text, re.I)
    if m:
        out["age"] = int(m.group(1))

    if re.search(r"\bmale\b", text, re.I):
        out["sex"] = "male"
    elif re.search(r"\bfemale\b", text, re.I):
        out["sex"] = "female"

    if re.search(r"\bpregnant\b", text, re.I):
        out["pregnant"] = True

    m = re.search(r"creatinine\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if m:
        out["creatinine"] = float(m.group(1))

    m = re.search(r"egfr\s*[:=]?\s*([0-9]+)", text, re.I)
    if m:
        out["egfr"] = int(m.group(1))

    lower = text.lower()
    for kw in DISEASE_KEYWORDS:
        if kw in lower:
            out["diagnosis"] = kw
            break

    return out
