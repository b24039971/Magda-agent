import logging
import uuid
import chromadb
from typing import Optional, Dict
from collections import Counter

class ProceduralMemory:
    """
    Procedural Memory: Stores reusable successful procedures and methods (skills/habits).
    Analyzes patterns to find which skills are frequently used for typical requests
    and receive high evaluation scores.
    """

    def __init__(self, persist_directory: str = "./memory_procedural_db") -> None:
        """
        Initializes the ProceduralMemory with a ChromaDB client.

        Args:
            persist_directory (str): The directory to persist ChromaDB data.
                                     Use ":memory:" for an ephemeral client.
        """
        if persist_directory == ":memory:":
            self.client = chromadb.EphemeralClient()
            logging.info("Initialized ProceduralMemory with EphemeralClient")
        else:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logging.info(f"Initialized ProceduralMemory with persistent directory: {persist_directory}")

        self.collection = self.client.get_or_create_collection(name="procedural_memory")

    def record_usage(self, input_text: str, skill_used: str, evaluation_score: float, user_id: int = None) -> None:
        """
        Records the successful usage of a skill for a given input.

        Args:
            input_text (str): The user's input.
            skill_used (str): The name of the skill that was used.
            evaluation_score (float): The evaluation score of the response.
            user_id (int, optional): The ID of the user.
        """
        # We only form habits from successful responses
        if evaluation_score >= 8.0:
            try:
                habit_id = str(uuid.uuid4())
                metadata = {"skill_used": skill_used}
                if user_id is not None:
                    metadata["user_id"] = user_id
                self.collection.add(
                    documents=[input_text],
                    metadatas=[metadata],
                    ids=[habit_id]
                )
                logging.info(f"Procedural memory reinforced: Stored success for skill '{skill_used}' with input '{input_text[:20]}...'")
            except Exception as e:
                logging.error(f"Failed to record procedural memory: {e}")

    def suggest_strategy(self, input_text: str, user_id: int = None) -> Optional[str]:
        """
        Suggests a preferred skill based on past high-scoring experiences for similar inputs.

        Args:
            input_text (str): The user's input to find a strategy for.
            user_id (int, optional): The ID of the user.

        Returns:
            Optional[str]: The name of the suggested skill, or None if no strong habit exists.
        """
        try:
            if self.collection.count() == 0:
                return None

            query_kwargs = {
                "query_texts": [input_text],
                "n_results": min(5, self.collection.count())
            }
            if user_id is not None:
                query_kwargs["where"] = {"user_id": user_id}

            results = self.collection.query(**query_kwargs)

            if not results or not results.get("distances") or not results["distances"][0]:
                return None

            distances = results["distances"][0]
            metadatas = results["metadatas"][0]

            valid_skills = []
            distance_threshold = 1.0

            for dist, meta in zip(distances, metadatas):
                if dist < distance_threshold and meta and "skill_used" in meta:
                    valid_skills.append(meta["skill_used"])

            if not valid_skills:
                return None

            skill_counts = Counter(valid_skills)
            best_skill, max_count = skill_counts.most_common(1)[0]

            if max_count >= 2:
                logging.info(f"Procedural memory matched: Suggesting skill '{best_skill}' for input '{input_text[:20]}...'")
                return best_skill

            return None
        except Exception as e:
            logging.error(f"Failed to suggest strategy: {e}")
            return None

    def close(self):
        """Clean up the client on shutdown."""
        try:
            self.client.clear_system_cache()
        except Exception:
            pass
