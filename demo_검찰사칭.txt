_model_cache = {}

def transcribe_audio(audio_path: str, model_size: str = "small") -> str:
    from faster_whisper import WhisperModel

    key = (model_size, "cpu")
    if key not in _model_cache:
        _model_cache[key] = WhisperModel(model_size, device="cpu", compute_type="int8")

    prompt = (
        "한국어 전화 통화입니다. 보이스피싱, 검찰, 경찰, 금융감독원, 금감원, 중앙지검, "
        "수사관, 안전계좌, 송금, 이체, 인증번호, 비밀번호, 계좌번호, 휴대폰 고장, "
        "합의금, 앱 설치, 원격 제어, 무료 체험, 자동결제 같은 단어가 나올 수 있습니다."
    )

    model = _model_cache[key]
    segments, info = model.transcribe(
        audio_path,
        language="ko",
        initial_prompt=prompt,
        vad_filter=True,
        beam_size=5,
        temperature=0.0,
        condition_on_previous_text=True,
    )
    return " ".join(seg.text.strip() for seg in segments if seg.text).strip()
