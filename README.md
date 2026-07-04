# 📞 안심콜 가드 (AnsimCall Guard)

> **AI 기반 실시간 보이스피싱 탐지 및 대응 시스템**


Faster-Whisper STT, Conversation Memory, KoBERT 멀티라벨 분류, Rule-based 하이브리드 탐지, Hybrid Risk Scoring, LLM 2차 검증(Gemini 2.5 Flash)을 결합하여 **통화 중** 보이스피싱을 실시간으로 탐지하고, 사용자가 바로 쓸 수 있는 대응 문구까지 제공하는 시스템입니다.

<p align="center">
<img width="1757" height="652" alt="Image" src="https://github.com/user-attachments/assets/751266a8-cb6c-465c-82d0-8da036edcc67" />
</p>

---

## 🎯 핵심 차별점 3가지

### 1️⃣ 통화 중 실시간 대응멘트 제안

탐지에서 끝나지 않습니다. 위험이 감지되면 **"절대 송금하지 않겠습니다"** 처럼 지금 이 순간 상대에게 말할 수 있는 대응 문구를 근거(유사 사례·LLM 판단 이유)와 함께 화면에 띄웁니다. 당황한 사용자가 통화 중에 그대로 읽기만 하면 되도록 설계했습니다.

### 2️⃣ 1394 신고용 자동 상황요약

신고 버튼을 누르면 LLM이 통화 내용에서 **개인정보를 제거한 상황 요약**을 생성합니다. 보이스피싱 통합신고센터(1394)에 전화했을 때 "이렇게 말씀하세요" 스크립트를 제공하여, 피해자가 상황을 정리하지 못해 신고를 포기하는 문제를 줄입니다.

### 3️⃣ 휴먼 라벨링 기반 성장형 모델

사용자가 신고한 통화는 LLM이 라벨·키워드·요약을 정제하여 `database/reported_cases.json`에 축적됩니다. 이 데이터는 KoBERT 재학습에 사용 가능한 형식으로 내보낼 수 있어, **사용할수록 탐지 성능이 성장하는** 구조입니다.

---

## 📌 프로젝트 소개

기존 보이스피싱 탐지 연구는 한 문장 단위 분석에 머무는 경우가 많습니다. 하지만 실제 보이스피싱은 통화가 진행되며 점진적으로 압박 강도를 높이는 시나리오형 범죄입니다.

안심콜 가드는 통화 내용을 **10초 단위로 계속 분석**하며 Conversation Memory에 누적하고, 현재 구간·누적 대화·유사 사례를 함께 반영하여 **통화가 길어질수록 판단이 정확해지는** 구조를 갖습니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🎙 음성 인식 | Faster-Whisper 기반 한국어 STT, 10~30초 단위 연속 인식 |
| ✏️ STT 보정 | 보이스피싱 도메인 용어 교정 + rapidfuzz 유사 키워드 복원 |
| 🧠 Conversation Memory | 통화 내용 누적 저장, 통화 흐름 기반 누적 위험도 계산 |
| 🤖 KoBERT 멀티라벨 | 기관사칭·금전요구·긴급압박·가족사칭·개인정보·앱설치유도·가입유도 동시 탐지 |
| 🔎 Rule-based 하이브리드 | 사례 DB 키워드 매칭 기반 라벨 탐지 + KoBERT 결과 결합 |
| 📚 Case Retrieval | 사례 DB에서 유사 보이스피싱 사례 Top 3 검색, 위험도 보정 |
| 📊 Hybrid Risk Scoring | 현재 구간 + 누적 대화 + 유사 사례 점수의 가중 합산 |
| 🧾 LLM 2차 검증 | 위험도 60점 이상 시 Gemini 2.5 Flash가 재판단·요약·대응 문구 보정 |
| 🚨 신고 및 DB 저장 | 1394 신고 안내 + 정제된 사례를 신고 DB에 저장 |

---

## 📊 Hybrid Risk Scoring

```text
Final Risk Score
= 현재 구간 점수      × 0.4
+ Conversation Memory × 0.4
+ 사례 DB 유사도       × 0.2
(+ KoBERT 추가 탐지 라벨당 +5점 보정)
```

- 순간적인 위험 발언(현재 구간)과 통화 전체 흐름(누적 대화)을 균형 있게 반영
- 실제 신고 사례와의 유사도로 오탐을 보정

---

## 🖥 실행 화면

### 위험 탐지 — 실시간 대응멘트 제안

