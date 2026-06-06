import chromadb
import uuid
import logging

class EpisodicMemory:
    """
    Episodic Memory: Stores events and experiences.
    Uses ChromaDB for semantic search.
    """
    def __init__(self, persist_directory: str = "./memory_episodic_db"):
        if persist_directory == ":memory:":
            self.client = chromadb.EphemeralClient()
            logging.info("Initialized EpisodicMemory with EphemeralClient")
        else:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logging.info(f"Initialized EpisodicMemory with persistent directory: {persist_directory}")
        self.collection = self.client.get_or_create_collection(name="episodic_memory")

    def store(self, text: str, metadata: dict = None, user_id: int = None) -> None:
        """
        Store an episodic memory (event) with optional metadata.
        """
        try:
            memory_id = str(uuid.uuid4())

            meta = metadata.copy() if metadata else {}
            if user_id is not None:
                meta["user_id"] = user_id

            if meta:
                self.collection.add(
                    documents=[text],
                    metadatas=[meta],
                    ids=[memory_id]
                )
            else:
                self.collection.add(
                    documents=[text],
                    ids=[memory_id]
                )
            logging.debug(f"Stored episodic event: {text[:50]}...")
        except Exception as e:
            logging.error(f"Failed to store episodic event: {e}")

    def recall(self, query: str, top_k: int = 5, user_id: int = None) -> list[str]:
        """
        Recall relevant episodic memories based on the semantic similarity to the query.
        """
        try:
            if self.collection.count() == 0:
                return []

            query_kwargs = {
                "query_texts": [query],
                "n_results": min(top_k, self.collection.count())
            }
            if user_id is not None:
                query_kwargs["where"] = {"user_id": user_id}

            results = self.collection.query(**query_kwargs)
            if results and results.get("documents") and len(results["documents"]) > 0:
                return results["documents"][0]
            return []
        except Exception as e:
            logging.error(f"Failed to recall episodic memories: {e}")
            return []

    def close(self):
        """Clean up the client on shutdown."""
        try:
            self.client.clear_system_cache()
        except Exception:
            pass
