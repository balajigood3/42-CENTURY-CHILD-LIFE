"""Local speech-to-text and text-to-speech adapters."""
from __future__ import annotations
from pathlib import Path
import tempfile

def transcribe_audio(audio_bytes: bytes, filename: str = "input.wav",
                     model_size: str = "small", language: str = "ta") -> str:
    if not audio_bytes:
        raise ValueError("Audio file காலியாக உள்ளது.")
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Speech recognition-க்கு faster-whisper install செய்யவும்: "
            "pip install faster-whisper"
        ) from exc

    suffix = Path(filename).suffix or ".wav"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(audio_bytes)
            temp_path = Path(temp.name)
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _info = model.transcribe(str(temp_path), language=language, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise RuntimeError("Audio-வில் புரிந்துகொள்ளக்கூடிய பேச்சு கிடைக்கவில்லை.")
        return text
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

def synthesize_speech(text: str, output_path: str) -> str:
    if not text.strip():
        raise ValueError("குரலாக மாற்ற உரை இல்லை.")
    try:
        import pyttsx3
    except ImportError as exc:
        raise RuntimeError("Text-to-speech-க்கு pyttsx3 install செய்யவும்.") from exc
    engine = pyttsx3.init()
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    engine.stop()
    path = Path(output_path)
    if not path.exists() or path.stat().st_size == 0:
        raise RuntimeError("Audio output உருவாக்கப்படவில்லை.")
    return str(path)
