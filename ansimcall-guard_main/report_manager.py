import json
from pathlib import Path
from rapidfuzz import fuzz

DB_PATH = Path("data/multilabel_cases.json")

def load_cases():
    return json.loads(DB_PATH.read_text(encoding="utf-8"))

def text_similarity(query: str, case: dict) -> int:
    target = " ".join(case.get("conversation", [])) + " " + " ".join(case.get("keywords", []))
    return fuzz.token_set_ratio(query, target)

def retrieve_similar_cases(query: str, detected_labels=None, top_k: int = 3):
    cases = load_cases()
    detected_labels = set(detected_labels or [])
    scored = []

    for case in cases:
        sim = text_similarity(query, case)
        label_overlap = len(detected_labels.intersection(set(case.get("multi_labels", []))))
        score = sim + label_overlap * 15
        scored.append((score, sim, label_overlap, case))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, sim, overlap, case in scored[:top_k]:
        results.append({
            "case_id": case["case_id"],
            "title": case["title"],
            "similarity": round(min(score, 100), 1),
            "text_similarity": sim,
            "label_overlap": overlap,
            "multi_labels": case["multi_labels"],
            "warning_reason": case["warning_reason"],
            "case_summary": case["case_summary"],
            "recommended_response": case["recommended_response"],
        })
    return results

def export_training_rows():
    cases = load_cases()
    labels = ["기관사칭", "금전요구", "긴급압박", "가족사칭", "개인정보", "앱설치유도", "가입유도"]
    rows = []
    for c in cases:
        text = " ".join(c.get("conversation", []))
        row = {"text": text, "label": int(c.get("is_phishing", 0))}
        for label in labels:
            row[label] = 1 if label in c.get("multi_labels", []) else 0
        rows.append(row)
    return rows
