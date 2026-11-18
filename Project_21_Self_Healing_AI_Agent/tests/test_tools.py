import pytest
from app.tools import SafeTools, ToolError

def test_calculator(tmp_path):
    tools = SafeTools(tmp_path)
    assert tools.call("calculator", expression="2 + 3 * 4") == "14"

def test_disallowed_tool(tmp_path):
    tools = SafeTools(tmp_path)
    with pytest.raises(ToolError):
        tools.call("shell", command="echo unsafe")

def test_path_traversal_blocked(tmp_path):
    tools = SafeTools(tmp_path)
    with pytest.raises(ToolError):
        tools.call("write_file", path="../escape.txt", content="bad")

def test_write_and_read(tmp_path):
    tools = SafeTools(tmp_path)
    tools.call("write_file", path="notes/a.txt", content="hello")
    assert tools.call("read_file", path="notes/a.txt") == "hello"
