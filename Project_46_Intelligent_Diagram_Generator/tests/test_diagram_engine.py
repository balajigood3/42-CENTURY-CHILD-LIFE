import pytest
from diagram_engine import parse_process, to_mermaid, render_svg

def test_parses_sequential_steps():
    nodes, edges = parse_process("Start\nValidate\nFinish")
    assert [n["label"] for n in nodes] == ["Start", "Validate", "Finish"]
    assert edges == [("N1", "N2"), ("N2", "N3")]

def test_parses_explicit_branch_connections():
    nodes, edges = parse_process("Request -> Approve -> Complete\nRequest -> Reject")
    assert len(nodes) == 4
    assert ("N1", "N2") in edges
    assert ("N1", "N4") in edges

def test_deduplicates_nodes_and_edges():
    nodes, edges = parse_process("Start -> End\nStart -> End")
    assert len(nodes) == 2
    assert edges == [("N1", "N2")]

@pytest.mark.parametrize("value", ["", "   ", "\n"])
def test_rejects_empty_description(value):
    with pytest.raises(ValueError):
        parse_process(value)

def test_rejects_bad_arrow():
    with pytest.raises(ValueError):
        parse_process("Start -> -> End")

def test_mermaid_export():
    nodes, edges = parse_process("A\nB")
    output = to_mermaid(nodes, edges)
    assert output.startswith("flowchart TD")
    assert "N1 --> N2" in output

def test_svg_export_escapes_markup():
    nodes, edges = parse_process("Input <safe>\nOutput")
    svg = render_svg(nodes, edges)
    assert "<svg" in svg
    assert "&lt;safe&gt;" in svg

def test_rejects_invalid_layout():
    with pytest.raises(ValueError):
        parse_process("A", "Mindmap")
