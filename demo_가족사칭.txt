import re
from rapidfuzz import fuzz

CORRECTION_MAP = {
    "안전 계좌": "안전계좌",
    "안전 개좌": "안전계좌",
    "안전계자": "안전계좌",
    "금융 감독원": "금융감독원",
    "금감 원": "금감원",
    "중앙 지검": "중앙지검",
    "사건 번호": "사건번호",
    "인증 번호": "인증번호",
    "비밀 번호": "비밀번호",
    "계좌 번호": "계좌번호",
    "앱 설치": "앱설치",
    "원격 제어": "원격제어",
    "무료 체험": "무료체험",
    "자동 결제": "자동결제",
    "폰 고장": "폰고장",
    "휴대폰 고장": "휴대폰고장",
}

CANONICAL_TERMS = [
    "검찰", "검찰청", "경찰", "경찰청", "금감원", "금융감독원", "중앙지검",
    "수사관", "사건번호", "범죄연루", "명의계좌", "안전계좌", "보관계좌",
    "송금", "이체", "입금", "인증번호", "비밀번호", "주민번호", "계좌번호",
    "보안카드", "OTP", "지금바로", "즉시", "긴급", "불이익", "전화끊지마세요",
    "엄마나야", "아빠나야", "폰고장", "휴대폰고장", "합의금", "앱설치",
    "원격제어", "링크", "클릭", "회원가입", "무료체험", "자동결제", "정기구독",
]

def compact_text(text: str) -> str:
    return re.sub(r"[^가-힣A-Za-z0-9]", "", text)

def normalize_stt_text(text: str):
    cleaned = re.sub(r"\s+", " ", text.strip())
    for wrong, correct in CORRECTION_MAP.items():
        cleaned = cleaned.replace(wrong, correct)

    compact = compact_text(cleaned)
    fuzzy_terms = []
    for term in CANONICAL_TERMS:
        cterm = compact_text(term)
        if cterm in compact:
            fuzzy_terms.append(term)
        elif len(cterm) >= 3 and fuzz.partial_ratio(cterm, compact) >= 84:
            fuzzy_terms.append(term)

    fuzzy_terms = sorted(set(fuzzy_terms))
    analysis_text = cleaned + (" " + " ".join(fuzzy_terms) if fuzzy_terms else "")

    return {
        "original": text,
        "cleaned": cleaned,
        "analysis_text": analysis_text,
        "fuzzy_terms": fuzzy_terms,
    }
