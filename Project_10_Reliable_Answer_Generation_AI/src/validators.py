def basic_checks(question,answer,evidence):
    """Small transparent checks; these do not prove factual correctness."""
    issues=[]
    if not answer.strip():
        issues.append("Empty answer")
    if len(answer.strip()) < 20:
        issues.append("Answer is unusually short; check completeness")
    if not evidence.strip():
        issues.append("No reference evidence supplied; factual claims remain unverified")
    suspicious=["according to the source", "as cited above", "[1]", "[2]"]
    for marker in suspicious:
        if marker in answer.lower() and not evidence.strip():
            issues.append(f"Possible unsupported citation/source wording: {marker}")
    if question.strip() and len(answer.split()) < 5:
        issues.append("Answer may not address the question sufficiently")
    return {"passed_basic_checks": not issues, "issues": issues}
