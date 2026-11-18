"""Research-gap analysis from user-provided literature notes."""
import re

def build_prompt(field, research_question, literature_notes, constraints=""):
    if not field.strip() or not research_question.strip() or not literature_notes.strip():
        raise ValueError("Research field, question, and literature notes are required.")
    if len(literature_notes) > 30000:
        raise ValueError("Literature notes exceed the 30,000-character limit.")
    return f"""
You are a cautious research-methods assistant. Analyze ONLY the literature notes supplied below.
Research field: {field.strip()}
Research question: {research_question.strip()}
Constraints/context: {constraints.strip()}
Literature notes:
{literature_notes.strip()}

Return valid JSON only:
{{
  "field": "field",
  "question": "research question",
  "literature_synthesis": "brief synthesis of themes in the supplied notes",
  "candidate_gaps": [
    {{
      "gap": "specific candidate gap",
      "evidence_from_notes": ["paraphrase of a supplied note"],
      "gap_type": "Methodological",
      "rationale": "why this may matter",
      "confidence": "Low"
    }}
  ],
  "research_directions": [
    {{
      "title": "possible research direction",
      "objective": "objective",
      "method": "possible method",
      "validation": "how it could be evaluated"
    }}
  ],
  "limitations": ["what cannot be concluded from these notes"],
  "next_steps": ["specific literature review or validation action"]
}}
Rules:
- Include 1 to 5 candidate_gaps and exactly 3 research_directions.
- gap_type must be Theoretical, Methodological, Empirical, Contextual, or Practical.
- confidence must be Low, Medium, or High.
- Do not invent papers, authors, citations, findings, or publication details.
- Distinguish a candidate gap from a proven novelty claim.
- Evidence must be traceable to the supplied notes; mention note identifiers if present.
- Explicitly identify where the supplied material is insufficient.
""".strip()

def validate_analysis(data):
    if not isinstance(data, dict):
        raise ValueError("Analysis must be a JSON object.")
    for key in ("field", "question", "literature_synthesis"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"Missing or invalid field: {key}")
    gaps = data.get("candidate_gaps")
    if not isinstance(gaps, list) or not 1 <= len(gaps) <= 5:
        raise ValueError("Provide between 1 and 5 candidate gaps.")
    allowed_types = {"Theoretical", "Methodological", "Empirical", "Contextual", "Practical"}
    for i, gap in enumerate(gaps, 1):
        if not isinstance(gap, dict):
            raise ValueError(f"Gap {i} must be an object.")
        for key in ("gap", "rationale"):
            if not isinstance(gap.get(key), str) or not gap[key].strip():
                raise ValueError(f"Gap {i}: {key} is required.")
        if gap.get("gap_type") not in allowed_types:
            raise ValueError(f"Gap {i}: invalid gap_type.")
        if gap.get("confidence") not in {"Low", "Medium", "High"}:
            raise ValueError(f"Gap {i}: invalid confidence.")
        evidence = gap.get("evidence_from_notes")
        if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
            raise ValueError(f"Gap {i}: evidence_from_notes must be a string list.")
    directions = data.get("research_directions")
    if not isinstance(directions, list) or len(directions) != 3:
        raise ValueError("Exactly 3 research directions are required.")
    for i, direction in enumerate(directions, 1):
        if not isinstance(direction, dict) or not all(
            isinstance(direction.get(k), str) and direction[k].strip()
            for k in ("title", "objective", "method", "validation")
        ):
            raise ValueError(f"Research direction {i} is incomplete.")
    for key in ("limitations", "next_steps"):
        if not isinstance(data.get(key), list) or not all(
            isinstance(x, str) and x.strip() for x in data[key]
        ):
            raise ValueError(f"{key} must be a list of non-empty strings.")
    return data

def offline_analysis(field, research_question, literature_notes):
    if not field.strip() or not research_question.strip() or not literature_notes.strip():
        raise ValueError("Research field, question, and literature notes are required.")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", literature_notes) if s.strip()]
    themes = sentences[:5]
    return {
        "field": field.strip(),
        "question": research_question.strip(),
        "literature_synthesis": (
            "Offline mode extracts a small set of supplied note excerpts for manual review. "
            "It does not infer or verify research novelty. Notes considered: " + " | ".join(themes)
        ),
        "candidate_gaps": [{
            "gap": "Potentially under-explored dimension requiring verification in a systematic literature search.",
            "evidence_from_notes": themes[:3],
            "gap_type": "Empirical",
            "rationale": "The provided notes may not cover all relevant studies, populations, methods, or publication venues.",
            "confidence": "Low"
        }],
        "research_directions": [
            {"title": "Broaden the literature search", "objective": "Identify additional studies and competing findings.",
             "method": "Search multiple scholarly databases with documented inclusion criteria.",
             "validation": "Screen and record relevant studies using a reproducible protocol."},
            {"title": "Compare research methods", "objective": "Identify methodological strengths and limitations.",
             "method": "Create a study matrix covering datasets, methods, populations, and metrics.",
             "validation": "Have a second reviewer check coding consistency."},
            {"title": "Test a focused question", "objective": "Convert a candidate gap into a testable research question.",
             "method": "Design a pilot study with a justified sample and baseline.",
             "validation": "Predefine outcomes, ethics review where required, and analysis criteria."}
        ],
        "limitations": [
            "Offline mode does not determine whether a gap is genuinely novel.",
            "The supplied notes may be incomplete, biased, or inaccurate.",
            "Candidate gaps require verification against current scholarly literature."
        ],
        "next_steps": [
            "Search scholarly databases using synonyms and related terms.",
            "Record inclusion and exclusion criteria.",
            "Verify each candidate gap against recent reviews and primary studies."
        ]
    }

def to_markdown(data):
    data = validate_analysis(data)
    lines = [f"# Research Gap Analysis: {data['field']}", "",
             f"**Research question:** {data['question']}", "",
             "## Literature synthesis", data["literature_synthesis"], "",
             "## Candidate research gaps"]
    for i, gap in enumerate(data["candidate_gaps"], 1):
        lines += [f"### {i}. {gap['gap']}", f"**Type:** {gap['gap_type']} · **Confidence:** {gap['confidence']}",
                  f"**Rationale:** {gap['rationale']}", "**Evidence from supplied notes:**"]
        lines += [f"- {x}" for x in gap["evidence_from_notes"]] or ["- No specific note excerpt supplied."]
        lines += [""]
    lines += ["## Research directions"]
    for i, direction in enumerate(data["research_directions"], 1):
        lines += [f"### {i}. {direction['title']}", f"**Objective:** {direction['objective']}",
                  f"**Method:** {direction['method']}", f"**Validation:** {direction['validation']}", ""]
    lines += ["## Limitations"] + [f"- {x}" for x in data["limitations"]]
    lines += ["", "## Next steps"] + [f"- {x}" for x in data["next_steps"]]
    return "\n".join(lines)
