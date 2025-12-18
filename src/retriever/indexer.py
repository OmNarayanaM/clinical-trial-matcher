class Retriever:
    """
    Lightweight retriever for Streamlit Cloud.
    Uses keyword overlap instead of embeddings.
    """

    def __init__(self, trials):
        self.trials = trials

    def score(self, patient_info, trial):
        score = 0

        # Diagnosis match
        if patient_info.get("diagnosis") and patient_info["diagnosis"] in trial.get("condition", "").lower():
            score += 3

        # Age match
        age = patient_info.get("age")
        min_age = trial.get("min_age")
        max_age = trial.get("max_age")

        if age is not None:
            if (min_age is None or age >= min_age) and (max_age is None or age <= max_age):
                score += 2

        # Sex match
        sex = patient_info.get("sex")
        allowed_sex = trial.get("sex")

        if allowed_sex in (None, "all") or sex == allowed_sex:
            score += 1

        return score

    def rank(self, patient_info):
        scored = []
        for trial in self.trials:
            s = self.score(patient_info, trial)
            scored.append((s, trial))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored