import pytest
from unittest.mock import MagicMock, AsyncMock
from magda_agent.attention.salience import SalienceNetwork
from magda_agent.consciousness.core import Consciousness

def test_noisy_low_value_input() -> None:
    """Test that noisy low-value input gets a low score."""
    network = SalienceNetwork()
    result = network.score_event("hi", user_urgency=0.0, is_ci_failure=False, is_security_risk=False)
    assert result["score"] == 0.0
    assert "Noisy low-value input" in result["explanation"]

def test_failed_ci_event() -> None:
    """Test that a CI failure event receives high salience."""
    network = SalienceNetwork()
    result = network.score_event("test failed", is_ci_failure=True)
    assert result["score"] >= 0.8
    assert "Critical CI failure" in result["explanation"]

def test_security_risk_event() -> None:
    """Test that a security risk event receives high salience."""
    network = SalienceNetwork()
    result = network.score_event("unauthorized access", is_security_risk=True)
    assert result["score"] >= 0.8
    assert "Security risk" in result["explanation"]

def test_high_urgency_event() -> None:
    """Test that high user urgency increases the salience score."""
    network = SalienceNetwork()
    result = network.score_event("I need this now", user_urgency=1.0)
    assert result["score"] > 0.3
    assert "User urgency" in result["explanation"]

@pytest.mark.asyncio
async def test_consciousness_integration() -> None:
    """Test that Consciousness correctly uses SalienceNetwork when processing input."""
    mock_llm = MagicMock()
    mock_llm.chat_completion = AsyncMock(return_value="mock response")
    mock_emotions = MagicMock()
    mock_memory = MagicMock()
    mock_skills = MagicMock()
    mock_salience = MagicMock()
    mock_salience.score_event.return_value = {"score": 0.5, "explanation": "test"}

    consciousness = Consciousness(
        llm=mock_llm,
        emotions=mock_emotions,
        memory=mock_memory,
        skills=mock_skills,
        salience_network=mock_salience
    )

    await consciousness.process_input("hello")
    mock_salience.score_event.assert_called_once_with("hello")
