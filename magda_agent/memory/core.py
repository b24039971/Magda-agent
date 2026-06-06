from typing import List, Optional
import logging
from magda_agent.emotions.engine import PADState
from magda_agent.memory.working import WorkingMemory, MemoryEntry
from magda_agent.memory.episodic import EpisodicMemory
from magda_agent.memory.semantic import SemanticMemory
from magda_agent.memory.procedural import ProceduralMemory

class MemorySystem:
    """
    Facade for the new split memory layers.
    Maintains compatibility with the old MemorySystem API while delegating
    to WorkingMemory, EpisodicMemory, SemanticMemory, and ProceduralMemory.
    """
    def __init__(self, short_term_limit: int = 10, persist_directory: str = ":memory:"):
        self.working = WorkingMemory(limit=short_term_limit)
        self.episodic = EpisodicMemory(persist_directory=persist_directory)
        self.semantic = SemanticMemory(persist_directory=persist_directory)
        self.procedural = ProceduralMemory(persist_directory=persist_directory)

        # Backward compatibility properties
        self.short_term = self.working.entries
        self.long_term = [] # We no longer maintain a single long_term list, but provide it to avoid breaks.

    def add_memory(self, content: str, importance: float, emotional_state: PADState, tags: List[str] = None, user_id: int = None):
        """Adds a memory to working memory. If important enough, it could be moved to episodic/semantic."""
        # Add to bounded working memory
        entry = self.working.add_memory(content, importance, emotional_state, tags, user_id)

        # If it's highly important, store it in episodic memory as well
        if importance > 0.3:
            meta = {"importance": importance}
            if tags:
                meta["tags"] = ",".join(tags)
            self.episodic.store(content, metadata=meta, user_id=user_id)

            # Temporary back-compat
            self.long_term.append(entry)

    def retrieve_relevant(self, query: str, limit: int = 5, user_id: int = None) -> List[MemoryEntry]:
        """
        Retrieves relevant memories. To maintain backward compatibility,
        this returns MemoryEntry objects reconstructed from episodic memory.
        """
        # For full search, we check episodic memory.
        results = self.episodic.recall(query, top_k=limit, user_id=user_id)

        # Results from episodic recall is a list of strings
        entries = []
        for res in results:
            entries.append(MemoryEntry(
                content=res,
                timestamp=0.0,
                importance=1.0,
                emotional_state=PADState(0.0,0.0,0.0),
                user_id=user_id
            ))
        return entries

    def get_summary(self) -> str:
        return self.working.get_summary()

    def close(self):
        """Clean up clients on shutdown."""
        self.episodic.close()
        self.semantic.close()
        self.procedural.close()
        logging.info("MemorySystem components gracefully closed.")
