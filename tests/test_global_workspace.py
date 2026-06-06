import pytest
from magda_agent.attention.workspace import GlobalWorkspace

def test_add_candidate() -> None:
    """Test adding a candidate to the global workspace."""
    workspace = GlobalWorkspace()
    workspace.add_candidate({"source": "user", "content": "hello", "salience": 0.5})
    assert len(workspace.candidates) == 1
    assert workspace.candidates[0]["content"] == "hello"

def test_select_focus() -> None:
    """Test selecting the highest salience candidate as focus."""
    workspace = GlobalWorkspace()
    workspace.add_candidate({"source": "user", "content": "hello", "salience": 0.2})
    workspace.add_candidate({"source": "internal", "content": "alert", "salience": 0.8})
    workspace.add_candidate({"source": "system", "content": "log", "salience": 0.5})

    focused = workspace.select_focus()
    assert focused is not None
    assert focused["source"] == "internal"
    assert focused["salience"] == pytest.approx(0.8)

    assert len(workspace.suppressed_candidates) == 2
    assert workspace.suppressed_candidates[0]["source"] == "system"  # Next highest
    assert workspace.suppressed_candidates[1]["source"] == "user"

    # Candidates should be cleared after selection
    assert len(workspace.candidates) == 0

def test_clear_workspace() -> None:
    """Test clearing the global workspace state."""
    workspace = GlobalWorkspace()
    workspace.add_candidate({"source": "user", "content": "hello", "salience": 0.5})
    workspace.select_focus()

    assert workspace.focused_event is not None
    assert len(workspace.suppressed_candidates) == 0

    workspace.clear()
    assert workspace.focused_event is None
    assert len(workspace.suppressed_candidates) == 0
    assert len(workspace.candidates) == 0

def test_empty_workspace_select() -> None:
    """Test selecting focus when the workspace is empty."""
    workspace = GlobalWorkspace()
    focused = workspace.select_focus()
    assert focused is None

def test_missing_salience() -> None:
    """Test adding a candidate without a salience score defaults to 0.0."""
    workspace = GlobalWorkspace()
    workspace.add_candidate({"source": "user", "content": "hello"})
    assert workspace.candidates[0]["salience"] == pytest.approx(0.0)
