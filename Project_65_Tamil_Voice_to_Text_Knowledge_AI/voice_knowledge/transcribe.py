"""Speech-to-text adapters: offline audio metadata and optional local Whisper."""
from pathlib import Path

class TranscriptionError(RuntimeError):
    pass

def transcribe_audio(path: str, model_size: str = "base") -> dict:
    audio_path = Path(path)
    if not audio_path.is_file():
        raise TranscriptionError("Audio file does not exist.")
    if audio_path.suffix.lower() not in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
        raise TranscriptionError("Supported audio: WAV, MP3, M4A, FLAC, OGG.")
    try:
        import whisper
    except ImportError as exc:
        raise TranscriptionError(
            "Whisper package is not installed. Install requirements and download a model on first use."
        ) from exc
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(str(audio_path), language="ta", task="transcribe")
        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "ta"),
            "segments": [
                {"start": float(s.get("start", 0)), "end": float(s.get("end", 0)),
                 "text": s.get("text", "").strip()}
                for s in result.get("segments", [])
            ],
        }
    except Exception as exc:
        raise TranscriptionError(f"Local Whisper transcription failed: {exc}") from exc
