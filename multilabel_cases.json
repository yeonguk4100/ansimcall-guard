from pathlib import Path
from datetime import datetime
import tempfile
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from modules.audio_recorder import list_input_devices, record_audio
from modules.stt_engine import transcribe_audio
from modules.analysis_engine import analyze_call_text
from modules.kobert_multilabel import KoBERTMultiLabelPredictor
from modules.case_db import export_training_rows, load_cases
from modules.llm_verifier import apply_llm_verification
from modules.report_manager import save_report_case, load_reported_cases

load_dotenv()

# 페이지 기본 설정
st.set_page_config(page_title="안심콜 가드 Memory MVP", page_icon="📞", layout="wide")

@st.cache_resource
def load_predictor():
    return KoBERTMultiLabelPredictor("models/kobert_multilabel")

predictor = load_predictor()

# 상태 관리 초기화
if "history" not in st.session_state:
    st.session_state.history = []

if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

if "page" not in st.session_state:
    st.session_state.page = "main"

if "current_result" not in st.session_state:
    st.session_state.current_result = None

if "last_saved_report_id" not in st.session_state:
    st.session_state.last_saved_report_id = None

# ==========================================
# 🚨 신고 화면 렌더링 함수 (절대 건드리지 않음)
# ==========================================
def render_report_page():
    score = st.session_state.current_result['risk_score'] if st.session_state.current_result else 0
    
    st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(to bottom, #C42525, #821414) !important;
    }}
    .block-container {{
        max-width: 640px !important;
        padding-top: 40px !important;
        padding-bottom: 40px !important;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    .center-header {{
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }}
    .report-ring {{
        width: 130px;
        height: 130px;
        margin-bottom: 20px;
        background-color: rgba(255, 255, 255, 0.12); 
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }}
    .ring-pulse {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.5);
        animation: pulse-animation 1.6s ease-out infinite;
    }}
    @keyframes pulse-animation {{
        0% {{ transform: scale(0.85); opacity: 0.9; }}
        100% {{ transform: scale(1.4); opacity: 0; }}
    }}
    .phone-number {{
        font-size: 42px !important;
        font-weight: 800 !important;
        letter-spacing: 2px;
        color: #FFFFFF;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 1; 
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%; 
    }}
    .connecting-text {{
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 26px;
        line-height: 1.4;
    }}
    .green-box {{
        background-color: #EBFBEE;
        border: 2px solid #C3EACB;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        text-align: left;
    }}
    .green-title {{
        color: #268038;
        font-size: 16px;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 12px;
    }}
    .green-content {{
        font-size: 17px;
        color: #1A4D24;
        font-weight: 500;
        line-height: 1.75;
    }}
    .slogan-text {{
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 26px;
        text-align: center;
        line-height: 1.5;
    }}
    div[data-testid="stExpander"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        border: none;
        margin-bottom: 24px;
    }}
    div[data-testid="stExpander"] * {{
        color: #222222 !important;
    }}
    div[data-testid="stButton"] {{
        display: flex;
        justify-content: center;
    }}
    div[data-testid="stButton"] > button {{
        padding: 14px 40px !important;
        border-radius: 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background-color: transparent !important;
        border: 2px solid rgba(255, 255, 255, 0.55) !important;
        color: #FFFFFF !important;
        height: auto !important;
        width: auto !important; 
        box-shadow: none;
        transition: background-color 0.3s ease;
    }}
    div[data-testid="stButton"] > button:hover {{
        background-color: rgba(255, 255, 255, 0.12) !important;
    }}
    /* 신고 저장 성공 박스: 박스는 유지하되 글씨를 흰색으로 */
    [data-testid="stAlert"], [data-testid="stAlertContainer"] {{
        background-color: #2F9E44 !important;
        border: none !important;
        border-radius: 12px !important;
    }}
    [data-testid="stAlert"] *, [data-testid="stAlertContainer"] * {{
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }}
    </style>
    
    <div class="center-header">
        <div class="report-ring">
            <div class="ring-pulse"></div>
            <div class="phone-number">&nbsp;1394</div>
        </div>
        <div class="connecting-text">보이스피싱 통합신고센터<br>연결 중…</div>
    </div>
    
    <div class="green-box">
        <div class="green-title">📋 상황 안내 (이렇게 말씀하세요)</div>
        <div class="green-content">
            "방금 서울중앙지검 수사관이라는 사람에게서 전화를 받았습니다. 제 계좌가 범죄에 연루됐다며 안전계좌로 송금하라고 했고, 앱을 설치해 원격으로 조작하려 했습니다. 보이스피싱으로 의심되어 신고합니다."
        </div>
    </div>
    
    <div class="slogan-text">
        당신의 신고 1분이<br>더 나은 세상을 만듭니다
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.current_result and st.session_state.current_result.get("llm_verification"):
        verification = st.session_state.current_result["llm_verification"]
        with st.expander("🤖 LLM 2차 검증 결과"):
            st.write(f"**검증 상태:** {'완료' if verification.get('llm_verified') else '대체 결과 사용'}")
            st.write(f"**보정 위험도:** {verification.get('risk_score')}점")
            st.write(f"**라벨:** {', '.join(verification.get('multi_labels', []))}")
            st.write(f"**요약:** {verification.get('case_summary', '')}")
            st.write(f"**판단 근거:** {verification.get('llm_reason', '')}")

    if st.session_state.last_saved_report_id:
        st.success(f"신고 사례가 DB에 저장되었습니다: {st.session_state.last_saved_report_id}")

    with st.expander("🔍 자세히 보기 (전체 통화 내용 확인)"):
        st.markdown("### 📝 기록된 통화 스크립트")
        full_text = "\n".join(st.session_state.conversation_memory) if st.session_state.conversation_memory else "기록된 통화 내용이 없습니다."
        st.text_area("분석된 통화 내용", full_text, height=120, disabled=True, label_visibility="collapsed")
        
        if st.session_state.current_result and st.session_state.current_result.get("final_labels"):
            st.markdown("### ⚠️ 감지된 위험 요소")
            for label in st.session_state.current_result["final_labels"]:
                st.error(f"- {label}")

    if st.button("돌아가기"):
        st.session_state.page = "main"
        st.session_state.history = []
        st.session_state.conversation_memory = []
        st.session_state.current_result = None
        st.session_state.last_saved_report_id = None
        st.rerun()

