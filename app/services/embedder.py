from openai import OpenAI
from app.config import settings
from typing import List

class Embedder:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Converts a list of strings into a list of 1536-dimensional vectors.
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise ValueError(f"OpenAI Embedding failed: {str(e)}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Converts a single string into a vector.
        """
        return self.generate_embeddings([text])[0]

embedder = Embedder()
