import pytest
from PIL import Image
from visual_qa import validate_image, answer_question, MAX_IMAGE_BYTES

def sample_image():
    return Image.new("RGB", (320, 200), (200, 50, 30))

def test_accepts_supported_image():
    validate_image("sample.PNG", 100)

@pytest.mark.parametrize("filename", ["photo.gif", "file.txt", "image"])
def test_rejects_unsupported_extension(filename):
    with pytest.raises(ValueError):
        validate_image(filename, 100)

def test_rejects_empty_and_oversized_upload():
    with pytest.raises(ValueError):
        validate_image("a.png", 0)
    with pytest.raises(ValueError):
        validate_image("a.png", MAX_IMAGE_BYTES + 1)

def test_basic_width_answer():
    result = answer_question(sample_image(), "What is the width?", "Basic image analysis")
    assert "320 pixels wide" in result["answer"]
    assert result["details"]["height"] == 200

def test_basic_height_answer():
    result = answer_question(sample_image(), "What is the height?", "Basic image analysis")
    assert "200 pixels high" in result["answer"]

def test_basic_aspect_ratio_answer():
    result = answer_question(sample_image(), "What is the aspect ratio?", "Basic image analysis")
    assert "1.6" in result["answer"]

def test_requires_question():
    with pytest.raises(ValueError):
        answer_question(sample_image(), "  ", "Basic image analysis")

def test_rejects_unknown_mode():
    with pytest.raises(ValueError):
        answer_question(sample_image(), "What is shown?", "Remote API")

def test_details_are_returned():
    result = answer_question(sample_image(), "Describe it", "Basic image analysis")
    assert result["method"] == "Basic image analysis"
    assert result["details"]["width"] == 320
