import time
from dataclasses import dataclass, field
from typing import List, Optional
from magda_agent.emotions.engine import PADState

@dataclass
class MemoryEntry:
    content: str
    timestamp: float
    importance: float  # 0.0 to 1.0
    emotional_state: PADState
    tags: List[str] = field(default_factory=list)
    id: int = field(default_factory=lambda: int(time.time() * 1000))
    user_id: Optional[int] = None

class WorkingMemory:
    """
    Working Memory: Bounded and non-persistent context for the current task.
    Replaces the short-term storage of the previous MemorySystem.
    """
    def __init__(self, limit: int = 10):
        self.entries: List[MemoryEntry] = []
        self.limit = limit

    def add_memory(self, content: str, importance: float, emotional_state: PADState, tags: List[str] = None, user_id: int = None) -> MemoryEntry:
        """Add a new entry to working memory. If full, removes the oldest/least important."""
        entry = MemoryEntry(
            content=content,
            timestamp=time.time(),
            importance=importance,
            emotional_state=emotional_state,
            tags=tags or [],
            user_id=user_id
        )
        self.entries.append(entry)

        # Enforce boundary
        if len(self.entries) > self.limit:
            self.consolidate()
        return entry

    def consolidate(self):
        """
        Trim the working memory down to its limit.
        Usually happens by dropping less important memories.
        """
        # Simplest trim: keep most recent or most important.
        # We'll keep most recent + most important, but for simplicity:
        # Sort by importance and keep top `limit`. Or just pop oldest.
        # Let's drop the oldest least important.
        if len(self.entries) > self.limit:
            self.entries.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
            self.entries = self.entries[:self.limit]

    def get_summary(self) -> str:
        return f"Working Memory: {len(self.entries)} entries."

    def clear(self):
        """Clear all working memory."""
        self.entries.clear()

    def get_entries(self, user_id: int = None) -> List[MemoryEntry]:
        """Return all entries, optionally filtered by user_id."""
        if user_id is not None:
            return [e for e in self.entries if e.user_id == user_id]
        return self.entries
