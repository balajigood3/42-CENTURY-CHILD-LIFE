import pytest
from research_gap.analyzer import build_prompt, validate_analysis, offline_analysis, to_markdown
from research_gap.storage import save_analysis, load_analyses

def sample():
    return {
        "field": "Explainable AI", "question": "How can explanations be evaluated?",
        "literature_synthesis": "Supplied notes discuss explanation methods and evaluation.",
        "candidate_gaps": [{
            "gap": "Limited comparison of evaluation methods in the target setting.",
            "evidence_from_notes": ["[P1] reports metric A.", "[P2] uses metric B."],
            "gap_type": "Methodological", "rationale": "The notes show different evaluation choices.",
            "confidence": "Low"
        }],
        "research_directions": [{
            "title": f"Direction {i}", "objective": "Compare approaches.",
            "method": "Run a controlled comparative study.",
            "validation": "Use predefined metrics and independent review."
        } for i in range(3)],
        "limitations": ["The note set may be incomplete."],
        "next_steps": ["Search additional scholarly databases."]
    }

def test_prompt_includes_question_and_note_ids():
    prompt = build_prompt("XAI", "How to evaluate?", "[P1] Study summary.")
    assert "How to evaluate?" in prompt and "[P1]" in prompt

def test_required_input_rejected():
    with pytest.raises(ValueError):
        build_prompt("Field", "Question", " ")

def test_oversized_notes_rejected():
    with pytest.raises(ValueError):
        build_prompt("Field", "Question", "x" * 30001)

def test_valid_analysis_passes():
    assert validate_analysis(sample())["field"] == "Explainable AI"

def test_invalid_gap_type_rejected():
    data = sample()
    data["candidate_gaps"][0]["gap_type"] = "Novel"
    with pytest.raises(ValueError):
        validate_analysis(data)

def test_invalid_confidence_rejected():
    data = sample()
    data["candidate_gaps"][0]["confidence"] = "Certain"
    with pytest.raises(ValueError):
        validate_analysis(data)

def test_requires_three_research_directions():
    data = sample()
    data["research_directions"].pop()
    with pytest.raises(ValueError):
        validate_analysis(data)

def test_offline_analysis_is_explicitly_cautious():
    result = offline_analysis("AI", "What is missing?", "Study A tests model X. Study B tests model Y.")
    assert validate_analysis(result)["candidate_gaps"][0]["confidence"] == "Low"
    assert any("does not determine" in x for x in result["limitations"])

def test_markdown_export():
    md = to_markdown(sample())
    assert "Candidate research gaps" in md and "Research directions" in md

def test_storage_round_trip(tmp_path):
    p = tmp_path / "analyses.jsonl"
    save_analysis(p, "XAI", "Question?", sample())
    assert load_analyses(p)[0]["analysis"]["field"] == "Explainable AI"

def test_storage_limit(tmp_path):
    p = tmp_path / "analyses.jsonl"
    for i in range(3):
        save_analysis(p, str(i), "Question", sample())
    assert len(load_analyses(p, 2)) == 2
