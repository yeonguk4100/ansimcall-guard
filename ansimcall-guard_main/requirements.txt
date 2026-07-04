import json
import os
import re
from datetime import datetime

try:
    from dotenv import load_dotenv
    import google.generativeai as genai
except Exception:
    load_dotenv = None
    genai = None


ALLOWED_LABELS = [
    "기관사칭",
    "금전요구",
    "긴급압박",
    "개인정보요구",
    "앱설치유도",
    "원격제어",
    "대출사기",
    "계좌도용",
    "가족사칭",
    "피싱아님",
]


def _extract_json(text: str) -> dict:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("LLM 응답에서 JSON을 찾지 못했습니다.")

    return json.loads(text[start:end + 1])


def _fallback_verification(result: dict, error: Exception | None = None) -> dict:
    score = int(float(result.get("risk_score", 0)))
    labels = result.get("final_labels") or (["피싱아님"] if score < 60 else ["기관사칭", "금전요구"])

    return {
        "llm_verified": False,
        "is_phishing": score >= 60,
        "risk_score": score,
        "multi_labels": labels,
        "keywords": result.get("fuzzy_terms", []) or [],
        "case_summary": (result.get("conversation_text", "") or "")[:200],
        "warning_reason": "LLM 호출 실패로 기존 분석 결과를 사용했습니다.",
        "recommended_response": [
            "전화로는 송금하지 않겠습니다.",
            "공식 대표번호로 다시 확인하겠습니다.",
        ],
        "llm_reason": f"LLM 호출 실패: {error}" if error else "LLM 호출 실패",
        "verified_at": datetime.now().isoformat(timespec="seconds"),
    }


def verify_with_llm(result: dict, model_name: str = "gemini-2.5-flash") -> dict:
    if genai is None:
        return _fallback_verification(result, RuntimeError("google-generativeai가 설치되지 않았습니다."))

    try:
        if load_dotenv:
            load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(".env에 GEMINI_API_KEY가 없습니다.")

        genai.configure(api_key=api_key)

        prompt = f"""
너는 한국어 보이스피싱 탐지 전문가다.
아래 통화 내용을 보고 보이스피싱 여부를 2차 검증하라.

반드시 JSON만 출력하라. 마크다운, 설명 문장, 코드블록은 출력하지 마라.

사용 가능한 라벨:
{ALLOWED_LABELS}

출력 형식:
{{
  "is_phishing": true,
  "risk_score": 0,
  "multi_labels": ["기관사칭"],
  "keywords": ["서울중앙지검"],
  "case_summary": "개인정보를 제거한 1~2문장 요약",
  "warning_reason": "위험하다고 판단한 이유",
  "recommended_response": ["전화로는 송금하지 않겠습니다."],
  "llm_reason": "판단 근거"
}}

기존 시스템 분석:
- 위험도: {result.get("risk_score", 0)}
- 라벨: {result.get("final_labels", [])}

방금 들은 말:
{result.get("current_text", "")}

누적 통화 내용:
{result.get("conversation_text", "")}
"""

        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        data = _extract_json(response.text)

        score = max(0, min(100, int(float(data.get("risk_score", result.get("risk_score", 0))))))
        labels = [x for x in data.get("multi_labels", []) if x in ALLOWED_LABELS]
        if not labels:
            labels = ["피싱아님"] if score < 60 else ["기관사칭"]

        return {
            "llm_verified": True,
            "is_phishing": bool(data.get("is_phishing", score >= 60)),
            "risk_score": score,
            "multi_labels": labels,
            "keywords": data.get("keywords", [])[:10],
            "case_summary": data.get("case_summary", ""),
            "warning_reason": data.get("warning_reason", ""),
            "recommended_response": data.get("recommended_response", [])[:5],
            "llm_reason": data.get("llm_reason", ""),
            "verified_at": datetime.now().isoformat(timespec="seconds"),
        }

    except Exception as e:
        return _fallback_verification(result, e)


def apply_llm_verification(result: dict, threshold: int = 60) -> dict:
    score = int(float(result.get("risk_score", 0)))

    if score < threshold:
        result["llm_verification"] = None
        return result

    verification = verify_with_llm(result)
    result["llm_verification"] = verification

    result["risk_score"] = verification["risk_score"]
    result["final_labels"] = verification["multi_labels"]

    if verification.get("recommended_response"):
        result["recommendations"] = [
            {
                "say": text,
                "source": "LLM 2차 검증",
                "why": verification.get("warning_reason", "보이스피싱 의심 패턴 감지"),
            }
            for text in verification["recommended_response"]
        ]

    score = result["risk_score"]
    if score >= 80:
        result["risk_level"] = "위험"
    elif score >= 60:
        result["risk_level"] = "경고"
    elif score >= 40:
        result["risk_level"] = "주의"
    else:
        result["risk_level"] = "안전"

    return result
