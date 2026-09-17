import faiss
import numpy as np


class SemanticSearch:
    """Lazy-loaded semantic search for resume text.

    The embedding model is intentionally loaded only when semantic search is
    first used. This keeps FastAPI startup independent of Hugging Face model
    download/load time and is especially important for Docker deployments.
    """

    def __init__(self):
        self.model = None
        self.documents = []
        self.index = faiss.IndexFlatL2(384)

    def _ensure_model(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            print("Loading semantic-search embedding model...")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Semantic-search embedding model ready.")

    def add_document(self, document_id, text):
        # Prevent duplicate resumes.
        for document in self.documents:
            if document["id"] == document_id:
                print("Resume already indexed:", document_id)
                return

        self._ensure_model()

        embedding = self.model.encode(
            [text],
            convert_to_numpy=True
        ).astype("float32")

        self.documents.append({
            "id": document_id,
            "text": text
        })

        self.index.add(embedding)

        print("=" * 50)
        print("Resume Added Successfully")
        print("ID:", document_id)
        print("Total Indexed Resumes:", len(self.documents))
        print("=" * 50)

    def search(self, query, top_k=5):
        print("=" * 50)
        print("Searching Resume")
        print("Query:", query)
        print("Indexed Resumes:", len(self.documents))
        print("=" * 50)

        if len(self.documents) == 0:
            print("No resumes available.")
            return []

        self._ensure_model()

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        ).astype("float32")

        k = min(top_k, len(self.documents))

        distances, indices = self.index.search(
            query_embedding,
            k
        )

        print("Indices:", indices)
        print("Distances:", distances)

        results = []

        for distance, index in zip(distances[0], indices[0]):
            if index < len(self.documents):
                results.append({
                    "id": self.documents[index]["id"],
                    "text": self.documents[index]["text"],
                    "distance": float(distance)
                })

        print("Results Found:", len(results))

        return results


semantic_search = SemanticSearch()
