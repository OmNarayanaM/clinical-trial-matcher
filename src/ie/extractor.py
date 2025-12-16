import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Simple IE: age, sex, pregnancy, creatinine, eGFR, diagnosis keywords
DISEASE_KEYWORDS = [
    "non-small cell lung cancer",
    "metastatic prostate cancer",
    "her2 positive breast cancer",
    "her2 positive breast cancer",  # duplicated intentionally tolerant
    "type 2 diabetes mellitus",
    "type 2 diabetes",
    "hypertension"
]

def extract_entities(text: str) -> dict:
    """
    Returns dictionary with fields: age, sex, pregnant (bool), creatinine (float), egfr (int), diagnosis (str or None)
    """
    out = {"age": None, "sex": None, "pregnant": False, "creatinine": None, "egfr": None, "diagnosis": None}
    if not text:
        return out

    # Age: "62-year-old" or "62 year old"
    m = re.search(r"(\d+)[-\s]*year[-\s]*old", text, re.I)
    if m:
        try:
            out["age"] = int(m.group(1))
        except:
            out["age"] = None

    # Sex: male / female heuristics
    if re.search(r"\bmale\b", text, re.I):
        out["sex"] = "male"
    elif re.search(r"\bfemale\b", text, re.I):
        out["sex"] = "female"

    # Pregnancy
    if re.search(r"\bpregnant\b", text, re.I):
        out["pregnant"] = True

    # Creatinine
    m = re.search(r"creatinine\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if m:
        try:
            out["creatinine"] = float(m.group(1))
        except:
            out["creatinine"] = None

    # eGFR
    m = re.search(r"eGFR\s*[:=]?\s*([0-9]+)", text, re.I)
    if m:
        try:
            out["egfr"] = int(m.group(1))
        except:
            out["egfr"] = None

    # Diagnosis keyword matching (simple)
    lower = text.lower()
    for kw in DISEASE_KEYWORDS:
        if kw.lower() in lower:
            out["diagnosis"] = kw
            break

    # fallback: spaCy entities (useful for showing named entities in UI)
    doc = nlp(text)
    ents = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    out["spacy_ents"] = ents

    return out
