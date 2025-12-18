import re
import spacy

# --- SAFE spaCy loading (works locally + Streamlit Cloud) ---
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # fallback so app never crashes
    nlp = spacy.blank("en")


# Simple IE: age, sex, pregnancy, creatinine, eGFR, diagnosis keywords
DISEASE_KEYWORDS = [
    "non-small cell lung cancer",
    "metastatic prostate cancer",
    "her2 positive breast cancer",
    "type 2 diabetes mellitus",
    "type 2 diabetes",
    "hypertension"
]


def extract_entities(text: str) -> dict:
    """
    Returns dictionary with fields:
    age, sex, pregnant (bool), creatinine (float),
    egfr (int), diagnosis (str or None), spacy_ents (list)
    """
    out = {
        "age": None,
        "sex": None,
        "pregnant": False,
        "creatinine": None,
        "egfr": None,
        "diagnosis": None,
        "spacy_ents": []
    }

    if not text:
        return out

    # Age: "62-year-old" or "62 year old"
    m = re.search(r"(\d+)[-\s]*year[-\s]*old", text, re.I)
    if m:
        out["age"] = int(m.group(1))

    # Sex
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
        out["creatinine"] = float(m.group(1))

    # eGFR
    m = re.search(r"egfr\s*[:=]?\s*([0-9]+)", text, re.I)
    if m:
        out["egfr"] = int(m.group(1))

    # Diagnosis keyword matching
    lower = text.lower()
    for kw in DISEASE_KEYWORDS:
        if kw in lower:
            out["diagnosis"] = kw
            break

    # spaCy entities (optional, for UI display)
    try:
        doc = nlp(text)
        out["spacy_ents"] = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    except Exception:
        out["spacy_ents"] = []

    return out