"""Transparent extractive summary builder for video metadata and frame captions."""
from __future__ import annotations

def summarize_video(metadata: dict, captions: list[dict], transcript: str = "") -> dict:
    duration = float(metadata.get("duration_seconds", 0))
    lines = []
    for item in captions:
        caption = str(item.get("caption", "")).strip()
        if caption:
            lines.append(f"{item.get('timestamp', 0):.1f}s: {caption}")
    if transcript.strip():
        transcript_preview = " ".join(transcript.split())[:1200]
    else:
        transcript_preview = ""
    if lines:
        summary = "Sampled visual events:\\n" + "\\n".join(lines)
    else:
        summary = (
            "No semantic frame captions are available. "
            "The video was inspected for duration, frame rate, resolution, and sampled keyframes only."
        )
    if transcript_preview:
        summary += "\\n\\nAudio transcript excerpt:\\n" + transcript_preview
    return {
        "filename": metadata.get("filename", "video"),
        "duration_seconds": duration,
        "resolution": f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
        "fps": metadata.get("fps", 0),
        "sampled_frame_count": metadata.get("sampled_frame_count", len(captions)),
        "summary": summary,
        "transcript_included": bool(transcript_preview),
        "method": "sampled_frame_captioning_and_metadata",
        "disclaimer": "Summary quality depends on available frame captions and transcript. Sampling may miss events between frames."
    }
