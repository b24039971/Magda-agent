from typing import List, Dict, Any, Optional

class GlobalWorkspace:
    """
    Global Workspace for the Magda Agent.
    Collects candidate events from various subsystems, selects the one with the highest salience
    to be the focused event, and suppresses the others for later processing or debugging.
    """
    def __init__(self):
        self.candidates: List[Dict[str, Any]] = []
        self.focused_event: Optional[Dict[str, Any]] = None
        self.suppressed_candidates: List[Dict[str, Any]] = []

    def add_candidate(self, candidate: Dict[str, Any]) -> None:
        """
        Add a candidate event to the workspace.
        A candidate should ideally have a 'source', 'content', and 'salience' score.
        """
        if 'salience' not in candidate:
            candidate['salience'] = 0.0
        self.candidates.append(candidate)

    def select_focus(self) -> Optional[Dict[str, Any]]:
        """
        Selects the candidate with the highest salience score as the focused event.
        The other candidates are moved to suppressed_candidates.
        Returns the focused event.
        """
        if not self.candidates:
            return None

        # Sort candidates by salience descending
        self.candidates.sort(key=lambda x: x.get('salience', 0.0), reverse=True)

        self.focused_event = self.candidates[0]
        self.suppressed_candidates = self.candidates[1:]

        # Clear candidates for the next selection cycle
        self.candidates = []

        return self.focused_event

    def clear(self) -> None:
        """Clears the workspace of all candidates and focus state."""
        self.candidates = []
        self.focused_event = None
        self.suppressed_candidates = []
