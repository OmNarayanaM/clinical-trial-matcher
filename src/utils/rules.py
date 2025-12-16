import re

def parse_numeric_check(text):
    """
    Parse expressions like 'creatinine > 2.0' or 'age >= 18' into (field, op, value).
    Returns None if not parseable.
    """
    m = re.search(r"(creatinine|age|egfr)\s*([<>]=?)\s*([0-9]+(?:\.[0-9]+)?)", text, re.I)
    if not m:
        return None
    field = m.group(1).lower()
    op = m.group(2)
    val = float(m.group(3))
    return (field, op, val)

def check_numeric_condition(patient, field, op, val):
    pv = None
    if field == "creatinine":
        pv = patient.get("creatinine")
    elif field == "age":
        pv = patient.get("age")
    elif field == "egfr":
        pv = patient.get("egfr")
    if pv is None:
        return None  # unknown
    if op == ">":
        return pv > val
    if op == "<":
        return pv < val
    if op == ">=":
        return pv >= val
    if op == "<=":
        return pv <= val
    return None

def evaluate_trial_rules(patient: dict, trial: dict):
    """
    Returns:
      inclusions_satisfied: list of inclusion texts that appear satisfied (very simple)
      exclusions_triggered: list of exclusion texts that appear triggered
    """
    inclusions = trial.get("inclusion", [])
    exclusions = trial.get("exclusion", [])
    satisfied = []
    triggered = []

    # simple inclusion matching: check diagnosis keyword
    pdx = (patient.get("diagnosis") or "").lower()
    for inc in inclusions:
        inc_low = inc.lower()
        if pdx and pdx in inc_low:
            satisfied.append(inc)

    # check exclusions: pregnancy and numeric thresholds
    for ex in exclusions:
        if "pregnant" in ex.lower() and patient.get("pregnant"):
            triggered.append(ex)
            continue
        # numeric parse
        parsed = parse_numeric_check(ex)
        if parsed:
            field, op, val = parsed
            res = check_numeric_condition(patient, field, op, val)
            if res is True:
                triggered.append(ex)
            # if None or False: don't add
    return satisfied, triggered
