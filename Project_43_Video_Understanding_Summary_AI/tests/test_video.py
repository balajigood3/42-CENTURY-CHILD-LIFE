import pytest
from video_understanding.processor import validate_video, sample_timestamps
from video_understanding.summarizer import summarize_video

def test_valid_extension_and_bytes():
    validate_video("clip.mp4", b"fake-video-bytes")

def test_invalid_extension():
    with pytest.raises(ValueError):
        validate_video("clip.exe", b"data")

def test_empty_video_rejected():
    with pytest.raises(ValueError):
        validate_video("clip.mp4", b"")

def test_non_bytes_rejected():
    with pytest.raises(TypeError):
        validate_video("clip.mp4", "not bytes")

def test_sample_timestamps():
    assert sample_timestamps(10, 3) == [0.0, 5.0, 10.0]

def test_short_video_timestamp():
    assert sample_timestamps(0.2, 6) == [0.0]

def test_invalid_frame_count():
    with pytest.raises(ValueError):
        sample_timestamps(10, 0)

def test_summary_without_captions_is_transparent():
    report = summarize_video({"filename":"x.mp4", "duration_seconds":5, "width":640, "height":480}, [])
    assert "No semantic frame captions" in report["summary"]
    assert report["resolution"] == "640x480"

def test_summary_includes_captions_and_transcript():
    report = summarize_video(
        {"filename":"x.mp4", "duration_seconds":10, "width":1280, "height":720, "fps":30, "sampled_frame_count":1},
        [{"timestamp":2.0, "caption":"A person enters a room."}],
        "Hello everyone."
    )
    assert "A person enters a room" in report["summary"]
    assert report["transcript_included"] is True
