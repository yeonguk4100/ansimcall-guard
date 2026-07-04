from .case_db import load_cases

LABEL_WEIGHTS = {
    "기관사칭": 22,
    "금전요구": 25,
    "긴급압박": 13,
    "가족사칭": 20,
    "개인정보": 25,
    "앱설치유도": 20,
    "가입유도": 15,
}

def detect_labels_by_db(text: str):
    cases = load_cases()
    label_scores = {k: 0 for k in LABEL_WEIGHTS}
    matched_keywords = {k: [] for k in LABEL_WEIGHTS}

    for case in cases:
        for kw in case.get("keywords", []):
            if kw and kw in text:
                for label in case.get("multi_labels", []):
                    if label in label_scores:
                        label_scores[label] += 1
                        if kw not in matched_keywords[label]:
                            matched_keywords[label].append(kw)

    detected = [label for label, count in label_scores.items() if count > 0]
    score = min(100, sum(LABEL_WEIGHTS[l] for l in detected))

    if score >= 75:
        level = "위험"
    elif score >= 50:
        level = "경고"
    elif score >= 25:
        level = "주의"
    else:
        level = "정상"

    return {
        "detected_labels": detected,
        "matched_keywords": {k: v for k, v in matched_keywords.items() if v},
        "db_score": score,
        "risk_level": level,
    }

def get_db_based_recommendations(similar_cases, detected_labels, max_items=3):
    responses = []
    seen = set()

    for case in similar_cases:
        for resp in case.get("recommended_response", []):
            if resp not in seen:
                seen.add(resp)
                responses.append({
                    "source": f"유사 사례 {case['case_id']}",
                    "say": resp,
                    "why": case["warning_reason"],
                })
            if len(responses) >= max_items:
                return responses

    fallback = [
        "전화로는 송금하지 않겠습니다. 가족에게 먼저 확인하겠습니다.",
        "제가 직접 공식 대표번호로 다시 전화하겠습니다.",
        "인증번호와 비밀번호는 전화로 말하지 않겠습니다.",
    ]
    for resp in fallback:
        if resp not in seen:
            responses.append({"source": "기본 대응", "say": resp, "why": "의심 통화에서는 즉시 행동하지 않는 것이 안전합니다."})
        if len(responses) >= max_items:
            break
    return responses
