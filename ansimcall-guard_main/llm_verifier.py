from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf

def list_input_devices():
    devices = sd.query_devices()
    result = []
    for idx, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0:
            result.append({
                "id": idx,
                "name": d.get("name", f"Device {idx}"),
                "channels": d.get("max_input_channels", 0),
                "samplerate": int(d.get("default_samplerate", 16000)),
            })
    return result

def record_audio(output_path: str, duration: float = 10.0, samplerate: int = 16000, device=None):
    frames = int(duration * samplerate)
    audio = sd.rec(frames, samplerate=samplerate, channels=1, dtype="float32", device=device)
    sd.wait()
    audio = np.squeeze(audio)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio, samplerate)
    return output_path
