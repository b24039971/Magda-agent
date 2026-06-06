"""Tests for the Amygdala RiskSystem."""

from magda_agent.safety.amygdala import RiskSystem

def test_risk_system_initialization():
    """Test that the RiskSystem initializes correctly."""
    rs = RiskSystem()
    assert rs is not None

def test_classify_file_change_low_risk():
    """Test classification of low-risk file changes."""
    rs = RiskSystem()
    assert rs.classify_file_change("docs/architecture.md") == "low"
    assert rs.classify_file_change("docs/some_image.png") == "low"
    assert rs.classify_file_change("README.md") == "low"

def test_classify_file_change_high_risk():
    """Test classification of high-risk file changes."""
    rs = RiskSystem()
    assert rs.classify_file_change(".github/workflows/main.yml") == "high"
    assert rs.classify_file_change("requirements.txt") == "high"
    assert rs.classify_file_change("sandbox/executor.py") == "high"
    assert rs.classify_file_change("magda_agent/skills/registry.py") == "high"

def test_classify_file_change_critical_risk():
    """Test classification of critical-risk file changes."""
    rs = RiskSystem()
    assert rs.classify_file_change("secrets/db_password.txt") == "critical"
    assert rs.classify_file_change(".env") == "critical"
    assert rs.classify_file_change(".env.production") == "critical"

def test_classify_file_change_medium_risk():
    """Test classification of medium-risk file changes (general code)."""
    rs = RiskSystem()
    assert rs.classify_file_change("magda_agent/core.py") == "medium"
    assert rs.classify_file_change("tests/test_something.py") == "medium"

def test_classify_action():
    """Test classification of actions."""
    rs = RiskSystem()

    # Read/inspect actions are low risk
    assert rs.classify_action("read", "magda_agent/core.py") == "low"
    assert rs.classify_action("inspect", "requirements.txt") == "low"

    # Edit actions delegate to file classification
    assert rs.classify_action("edit", "docs/README.md") == "low"
    assert rs.classify_action("edit", "magda_agent/core.py") == "medium"
    assert rs.classify_action("edit", "requirements.txt") == "high"
    assert rs.classify_action("edit", "secrets/db_password.txt") == "critical"

    # Execute actions are generally high risk
    assert rs.classify_action("execute", "sandbox/runner.py") == "high"
    assert rs.classify_action("execute", "some_safe_tool") == "high"
