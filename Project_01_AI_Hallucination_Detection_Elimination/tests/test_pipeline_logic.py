def test_status_logic_examples():
    statuses = {"SUPPORTED", "UNKNOWN"}
    if "CONTRADICTED" in statuses:
        overall = "CONTRADICTION FOUND"
    elif "UNKNOWN" in statuses:
        overall = "PARTIALLY VERIFIED / UNKNOWN"
    else:
        overall = "SUPPORTED BY PROVIDED EVIDENCE"
    assert overall == "PARTIALLY VERIFIED / UNKNOWN"
