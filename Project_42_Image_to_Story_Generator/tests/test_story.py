import io
import pytest
from PIL import Image
from story_generator.story import generate_story
from story_generator.vision import validate_image, describe_image

def test_story_generation_contains_scene():
    result = generate_story("A red bicycle beside a tree", "adventure")
    assert "red bicycle" in result["story"]
    assert result["word_count"] > 0

def test_story_styles_supported():
    for style in ["adventure", "fairy_tale", "science_fiction", "mystery"]:
        assert generate_story("A mountain at sunrise", style)["style"] == style

def test_prompt_is_included():
    result = generate_story("A quiet beach", user_prompt="Include a lost map")
    assert "Include a lost map" in result["story"]

def test_empty_caption_rejected():
    with pytest.raises(ValueError):
        generate_story(" ")

def test_invalid_style_rejected():
    with pytest.raises(ValueError):
        generate_story("A forest", "horror")

def test_word_limit_validation():
    with pytest.raises(ValueError):
        generate_story("A forest", max_words=10)

def test_valid_image():
    buf = io.BytesIO()
    Image.new("RGB", (32, 24), "white").save(buf, format="PNG")
    img = validate_image(buf.getvalue())
    assert img.size == (32, 24)

def test_invalid_image_rejected():
    with pytest.raises(ValueError):
        validate_image(b"not an image")

def test_metadata_fallback_caption():
    buf = io.BytesIO()
    Image.new("RGB", (20, 10), "white").save(buf, format="PNG")
    result = describe_image(buf.getvalue())
    assert result["caption"]
    assert result["caption_source"] == "metadata_fallback"
