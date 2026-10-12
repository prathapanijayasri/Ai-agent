import os
from google import genai

class GeminiEmbeddings:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-embedding-2"

    def embed_text(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text
        )
        return response.embeddings[0].values

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=texts
        )
        return [emb.values for emb in response.embeddings]
