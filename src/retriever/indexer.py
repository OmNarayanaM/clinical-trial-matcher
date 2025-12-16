import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
import os

# Try import faiss; if not present we'll fall back to numpy search
try:
    import faiss
    _has_faiss = True
except Exception:
    _has_faiss = False

MODEL_NAME = "all-MiniLM-L6-v2"

class Retriever:
    def __init__(self, trials_path="data/trials_small.jsonl", model_name=MODEL_NAME):
        self.trials_path = trials_path
        self.model = SentenceTransformer(model_name)
        self.trials = []
        self.corpus_texts = []
        self.corpus_ids = []
        self.embeddings = None
        self.index = None
        self._load_trials()
        self._build_index()

    def _load_trials(self):
        with open(self.trials_path, "r", encoding="utf-8") as f:
            for line in f:
                t = json.loads(line)
                self.trials.append(t)
                text = self._flatten_trial_text(t)
                self.corpus_texts.append(text)
                self.corpus_ids.append(t["trial_id"])

    def _flatten_trial_text(self, trial):
        inc = " ; ".join(trial.get("inclusion", []))
        exc = " ; ".join(trial.get("exclusion", []))
        return f"{trial.get('title','')} INCLUSION: {inc} EXCLUSION: {exc}"

    def _build_index(self):
        # compute embeddings (numpy)
        self.embeddings = self.model.encode(self.corpus_texts, convert_to_numpy=True, show_progress_bar=True)
        # normalize embeddings for cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms==0] = 1.0
        self.embeddings = self.embeddings / norms

        if _has_faiss:
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine similarity
            self.index.add(self.embeddings.astype('float32'))
        else:
            self.index = None  # will use numpy fallback

    def search(self, query_text, top_k=5):
        q_emb = self.model.encode([query_text], convert_to_numpy=True)[0]
        q_emb = q_emb / (np.linalg.norm(q_emb)+1e-12)
        if _has_faiss and self.index is not None:
            D, I = self.index.search(q_emb.reshape(1,-1).astype('float32'), top_k)
            results = []
            for score, idx in zip(D[0], I[0]):
                results.append({"score": float(score), "corpus_id": int(idx), "trial": self.trials[int(idx)]})
            return results
        else:
            # numpy fallback: dot product with all embeddings
            scores = np.dot(self.embeddings, q_emb)
            idxs = np.argsort(-scores)[:top_k]
            return [{"score": float(scores[i]), "corpus_id": int(i), "trial": self.trials[int(i)]} for i in idxs]

    def get_trial_texts(self):
        return self.corpus_texts

    def get_trials_meta(self):
        return self.trials
