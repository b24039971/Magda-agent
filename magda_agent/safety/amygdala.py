"""
Amygdala (Risk System) module for Magda Agent.

This module is responsible for classifying the risk of file changes and action requests.
It acts as a safeguard before tool execution or auto-merge decisions.
"""

import re
from typing import Literal

RiskLevel = Literal["low", "medium", "high", "critical"]

class RiskSystem:
    """
    Evaluates risks for file changes and proposed actions.
    """

    def __init__(self) -> None:
        """Initialize the RiskSystem."""
        # Precompile regexes for path matching
        self._high_risk_patterns = [
            re.compile(r"^\.github/workflows/.*"),
            re.compile(r"^requirements\.txt$"),
            re.compile(r"^sandbox/.*"),
            re.compile(r"^magda_agent/skills/registry\.py$")
        ]

        self._critical_risk_patterns = [
            re.compile(r"^secrets/.*"),
            re.compile(r"^\.env.*")
        ]

        self._low_risk_patterns = [
            re.compile(r"^docs/.*"),
            re.compile(r".*\.md$")
        ]

    def classify_file_change(self, filepath: str) -> RiskLevel:
        """
        Classifies the risk level of a file change based on its path.

        Args:
            filepath: The path of the file being changed.

        Returns:
            The assessed RiskLevel ("low", "medium", "high", "critical").
        """
        for pattern in self._critical_risk_patterns:
            if pattern.match(filepath):
                return "critical"

        for pattern in self._high_risk_patterns:
            if pattern.match(filepath):
                return "high"

        for pattern in self._low_risk_patterns:
            if pattern.match(filepath):
                return "low"

        # Default to medium risk for general code changes
        return "medium"

    def classify_action(self, action: str, target: str) -> RiskLevel:
        """
        Classifies the risk level of an action against a specific target.

        Args:
            action: The action to be performed (e.g., "edit", "read", "execute").
            target: The target of the action (e.g., a file path or tool name).

        Returns:
            The assessed RiskLevel.
        """
        if action == "read" or action == "inspect":
            return "low"

        if action == "edit" or action == "write":
            return self.classify_file_change(target)

        if action == "execute":
            # Execution defaults to high unless we implement a whitelist
            return "high"

        return "medium"
