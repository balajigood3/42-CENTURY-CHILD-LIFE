"""Offline audio transcription and deterministic knowledge extraction."""
from __future__ import annotations
import re
import tempfile
from pathlib import Path

MAX_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}

def validate_audio(filename: str, size: int) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported audio format: {suffix or '(missing extension)'}.")
    if size <= 0:
        raise ValueError("The uploaded audio file is empty.")
    if size > MAX_BYTES:
        raise ValueError(f"Audio exceeds the {MAX_BYTES // (1024 * 1024)} MB limit.")

def transcribe_audio(audio_bytes: bytes, filename: str, model_size: str = "tiny") -> str:
    """Transcribe with faster-whisper on CPU. Model weights are fetched on first run."""
    validate_audio(filename, len(audio_bytes))
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Speech transcription is optional. Install it with: "
            "pip install faster-whisper. You can also paste a transcript manually."
        ) from exc
    if model_size not in {"tiny", "base", "small"}:
        raise ValueError("Model size must be tiny, base, or small.")
    suffix = Path(filename).suffix.lower()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(temp_path, vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception as exc:
        raise RuntimeError(f"Transcription failed: {exc}") from exc
    finally:
        if temp_path and Path(temp_path).exists():
            Path(temp_path).unlink()

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]

def build_knowledge(transcript: str) -> dict:
    text = re.sub(r"\s+", " ", transcript).strip()
    if not text:
        raise ValueError("Transcript cannot be empty.")
    sentences = _sentences(text)
    words = re.findall(r"\b[\w'-]+\b", text)
    summary = " ".join(sentences[:3])
    if len(summary) > 650:
        summary = summary[:647].rsplit(" ", 1)[0] + "..."
    key_points = sentences[:10]
    action_patterns = re.compile(
        r"\b(need to|should|must|will|please|action item|follow up|remember to|todo)\b",
        re.I
    )
    action_items = [s for s in sentences if action_patterns.search(s)][:10]
    stop = {"the", "and", "for", "that", "this", "with", "from", "have", "will",
            "your", "you", "are", "was", "were", "into", "about", "need", "should"}
    terms = []
    seen = set()
    for word in re.findall(r"\b[A-Z][a-zA-Z0-9-]{2,}\b", text):
        key = word.lower()
        if key not in stop and key not in seen:
            terms.append(word)
            seen.add(key)
    faq_candidates = [f"What is the main point of: {s[:140]}" for s in sentences[:5]]
    return {
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
        "terms": terms[:20],
        "faq_candidates": faq_candidates,
        "transcript": text,
        "word_count": len(words),
    }
