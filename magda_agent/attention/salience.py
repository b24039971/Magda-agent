"""
Salience Network module for Magda Agent.

Determines what events deserve attention based on urgency, active task relevance,
failing CI/test signals, security risks, emotional/interoceptive pressure, novelty, and uncertainty.
"""

from typing import Dict, Any

class SalienceNetwork:
    """Scores events to determine their salience."""

    def __init__(self) -> None:
        """Initialize SalienceNetwork with weights for different factors."""
        self.weights = {
            "user_urgency": 0.3,
            "active_task_relevance": 0.2,
            "novelty": 0.2,
            "uncertainty": 0.1,
            "is_ci_failure": 0.9,
            "is_security_risk": 0.9,
        }

    def score_event(
        self,
        event_content: str,
        user_urgency: float = 0.0,
        active_task_relevance: float = 0.0,
        is_ci_failure: bool = False,
        is_security_risk: bool = False,
        novelty: float = 0.0,
        uncertainty: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Scores an event's salience.

        Args:
            event_content: The content of the event.
            user_urgency: A value from 0.0 to 1.0 indicating how urgent the user request is.
            active_task_relevance: A value from 0.0 to 1.0 indicating relevance to current tasks.
            is_ci_failure: True if this is a CI failure event.
            is_security_risk: True if this event indicates a security risk.
            novelty: A value from 0.0 to 1.0 indicating how new/surprising the event is.
            uncertainty: A value from 0.0 to 1.0 indicating uncertainty.

        Returns:
            A dictionary containing the calculated 'score' (0.0 to 1.0) and an 'explanation'.
        """
        if is_ci_failure:
            return {"score": 1.0, "explanation": "Critical CI failure requires immediate attention."}

        if is_security_risk:
            return {"score": 1.0, "explanation": "Security risk requires immediate attention."}

        # Handle noisy low-value input (empty or short text with no other signals)
        text_length = len(event_content.strip())
        total_signals = user_urgency + active_task_relevance + novelty + uncertainty
        if text_length < 5 and total_signals < 1e-9:
            return {"score": 0.0, "explanation": "Noisy low-value input."}

        base_score = 0.1 # Base attention for any non-empty input

        score = base_score + (
            (user_urgency * self.weights["user_urgency"]) +
            (active_task_relevance * self.weights["active_task_relevance"]) +
            (novelty * self.weights["novelty"]) +
            (uncertainty * self.weights["uncertainty"])
        )

        score = min(max(score, 0.0), 1.0)

        explanation_parts = [f"Base score: {base_score}"]
        if user_urgency > 0:
            explanation_parts.append(f"User urgency (+{user_urgency * self.weights['user_urgency']:.2f})")
        if active_task_relevance > 0:
            explanation_parts.append(f"Task relevance (+{active_task_relevance * self.weights['active_task_relevance']:.2f})")
        if novelty > 0:
            explanation_parts.append(f"Novelty (+{novelty * self.weights['novelty']:.2f})")
        if uncertainty > 0:
            explanation_parts.append(f"Uncertainty (+{uncertainty * self.weights['uncertainty']:.2f})")

        explanation = ", ".join(explanation_parts) + f". Total: {score:.2f}."

        return {"score": score, "explanation": explanation}
