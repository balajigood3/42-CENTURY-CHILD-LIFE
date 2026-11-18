import pytest
from story_video import parse_story, create_frame, render_video

def test_parse_story_into_scenes():
    scenes = parse_story("First scene. Second scene! Third scene?")
    assert scenes == ["First scene.", "Second scene!", "Third scene?"]

def test_parse_story_limits_scene_count():
    assert len(parse_story("A. B. C.", max_scenes=2)) == 2

@pytest.mark.parametrize("story", ["", "   ", None])
def test_rejects_empty_story(story):
    with pytest.raises(ValueError):
        parse_story(story)

def test_rejects_invalid_scene_limit():
    with pytest.raises(ValueError):
        parse_story("Story.", max_scenes=21)

def test_creates_frame():
    frame = create_frame("A hero enters a forest.", "Test Story", 1, 1, width=640, height=360)
    assert frame.size == (640, 360)

def test_rejects_unknown_style():
    with pytest.raises(ValueError):
        create_frame("Scene", "Title", 1, 1, style="Unknown")

def test_renders_mp4():
    video = render_video(["A short scene."], seconds_per_scene=1, fps=2)
    assert video[:4] == b"\x00\x00\x00\x18" or b"ftyp" in video[:16]
    assert len(video) > 1000

def test_rejects_invalid_duration():
    with pytest.raises(ValueError):
        render_video(["Scene"], seconds_per_scene=0)
