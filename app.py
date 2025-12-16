import streamlit as st
import json
from src.ie.extractor import extract_entities
from src.retriever.indexer import Retriever
from src.utils.rules import evaluate_trial_rules
import random

st.set_page_config(page_title="Clinical Trial Eligibility Matcher", layout="wide")
st.title("Clinical Trial Eligibility Matcher — Demo")

@st.cache_data
def load_retriever():
    return Retriever()

retriever = load_retriever()

left, right = st.columns([2,1])

with left:
    st.subheader("Patient input")
    txt = st.text_area("Paste patient summary here", height=220)
    if st.button("Use a random sample"):
        # load a random sample from data
        with open("data/patients_small.jsonl","r",encoding="utf-8") as f:
            lines = f.readlines()
        sample = json.loads(random.choice(lines))
        txt = sample["summary"]
        st.session_state["sample_text"] = txt
        st.experimental_rerun()

    if "sample_text" in st.session_state and not txt:
        txt = st.session_state["sample_text"]

    if st.button("Match Trials"):
        if not txt or not txt.strip():
            st.error("Please paste patient summary (or use a random sample).")
        else:
            patient = extract_entities(txt)
            st.subheader("Extracted Medical Info")
            st.json(patient)

            st.subheader("Top matching trials (retrieval)")
            results = retriever.search(txt, top_k=6)
            for r in results:
                t = r["trial"]
                score = r["score"]
                st.markdown(f"### {t['title']}  —  score {score:.3f}")
                st.write(f"Trial id: {t['trial_id']} — Phase/notes: {t.get('title')}")
                satisfied, triggered = evaluate_trial_rules(patient, t)
                if triggered:
                    st.markdown("**Potential Exclusions (rule-based):**")
                    for ex in triggered:
                        st.write("- " + ex)
                else:
                    st.write("No immediate rule-based exclusions detected.")
                if satisfied:
                    st.markdown("**Inclusions matched (rough):**")
                    for inc in satisfied:
                        st.write("- " + inc)
                # expand trial details
                with st.expander("View full trial details"):
                    st.write("Inclusion criteria:", t.get("inclusion",[]))
                    st.write("Exclusion criteria:", t.get("exclusion",[]))
                    # show evidence: naive substring search
                    for inc in t.get("inclusion",[]):
                        if inc.lower() in txt.lower():
                            st.markdown(f"- Evidence for inclusion: '{inc}' appears in patient text.")
                    for ex in t.get("exclusion",[]):
                        if ex.lower() in txt.lower():
                            st.markdown(f"- Evidence for exclusion: '{ex}' appears in patient text.")

with right:
    st.subheader("Controls / Info")
    st.markdown("- Generate toy patients with `generate_toy_data.py`")
    st.markdown("- Uses sentence-transformers for embeddings")
    if _ := st.button("Regenerate toy data (overwrite)"):
        import subprocess, sys
        subprocess.run([sys.executable, "generate_toy_data.py"])
        st.success("Toy data regenerated. Restart the app (or click any action).")