위험도 95점 탐지 시 감지된 유형, 유사 사례 Top 3와 함께 **지금 말할 수 있는 대응 문구**가 표시됩니다.

<img src="images/dashboard_warning.png" width="900">

### 상세 분석 — LLM 2차 검증 결과

누적 대화 기록, 방금 들은 말, 탐지 키워드와 함께 LLM의 판단 근거를 확인할 수 있습니다.

<img src="images/dashboard_detail.png" width="900">

### 신고 화면 — 1394 자동 상황요약

신고 시 개인정보가 제거된 상황 안내 스크립트가 생성되고, 사례가 신고 DB에 저장됩니다.

<img src="images/dashboard_report.png" width="900">

---

## 🏗 시스템 구조

```text
                Voice Call
                     │
                     ▼
             Audio Recorder (10초 단위)
                     │
                     ▼
          Faster-Whisper STT
                     │
                     ▼
           STT Text Correction
                     │
                     ▼
         Conversation Memory
            │               │
            ▼               ▼
  KoBERT Multi-label   Rule-based DB 탐지
            │               │
            └───────┬───────┘
                    ▼
          Case Retrieval (유사 사례 Top 3)
                    │
                    ▼
        Hybrid Risk Scoring
                    │
                    ▼
           위험도 ≥ 60 ?
                    │ Yes
                    ▼
     LLM 2차 검증 (Gemini 2.5 Flash)
                    │
                    ▼
   🚨 신고 → 1394 상황요약 + 신고 DB 저장
                    │
                    ▼
        향후 KoBERT 재학습 (성장형 모델)
```

---

## 📂 프로젝트 구조

```text
ansimcall_guard/
├── app.py                      # Streamlit 대시보드 (메인 앱)
├── train_multilabel_kobert.py  # KoBERT 멀티라벨 학습 스크립트
├── requirements.txt
├── .env.example                # GEMINI_API_KEY 설정 예시
│
├── modules/
│   ├── audio_recorder.py       # 마이크 녹음
│   ├── stt_engine.py           # Faster-Whisper STT
│   ├── stt_correction.py       # STT 보정 + fuzzy 키워드 복원
│   ├── analysis_engine.py      # 분석 파이프라인 총괄
│   ├── db_analyzer.py          # Rule-based 라벨 탐지
│   ├── case_db.py              # 사례 DB 로드 / 유사 사례 검색
│   ├── kobert_multilabel.py    # KoBERT 멀티라벨 추론
│   ├── llm_verifier.py         # Gemini 2.5 Flash 2차 검증
│   └── report_manager.py       # 신고 DB 저장 / 학습 데이터 내보내기
│
├── models/
│   └── kobert_multilabel/      # 학습된 KoBERT 모델 (별도 학습 필요)
│
├── data/
│   └── multilabel_cases.json   # 보이스피싱 사례 DB
│
├── database/
│   └── reported_cases.json     # 사용자 신고 DB (자동 생성)
│
└── images/                     # README 스크린샷
```

---

## ⚙ 기술 스택

| 분야 | 기술 |
|------|------|
| Language | Python |
| UI | Streamlit |
| STT | Faster-Whisper |
| NLP | KoBERT (skt/kobert-base-v1) 멀티라벨 분류 |
| 탐지 보조 | Rule-based 키워드 매칭 + rapidfuzz |
| LLM | Gemini 2.5 Flash |
| Framework | HuggingFace Transformers |
| Database | JSON |
| Audio | SoundDevice / SoundFile |

---

## ▶ 실행 방법

### 1. 설치

```bash
git clone https://github.com/mainymlee/ansimcall_guard.git
cd ansimcall_guard

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 2. API 키 설정

`.env.example`을 복사해 `.env`를 만들고 Gemini API 키를 입력합니다.

```text
GEMINI_API_KEY=your_api_key_here
```

### 3. (선택) KoBERT 멀티라벨 학습

```bash
python train_multilabel_kobert.py --csv data/train.csv --output models/kobert_multilabel
```

학습된 모델이 없어도 Rule-based 탐지만으로 동작합니다.

### 4. 실행

```bash
streamlit run app.py
```

---

## 🚀 향후 계획

- 경찰청 · 금융감독원 신고 API 연동
- 신고 DB 기반 KoBERT 자동 재학습 파이프라인
- Android 앱 개발 및 실시간 통화 연동
- 사례 DB 확장 (금융감독원 공개 사례 반영)

---

## 👥 Team 코딩콩떡

2026 X+AI·SW 융합 프로젝트 출품작 (강원대학교)
