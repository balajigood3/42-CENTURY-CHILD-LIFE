import json
import pytest
from story_ai.generator import build_prompt, template_story, generate_story, ollama_story
from story_ai.storage import save_story, recent_stories

def test_prompt_contains_topic_and_tamil_instruction():
    prompt = build_prompt("கடல்", "சாகசம்", "குழந்தைகள்", "சிறியது")
    assert "கடல்" in prompt
    assert "தமிழில் மட்டும்" in prompt

def test_empty_topic_rejected():
    with pytest.raises(ValueError):
        build_prompt(" ", "நட்பு", "அனைவரும்", "சிறியது")

def test_invalid_genre_rejected():
    with pytest.raises(ValueError):
        build_prompt("மரம்", "unknown", "அனைவரும்", "சிறியது")

def test_template_story_has_title_and_moral():
    story = template_story("நல்ல நண்பன்", "நட்பு")
    assert "நல்ல நண்பன்" in story
    assert "கதையின் கருத்து" in story

def test_generate_template_mode():
    assert "கதையின் கருத்து" in generate_story("மழை", "கற்பனை")

def test_invalid_mode_rejected():
    with pytest.raises(ValueError):
        generate_story("மழை", "கற்பனை", mode="cloud")

def test_storage_round_trip(tmp_path):
    path = tmp_path / "stories.jsonl"
    save_story(path, "மழை", "கற்பனை", "ஒரு கதை", "template")
    rows = recent_stories(path)
    assert rows[0]["story"] == "ஒரு கதை"

def test_history_limit(tmp_path):
    path = tmp_path / "stories.jsonl"
    for i in range(3):
        save_story(path, str(i), "நட்பு", "கதை", "template")
    assert len(recent_stories(path, 2)) == 2
