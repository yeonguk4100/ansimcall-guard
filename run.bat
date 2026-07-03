import json
from datetime import datetime
from pathlib import Path


REPORTED_CASES_PATH = Path("database/reported_cases.json")


def _ensure_report_db():
    REPORTED_CASES_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not REPORTED_CASES_PATH.exists():
        REPORTED_CASES_PATH.write_text("[]", encoding="utf-8")


def load_reported_cases() -> list:
    _ensure_report_db()

    try:
        return json.loads(REPORTED_CASES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def build_report_case(result: dict, conversation_memory: list[str] | None = None) -> dict:
    verification = result.get("llm_verification") or {}
    now = datetime.now()

    conversation_text = "\n".join(conversation_memory or [])
    if not conversation_text:
        conversation_text = result.get("conversation_text", "")

    risk_score = int(float(verification.get("risk_score", result.get("risk_score", 0))))
    labels = verification.get("multi_labels") or result.get("final_labels") or []

    return {
        "case_id": f"user_report_{now.strftime('%Y%m%d_%H%M%S')}",
        "title": verification.get("case_summary") or "사용자 신고 보이스피싱 의심 사례",
        "is_phishing": bool(verification.get("is_phishing", risk_score >= 60)),
        "risk_score": risk_score,
        "multi_labels": labels,
        "keywords": verification.get("keywords", result.get("fuzzy_terms", [])),
        "case_summary": verification.get("case_summary", conversation_text[:200]),
        "warning_reason": verification.get("warning_reason", "사용자가 신고 버튼을 눌러 저장된 사례입니다."),
        "recommended_response": verification.get(
            "recommended_response",
            ["전화로는 송금하지 않겠습니다.", "공식 대표번호로 다시 확인하겠습니다."],
        ),
        "raw_conversation": conversation_text,
        "source": "user_report_llm_verified" if verification.get("llm_verified") else "user_report",
        "llm_verified": bool(verification.get("llm_verified", False)),
        "llm_reason": verification.get("llm_reason", ""),
        "created_at": now.isoformat(timespec="seconds"),
    }


def save_report_case(result: dict, conversation_memory: list[str] | None = None) -> dict:
    _ensure_report_db()

    cases = load_reported_cases()
    new_case = build_report_case(result, conversation_memory)
    cases.append(new_case)

    REPORTED_CASES_PATH.write_text(
        json.dumps(cases, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return new_case


def export_reported_cases_for_training() -> list[dict]:
    rows = []

    for case in load_reported_cases():
        rows.append(
            {
                "text": case.get("raw_conversation") or case.get("case_summary", ""),
                "is_phishing": int(bool(case.get("is_phishing", False))),
                "labels": ",".join(case.get("multi_labels", [])),
                "risk_score": case.get("risk_score", 0),
                "source": case.get("source", "user_report"),
                "case_id": case.get("case_id", ""),
            }
        )

    return rows
