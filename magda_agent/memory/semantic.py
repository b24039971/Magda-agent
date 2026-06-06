import chromadb
import uuid
import logging

class SemanticMemory:
    """
    Semantic Memory: Stores stable knowledge, facts, and concepts about the project or user.
    Uses ChromaDB for semantic search.
    """
    def __init__(self, persist_directory: str = "./memory_semantic_db"):
        if persist_directory == ":memory:":
            self.client = chromadb.EphemeralClient()
            logging.info("Initialized SemanticMemory with EphemeralClient")
        else:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logging.info(f"Initialized SemanticMemory with persistent directory: {persist_directory}")
        self.collection = self.client.get_or_create_collection(name="semantic_memory")

    def store(self, text: str, metadata: dict = None, user_id: int = None) -> None:
        """
        Store a semantic memory (fact) with optional metadata.
        """
        try:
            memory_id = str(uuid.uuid4())

            meta = metadata.copy() if metadata else {}
            if user_id is not None:
                meta["user_id"] = user_id

            kwargs = {
                "documents": [text],
                "ids": [memory_id]
            }
            if meta:
                kwargs["metadatas"] = [meta]
            self.collection.add(**kwargs)
            logging.debug(f"Stored semantic fact: {text[:50]}...")
        except Exception as e:
            logging.error(f"Failed to store semantic fact: {e}")

    def recall(self, query: str, top_k: int = 5, user_id: int = None) -> list[str]:
        """
        Recall relevant semantic memories based on the semantic similarity to the query.
        """
        try:
            if self.collection.count() == 0:
                return []

            kwargs = {
                "query_texts": [query],
                "n_results": min(top_k, self.collection.count())
            }
            if user_id is not None:
                kwargs["where"] = {"user_id": user_id}

            results = self.collection.query(**kwargs)
            if results and results.get("documents") and len(results["documents"]) > 0:
                return results["documents"][0]
            return []
        except Exception as e:
            logging.error(f"Failed to recall semantic memories: {e}")
            return []

    def close(self):
        """Clean up the client on shutdown."""
        try:
            self.client.clear_system_cache()
        except Exception:
            pass
