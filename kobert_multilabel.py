from .stt_correction import normalize_stt_text
from .db_analyzer import detect_labels_by_db, get_db_based_recommendations
from .case_db import retrieve_similar_cases
from .kobert_multilabel import KoBERTMultiLabelPredictor, LABELS

def combine_labels(*label_lists):
    result = []
    for label in LABELS:
        for labels in label_lists:
            if label in labels and label not in result:
                result.append(label)
    return result

def level_from_score(score):
    if score >= 75:
        return "위험"
    if score >= 50:
        return "경고"
    if score >= 25:
        return "주의"
    return "정상"

def calculate_memory_score(current_score, memory_score, db_similarity):
    return round(current_score * 0.4 + memory_score * 0.4 + db_similarity * 0.2, 1)

def analyze_call_text(current_text: str, conversation_text: str = None, predictor=None):
    current_corrected = normalize_stt_text(current_text or "")
    current_analysis_text = current_corrected["analysis_text"]

    if conversation_text is None:
        conversation_text = current_text or ""

    memory_corrected = normalize_stt_text(conversation_text or "")
    memory_analysis_text = memory_corrected["analysis_text"]

    if predictor is None:
        predictor = KoBERTMultiLabelPredictor()

    current_db = detect_labels_by_db(current_analysis_text)
    memory_db = detect_labels_by_db(memory_analysis_text)
    kobert_result = predictor.predict(memory_analysis_text)

    final_labels = combine_labels(
        current_db["detected_labels"],
        memory_db["detected_labels"],
        kobert_result.get("predicted_labels", []),
    )

    similar_cases = retrieve_similar_cases(memory_analysis_text, final_labels, top_k=3)
    best_similarity = similar_cases[0]["similarity"] if similar_cases else 0

    final_score = calculate_memory_score(
        current_score=current_db["db_score"],
        memory_score=memory_db["db_score"],
        db_similarity=best_similarity,
    )

    if kobert_result["available"]:
        extra_labels = [l for l in kobert_result.get("predicted_labels", []) if l not in memory_db["detected_labels"]]
        final_score = min(100, final_score + len(extra_labels) * 5)

    recommendations = get_db_based_recommendations(similar_cases, final_labels, max_items=3)

    return {
        "current_text": current_corrected["cleaned"],
        "conversation_text": memory_corrected["cleaned"],
        "current_original_text": current_corrected["original"],
        "analysis_text": memory_analysis_text,
        "fuzzy_terms": sorted(set(current_corrected["fuzzy_terms"] + memory_corrected["fuzzy_terms"])),
        "risk_level": level_from_score(final_score),
        "risk_score": final_score,
        "current_score": current_db["db_score"],
        "memory_score": memory_db["db_score"],
        "db_similarity_score": best_similarity,
        "final_labels": final_labels,
        "current_db": current_db,
        "memory_db": memory_db,
        "kobert": kobert_result,
        "similar_cases": similar_cases,
        "recommendations": recommendations,
    }