# ==========================================
# 📊 메인(감지) 화면 전용 결과 출력 함수
# ==========================================
def render_result(result):
    level = result["risk_level"]
    score = result['risk_score']

    if level == "위험": 
        color_hex = "#E03131"
        card_bg = "#FFF0F0"
        card_border = "#FAD4D4"
        level_emoji = "🚨"
    elif level == "경고": 
        color_hex = "#FF9800"
        card_bg = "#FFFFFF"
        card_border = "#ECECF1"
        level_emoji = "⚠️"
    elif level == "주의": 
        color_hex = "#FFEB3B"
        card_bg = "#FFFFFF"
        card_border = "#ECECF1"
        level_emoji = "🔔"
    else: 
        color_hex = "#2F9E44"
        card_bg = "#EBFBEE"
        card_border = "#C3EACB"
        level_emoji = "✅"

    # 결과 영역 상단 헤더 (안심콜 가드 + 위험 배지)
    st.markdown(
        f'<div class="app-header">'
        f'<div class="app-header-left">'
        f'<div class="app-logo">📞</div>'
        f'<div><div class="app-name">안심콜 가드</div>'
        f'<div class="app-sub">AI 보이스피싱 탐지 시스템</div></div>'
        f'</div>'
        f'<div class="app-badge" style="background:{card_bg}; color:{color_hex}; border:1px solid {card_border};">{level_emoji} {level}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([3.8, 6.2], gap="large")

    with c1:
        labels_html = "".join([f'<span class="type-pill">{lbl}</span>' for lbl in result.get("final_labels", [])])
        if not labels_html:
            labels_html = '<span class="type-pill" style="background:#F3F3F7; color:#6B6B7B;">탐지 없음</span>'
        llm_html = ""
        if result.get("llm_verification"):
            verified = result["llm_verification"].get("llm_verified")
            llm_html = (
                "<div style='font-size: 14px; color:#6B6B7B; margin-top: 12px;'>"
                f"🤖 LLM 2차 검증: <b>{'완료' if verified else '대체 결과 사용'}</b>"
                "</div>"
            )
        st.markdown(f"""<div class="score-card" style="background-color: {card_bg}; border-color: {card_border};">
<div class="score-level" style="color: {color_hex};">{level_emoji} {level}</div>
<div class="score-value" style="color: {color_hex};">{score}<span style="font-size: 24px; color: {color_hex};">점</span></div>
<div class="gauge-bg">
<div class="gauge-fill" style="width: {score}%; background-color: {color_hex};"></div>
</div>
<div style="font-size: 14px; color: #6B6B7B; margin-bottom: 20px; line-height: 1.6;">
현재 구간 점수: <b>{result['current_score']}</b>점<br>
누적 대화 점수: <b>{result['memory_score']}</b>점<br>
유사 사례 점수: <b>{result['db_similarity_score']}</b>점
</div>
<div>
<div style="font-size: 15px; font-weight: 700; color: #1A1A2E; margin-bottom: 8px;">감지된 유형</div>
{labels_html}
</div>
{llm_html}
</div>""", unsafe_allow_html=True)

        risk_score = result.get('risk_score', 0)
        btn_key = f"action_btn_{len(st.session_state.history)}_{risk_score}"
        
        if risk_score >= 60:
            if st.button("🚨 전화 끊고 신고하기", type="primary", use_container_width=True, key=f"report_call_btn_{len(st.session_state.history)}"):
                saved_case = save_report_case(result, st.session_state.conversation_memory)
                st.session_state.last_saved_report_id = saved_case["case_id"]
                st.session_state.page = "report"
                st.rerun()
        else:
            if st.button("👂 더 들어보기", use_container_width=True, key=btn_key):
                st.toast("통화 내용을 계속 주시하며 분석합니다.", icon="👀")

    with c2:
        # 1. 유도 멘트 — 제목 + 추천 멘트를 하나의 초록 박스에
        if result["recommendations"]:
            recs = []
            for rec in result["recommendations"]:
                recs.append(
                    f'<div class="guide-text">"{rec["say"]}"</div>'
                    f'<div class="guide-source">출처: {rec["source"]} ㆍ {rec["why"]}</div>'
                )
            recs_html = '<div class="guide-divider"></div>'.join(recs)
        else:
            recs_html = '<div style="color:#6B6B7B;">추천 대응 멘트가 없습니다.</div>'

        st.markdown(
            f'<div class="guide-box">'
            f'<div class="guide-title">💬 지금 이렇게 말해보세요</div>'
            f'{recs_html}'
            f'</div>',
            unsafe_allow_html=True
        )

        # 2. 유사 사례 Top 3 — 하나의 박스로 묶음
        with st.container(border=True):
            st.markdown("<div class='section-title' style='margin-top: 0;'>유사 사례 Top 3</div>", unsafe_allow_html=True)
            for case in result["similar_cases"]:
                title = f"🔴 [유사도 {case['similarity']}%] {case['title']}"
                with st.expander(title):
                    st.markdown(f"**사례 요약:** {case['case_summary']}")
                    st.markdown(f"**위험 이유:** {case['warning_reason']}")
                    st.markdown(f"**대응 문구:** {', '.join(case['recommended_response'])}")

        # 3. 자세히 보기 (기본 접힘, 박스 밖) — 누적 대화 기록 + 방금 들은 말
        with st.expander("🔍 자세히 보기 (통화 기록 · 방금 들은 말)", expanded=False):
            st.markdown("**🧾 누적 대화 기록**")
            if st.session_state.conversation_memory:
                for i, chunk in enumerate(st.session_state.conversation_memory, 1):
                    st.write(f"{i}. {chunk}")
            else:
                st.write("아직 누적된 대화가 없습니다.")

            st.markdown("**👂 방금 들은 말**")
            detail_text = result["current_text"] if result["current_text"] else "(인식된 문장이 없습니다.)"
            st.markdown(f"<div style='font-size: 16px; color: #1A1A2E; margin-bottom: 12px; line-height: 1.5;'>{detail_text}</div>", unsafe_allow_html=True)
            if result["fuzzy_terms"]:
                tags_html = "".join([f'<span class="word-tag">{t}</span>' for t in result["fuzzy_terms"]])
                st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

            if result.get("llm_verification"):
                verification = result["llm_verification"]
                st.markdown("---")
                st.markdown("**🤖 LLM 2차 검증 결과**")
                st.write(f"요약: {verification.get('case_summary', '')}")
                st.write(f"판단 근거: {verification.get('llm_reason', '')}")

# ==========================================
# 🔀 화면 라우팅 (메인 vs 신고화면)
# ==========================================
if st.session_state.page == "main":
    
    # 메인 페이지 전용 배경을 아주 밝고 깨끗하게 덮어씌움 (신고 화면 빨간 배경 무효화)
    st.markdown("""
    <style>
    /* 메인 화면 밝은 앱 배경 강제 적용 */
    .stApp, [data-testid="stAppViewContainer"] {
        background: #F3F3F7 !important; /* 깔끔한 라이트 그레이/화이트 톤 */
    }
    
    [data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
    }
    
    .block-container {
        padding: 56px 34px 60px !important;
        max-width: 1400px !important;
    }

    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
    }
    .app-header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .app-logo {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        background-color: #F0EEFC;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
    }
    .app-name {
        font-size: 22px;
        font-weight: 800;
        color: #1A1A2E;
        line-height: 1.2;
    }
    .app-sub {
        font-size: 14px;
        color: #6B6B7B;
        margin-top: 2px;
    }
    .app-badge {
        padding: 7px 16px;
        border-radius: 20px;
        font-size: 15px;
        font-weight: 700;
    }

    /* 대기(idle) 화면 */
    .app-name-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-badge-idle {
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 700;
        background-color: #EEF2FE;
        color: #2F5BEA;
    }
    .shield-box {
        max-width: 460px;
        background-color: #EEF2FE;
        border-radius: 14px;
        padding: 16px 20px;
    }
    .shield-title {
        font-size: 15px;
        font-weight: 700;
        color: #2347C4;
        margin-bottom: 4px;
    }
    .shield-sub {
        font-size: 13px;
        color: #6B6B7B;
        line-height: 1.5;
    }
    .hero {
        text-align: center;
        padding: 18px 0 8px;
    }
    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #1A1A2E;
        margin-bottom: 10px;
    }
    .hero-sub {
        font-size: 16px;
        color: #6B6B7B;
        margin-bottom: 22px;
    }
    .hero-mic {
        width: 96px;
        height: 96px;
        margin: 0 auto;
        border-radius: 50%;
        background-color: #EEF2FE;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 44px;
    }
    .hero-hint {
        text-align: center;
        font-size: 14px;
        color: #6B6B7B;
        margin-top: 12px;
    }
    .steps-row {
        display: flex;
        gap: 16px;
        margin: 20px 0;
    }
    .step-card {
        flex: 1;
        background-color: #FFFFFF;
        border: 1px solid #ECECF1;
        border-radius: 16px;
        padding: 22px 20px;
    }
    .step-num {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #2F5BEA;
        color: #FFFFFF;
        font-size: 14px;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
    }
    .step-icon {
        font-size: 26px;
        margin-bottom: 10px;
    }
    .step-title {
        font-size: 17px;
        font-weight: 700;
        color: #1A1A2E;
        margin-bottom: 6px;
    }
    .step-desc {
        font-size: 14px;
        color: #6B6B7B;
        line-height: 1.55;
    }
    .tip-box {
        background-color: #EEF2FE;
        border-radius: 14px;
        padding: 18px 22px;
    }
    .tip-title {
        font-size: 16px;
        font-weight: 700;
        color: #2347C4;
        margin-bottom: 6px;
    }
    .tip-sub {
        font-size: 14px;
        color: #6B6B7B;
        line-height: 1.55;
    }

    .score-card {
        padding: 28px 24px;
        border-radius: 16px;
        border: 1px solid #ECECF1;
        background-color: #FFFFFF;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .score-level {
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .score-value {
        font-size: 60px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 15px;
        color: #1A1A2E;
    }
    .gauge-bg {
        width: 100%;
        height: 10px;
        background-color: #F3F3F7;
        border-radius: 5px;
        margin-bottom: 20px;
        overflow: hidden;
    }
    .gauge-fill {
        height: 10px;
        border-radius: 5px;
        transition: width 0.5s ease;
    }

    div[data-testid="stButton"] > button {
        height: 60px !important;
        border-radius: 14px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }

    /* primary 버튼 기본 = 초록 (시작/분석) */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #2F9E44 !important;
        border-color: #2F9E44 !important;
        color: #FFFFFF !important;
        font-size: 22px !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #268038 !important;
        border-color: #268038 !important;
        color: #FFFFFF !important;
    }

    /* 신고 버튼만 위험 빨강으로 (key=report_call_btn_N 대응) */
    [class*="st-key-report_call_btn"] div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #E03131 !important;
        border-color: #E03131 !important;
        color: #FFFFFF !important;
    }
    [class*="st-key-report_call_btn"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #B02525 !important;
        border-color: #B02525 !important;
        color: #FFFFFF !important;
    }

    .type-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        background-color: #F0EEFC; 
        color: #5B4BC4; 
        font-size: 14px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .word-tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        background-color: #FFFFFF; /* 밝은 배경에 맞게 태그 배경 조정 */
        color: #1A1A2E;
        font-size: 14px;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #ECECF1;
    }

    .guide-box {
        background-color: #EBFBEE;
        border: 1px solid #C3EACB;
        padding: 20px 22px;
        border-radius: 14px;
        margin-bottom: 16px;
    }
    .guide-title {
        font-size: 16px;
        font-weight: 700;
        color: #268038;
        margin-bottom: 16px;
    }
    .guide-divider {
        border-top: 1px solid #C3EACB;
        margin: 16px 0;
    }
    .guide-text {
        font-size: 18px;
        font-weight: 600;
        color: #1A4D24;
        line-height: 1.5;
    }
    .guide-source {
        font-size: 13px;
        color: #268038;
        margin-top: 10px;
        text-align: right;
    }

    div[data-testid="stExpander"] {
        border-radius: 11px !important;
        border: 1px solid #ECECF1 !important;
        background-color: #FFFFFF;
        margin-bottom: 12px;
    }
    div[data-testid="stExpander"] summary {
        padding: 14px 18px !important;
        border-radius: 11px !important;
    }
    div[data-testid="stExpander"] summary p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1A1A2E;
    }
    div[data-testid="stExpanderDetails"] {
        padding: 15px !important;
        border-radius: 12px !important;
        background-color: #F3F3F7; /* 상세 보기 배경 살짝 구분 */
    }
    div[data-testid="stExpanderDetails"] * {
        font-size: 14px;
        line-height: 1.6;
    }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #1A1A2E;
        margin-top: 30px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("설정")
        duration = st.slider("녹음 시간", 10, 30, 10)
        model_size = st.selectbox("Whisper 모델", ["tiny", "base", "small"], index=2)

        devices = list_input_devices()
        labels = ["기본 마이크"] + [f"{d['id']} - {d['name']}" for d in devices]
        chosen = st.selectbox("입력 장치", labels)
        device = None if chosen == "기본 마이크" else int(chosen.split(" - ")[0])

        st.divider()
        st.subheader("KoBERT 상태")
        if predictor.available:
            st.success("멀티라벨 KoBERT 연결됨")
        else:
            st.warning("KoBERT 모델 없음: DB 기반으로 동작")
            if predictor.error:
                st.caption(predictor.error)

        st.divider()
        if st.button("통화 메모리 초기화"):
            st.session_state.history = []
            st.session_state.conversation_memory = []
            st.session_state.current_result = None
            st.session_state.last_saved_report_id = None
            st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎙️ 연속 통화 데모",
    "🧪 단계별 텍스트 데모",
    "📝 단일 텍스트 분석",
    "🗂️ 멀티라벨 DB",
    "🎓 학습 데이터",
    "🚨 신고 DB",
])
    with tab1:
        is_idle = st.session_state.current_result is None

        if is_idle:
            st.markdown(
                '<div class="app-header">'
                '<div class="app-header-left">'
                '<div class="app-logo">📞</div>'
                '<div><div class="app-name-row"><span class="app-name">안심콜 가드</span>'
                '<span class="app-badge-idle">대기 중</span></div>'
                '<div class="app-sub">AI 보이스피싱 탐지 시스템</div></div>'
                '</div></div>',
                unsafe_allow_html=True,
            )

        with st.container(border=True):
            if is_idle:
                st.markdown(
                    '<div class="hero">'
                    '<div class="hero-title">통화 감지를 시작해보세요</div>'
                    '<div class="hero-sub">10초간 통화 내용을 듣고 보이스피싱 위험도를 분석합니다.</div>'
                    '<div class="hero-mic">'
                    '<svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="#2F5BEA" '
                    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                    '<rect x="9" y="2" width="6" height="11" rx="3"/>'
                    '<path d="M5 10v2a7 7 0 0 0 14 0v-2"/>'
                    '<line x1="12" y1="19" x2="12" y2="22"/></svg>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
            cols = st.columns([1, 2, 1])
            with cols[1]:
                do_record = st.button(
                    f"🎙️ {duration}초 듣고 누적 분석 시작" if is_idle else f"🎙️ {duration}초 더 듣고 분석",
                    type="primary",
                    use_container_width=True,
                    key="listen_analyze_btn",
                )
            if is_idle:
                st.markdown(
                    '<div class="hero-hint">🛡️ 버튼을 누르면 음성 인식과 분석이 시작됩니다.</div>',
                    unsafe_allow_html=True,
                )

        if is_idle:
            st.markdown(
                '<div class="tip-box">'
                '<div class="tip-title">💡 분석 후에는 다음 정보가 표시됩니다.</div>'
                '<div class="tip-sub">위험도 점수, 의심 유형, 누적 통화 내용, 유사 사례, 대응 문구 및 신고 안내</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        if do_record:
            wav_path = Path(tempfile.gettempdir()) / f"ansimcall_{datetime.now().strftime('%H%M%S')}.wav"

            with st.spinner(f"{duration}초 동안 녹음 중입니다..."):
                try:
                    record_audio(str(wav_path), duration=duration, samplerate=16000, device=device)
                except Exception as e:
                    st.error(f"녹음 오류: {e}")
                    st.stop()

            st.audio(str(wav_path))

            with st.spinner("Whisper STT 변환 중입니다..."):
                try:
                    current_text = transcribe_audio(str(wav_path), model_size=model_size)
                except Exception as e:
                    st.error(f"STT 오류: {e}")
                    st.stop()

            if current_text:
                st.session_state.conversation_memory.append(current_text)

            conversation_text = "\n".join(st.session_state.conversation_memory[-10:])
            result = analyze_call_text(current_text=current_text, conversation_text=conversation_text, predictor=predictor)

            if result.get("risk_score", 0) >= 60:
                with st.spinner("LLM 2차 검증 중입니다..."):
                    result = apply_llm_verification(result, threshold=60)

            st.session_state.history.append(result)
            st.session_state.current_result = result
            st.rerun()

    with tab2:
        st.markdown("발표 데모용입니다. 아래 대사를 하나씩 누르면 통화가 이어지는 것처럼 누적 분석됩니다.")
        demo_steps = [
            "안녕하세요. 서울중앙지검 수사관입니다.",
            "고객님 명의 계좌가 범죄에 연루되었습니다.",
            "지금 바로 안전계좌로 300만 원을 이체하셔야 합니다.",
            "다른 사람에게 알리면 수사에 불이익이 생길 수 있습니다. 전화 끊지 마세요.",
        ]

        for idx, script in enumerate(demo_steps, 1):
            if st.button(f"{idx}단계 추가: {script}", key=f"step_{idx}"):
                st.session_state.conversation_memory.append(script)
                conversation_text = "\n".join(st.session_state.conversation_memory[-10:])
                result = analyze_call_text(
                    current_text=script,
                    conversation_text=conversation_text,
                    predictor=predictor,
                )

                if result.get("risk_score", 0) >= 60:
                    with st.spinner("LLM 2차 검증 중입니다..."):
                        result = apply_llm_verification(result, threshold=60)

                st.session_state.history.append(result)
                st.session_state.current_result = result
                st.rerun()

        st.markdown("<div class='section-title'>현재 누적 통화</div>", unsafe_allow_html=True)
        st.text_area("memory", "\n".join(st.session_state.conversation_memory), height=160, disabled=True, label_visibility="collapsed")

    with tab3:
        st.markdown("한 번의 텍스트를 분석합니다. 이 탭은 메모리를 사용하지 않는 단일 분석입니다.")
        default = "검찰입니다. 고객님 명의 계좌가 범죄에 연루되었습니다. 지금 바로 안전계좌로 300만 원을 이체하셔야 합니다."
        text = st.text_area("통화 내용 입력", default, height=160)

        if st.button("단일 분석 시작", type="primary"):
            result = analyze_call_text(current_text=text, conversation_text=text, predictor=predictor)

            if result.get("risk_score", 0) >= 60:
                with st.spinner("LLM 2차 검증 중입니다..."):
                    result = apply_llm_verification(result, threshold=60)

            st.session_state.history.append(result)
            st.session_state.current_result = result
            st.rerun()

    with tab4:
        st.markdown("하나의 DB가 KoBERT 학습, 유사 사례 검색, 위험도 계산, 대응 문구 추천에 모두 사용됩니다.")
        cases = load_cases()
        rows = []
        for c in cases:
            rows.append({
                "case_id": c["case_id"],
                "title": c["title"],
                "is_phishing": c["is_phishing"],
                "multi_labels": ", ".join(c["multi_labels"]),
                "risk_score": c["risk_score"],
                "keywords": ", ".join(c["keywords"]),
                "warning_reason": c["warning_reason"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        with st.expander("원본 JSON 보기"):
            st.json(cases)

    with tab5:
        st.markdown("멀티라벨 사례 DB를 KoBERT 학습용 표 형태로 변환한 결과입니다.")
        rows = export_training_rows()
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        st.download_button("학습용 CSV 다운로드", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="kobert_multilabel_training.csv", mime="text/csv")

    with tab6:
        st.markdown("사용자가 신고 버튼을 누른 고위험 통화가 저장되는 DB입니다.")
        reported_cases = load_reported_cases()

        if reported_cases:
            st.dataframe(pd.DataFrame(reported_cases), use_container_width=True)

            with st.expander("원본 JSON 보기"):
                st.json(reported_cases)
        else:
            st.info("아직 저장된 신고 사례가 없습니다.")


    if st.session_state.current_result:
        st.markdown("---")
        render_result(st.session_state.current_result)

elif st.session_state.page == "report":
    render_report_page()