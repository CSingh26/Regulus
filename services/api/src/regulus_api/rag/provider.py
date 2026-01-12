from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from openai import OpenAI
from sentence_transformers import SentenceTransformer

from regulus_api.core.config import get_settings

EMBEDDING_DIM = 1536


class EmbeddingProvider(Protocol):
    name: str
    model: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class OpenAIEmbeddingProvider:
    name = "openai"
    model = "text-embedding-3-small"
    dim = EMBEDDING_DIM

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class LocalEmbeddingProvider:
    name = "local"
    model = "all-MiniLM-L6-v2"
    dim = EMBEDDING_DIM

    def __init__(self) -> None:
        self._model = get_local_model()

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        results: list[list[float]] = []
        for vector in vectors:
            padded = list(vector)
            if len(padded) < EMBEDDING_DIM:
                padded.extend([0.0] * (EMBEDDING_DIM - len(padded)))
            results.append(padded[:EMBEDDING_DIM])
        return results


@lru_cache
def get_local_model() -> SentenceTransformer:
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIEmbeddingProvider(settings.openai_api_key)
    return LocalEmbeddingProvider()
