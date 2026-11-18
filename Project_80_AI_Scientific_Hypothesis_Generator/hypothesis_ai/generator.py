"""Generate testable candidate hypotheses from user-supplied observations."""
ALLOWED_STUDY_TYPES = {"Experimental", "Observational", "Computational", "Survey", "Mixed methods"}

def build_prompt(field, observation, background, study_type, constraints=""):
    if not field.strip() or not observation.strip() or not background.strip():
        raise ValueError("Research field, observation, and background are required.")
    if len(background) > 20000 or len(observation) > 10000:
        raise ValueError("Input exceeds the configured length limit.")
    if study_type not in ALLOWED_STUDY_TYPES:
        raise ValueError("Unsupported study type.")
    return f"""
You are a cautious scientific research assistant.
Research field: {field.strip()}
Observation or phenomenon: {observation.strip()}
Background evidence supplied by user: {background.strip()}
Preferred study type: {study_type}
Constraints: {constraints.strip()}

Generate candidate hypotheses, not established facts. Return valid JSON only:
{{
  "field": "research field",
  "phenomenon": "short restatement",
  "background_summary": "summary of supplied evidence",
  "hypotheses": [
    {{
      "statement": "clear, falsifiable hypothesis",
      "null_hypothesis": "corresponding null hypothesis",
      "rationale": "reasoning linked to supplied background",
      "variables": {{
        "independent": ["variable"],
        "dependent": ["variable"],
        "controls": ["variable"]
      }},
      "predictions": ["measurable prediction"],
      "study_design": "suggested design",
      "measurement": "how variables could be measured",
      "confounders": ["possible confounder"],
      "ethical_considerations": ["ethical concern"],
      "confidence": "Low"
    }}
  ],
  "validation_plan": ["steps to test the hypothesis"],
  "limitations": ["what remains uncertain"]
}}
Rules:
- Include 1 to 3 hypotheses.
- Each hypothesis must be testable and falsifiable.
- Separate correlation from causation; do not imply causality for observational designs.
- Do not fabricate citations, datasets, results, or prior findings.
- Confidence must be Low, Medium, or High and reflect evidence quality.
- Include measurable variables, possible confounders, and ethical considerations.
- Do not propose unsafe human or animal experiments; require relevant ethics review.
""".strip()

def validate_output(data):
    if not isinstance(data, dict):
        raise ValueError("Output must be a JSON object.")
    for key in ("field", "phenomenon", "background_summary"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError(f"Missing or invalid field: {key}")
    hypotheses = data.get("hypotheses")
    if not isinstance(hypotheses, list) or not 1 <= len(hypotheses) <= 3:
        raise ValueError("Provide between 1 and 3 hypotheses.")
    for i, item in enumerate(hypotheses, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Hypothesis {i} must be an object.")
        for key in ("statement", "null_hypothesis", "rationale", "study_design", "measurement"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Hypothesis {i}: {key} is required.")
        if item.get("confidence") not in {"Low", "Medium", "High"}:
            raise ValueError(f"Hypothesis {i}: invalid confidence.")
        variables = item.get("variables")
        if not isinstance(variables, dict):
            raise ValueError(f"Hypothesis {i}: variables must be an object.")
        for key in ("independent", "dependent", "controls"):
            if not isinstance(variables.get(key), list) or not all(
                isinstance(x, str) and x.strip() for x in variables[key]
            ):
                raise ValueError(f"Hypothesis {i}: {key} must be a string list.")
        for key in ("predictions", "confounders", "ethical_considerations"):
            if not isinstance(item.get(key), list) or not item[key] or not all(
                isinstance(x, str) and x.strip() for x in item[key]
            ):
                raise ValueError(f"Hypothesis {i}: {key} must be a non-empty string list.")
    for key in ("validation_plan", "limitations"):
        if not isinstance(data.get(key), list) or not data[key] or not all(
            isinstance(x, str) and x.strip() for x in data[key]
        ):
            raise ValueError(f"{key} must be a non-empty string list.")
    return data

def offline_template(field, observation, background):
    if not field.strip() or not observation.strip() or not background.strip():
        raise ValueError("Research field, observation, and background are required.")
    return {
        "field": field.strip(),
        "phenomenon": observation.strip(),
        "background_summary": "Offline mode preserves your input as context; it does not synthesize or verify scientific evidence.",
        "hypotheses": [{
            "statement": "Among the defined study population, the measured outcome may differ between the specified exposure and comparison conditions.",
            "null_hypothesis": "There is no measurable difference in the defined outcome between the exposure and comparison conditions.",
            "rationale": "This is a generic hypothesis scaffold. Refine it using established theory and the supplied background.",
            "variables": {
                "independent": ["Clearly define the exposure or intervention"],
                "dependent": ["Select one measurable outcome"],
                "controls": ["Predefine relevant baseline and contextual variables"]
            },
            "predictions": ["The outcome measure will differ by a predefined threshold between groups or conditions."],
            "study_design": "Choose an appropriate design after checking feasibility and ethics requirements.",
            "measurement": "Use validated instruments and predefine the measurement protocol.",
            "confounders": ["Selection bias", "Measurement error", "Unmeasured contextual factors"],
            "ethical_considerations": ["Obtain required ethics approval and informed consent where applicable."],
            "confidence": "Low"
        }],
        "validation_plan": [
            "Define the population, exposure, outcome, and comparison condition.",
            "Review prior literature and refine the operational definitions.",
            "Pre-register the analysis plan where appropriate.",
            "Assess feasibility, sample size, bias, and ethical requirements."
        ],
        "limitations": [
            "Offline mode does not evaluate the scientific plausibility of the hypothesis.",
            "The scaffold is not evidence of novelty or causality.",
            "A domain expert and formal literature review are needed before conducting a study."
        ]
    }

def to_markdown(data):
    data = validate_output(data)
    lines = [f"# Scientific Hypothesis Generator: {data['field']}", "",
             f"**Phenomenon:** {data['phenomenon']}", "",
             "## Background summary", data["background_summary"], "",
             "## Candidate hypotheses"]
    for i, h in enumerate(data["hypotheses"], 1):
        lines += [f"### Hypothesis {i}", h["statement"],
                  f"**Null hypothesis:** {h['null_hypothesis']}",
                  f"**Rationale:** {h['rationale']}",
                  f"**Study design:** {h['study_design']}",
                  f"**Measurement:** {h['measurement']}",
                  f"**Confidence:** {h['confidence']}", "**Variables:**"]
        for key, values in h["variables"].items():
            lines.append(f"- **{key.title()}:** {', '.join(values)}")
        for key in ("predictions", "confounders", "ethical_considerations"):
            lines.append(f"**{key.replace('_', ' ').title()}:**")
            lines.extend(f"- {x}" for x in h[key])
        lines.append("")
    lines += ["## Validation plan"] + [f"- {x}" for x in data["validation_plan"]]
    lines += ["", "## Limitations"] + [f"- {x}" for x in data["limitations"]]
    return "\n".join(lines)
