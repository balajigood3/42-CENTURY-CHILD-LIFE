import pytest
from PIL import Image
from multimodal_assistant import (
    validate_upload, image_context, build_response, MAX_UPLOAD_BYTES
)

def test_validates_image_and_audio():
    validate_upload("picture.PNG", 100, "image")
    validate_upload("speech.WAV", 100, "audio")

@pytest.mark.parametrize("filename,modality", [
    ("clip.mp4", "audio"), ("scan.pdf", "image"), ("file", "image")
])
def test_rejects_wrong_extensions(filename, modality):
    with pytest.raises(ValueError):
        validate_upload(filename, 100, modality)

def test_rejects_empty_and_oversized_files():
    with pytest.raises(ValueError):
        validate_upload("a.png", 0, "image")
    with pytest.raises(ValueError):
        validate_upload("a.wav", MAX_UPLOAD_BYTES + 1, "audio")

def test_rejects_unknown_modality():
    with pytest.raises(ValueError):
        validate_upload("a.txt", 10, "text")

def test_image_metadata_context():
    img = Image.new("RGB", (100, 50), (20, 100, 200))
    context = image_context(img)
    assert "100x50" in context
    assert "average RGB" in context

def test_builds_multimodal_response():
    result = build_response("Summarize these inputs", [
        ("Text", "The meeting starts at 10."),
        ("Image", "Image dimensions: 640x480."),
        ("Audio transcript", "Please prepare the agenda."),
    ])
    assert result["question"] == "Summarize these inputs"
    assert len(result["context"]) == 3
    assert "Audio transcript" in result["response"]
    assert "# Multimodal Assistant Response" in result["markdown"]

def test_rejects_empty_question_and_context():
    with pytest.raises(ValueError):
        build_response(" ", [("Text", "hello")])
    with pytest.raises(ValueError):
        build_response("Question?", [("Text", "  ")])

def test_empty_context_list_rejected():
    with pytest.raises(ValueError):
        build_response("Question?", [])
