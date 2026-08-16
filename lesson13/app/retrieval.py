"""Azure AI Search retrieval helpers for Meridian's contracts index.

Three retrieval strategies are exposed so the exercises can toggle between
them and compare groundedness scores. Every helper returns a list of
`{id, source, chunk, score}` dicts ordered by score.
"""
from __future__ import annotations

from typing import Iterable

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryType,
    VectorizedQuery,
)

from azure.ai.projects import AIProjectClient

from app.config import load

_CRED = DefaultAzureCredential()
_SETTINGS = load()


def _client(index_name: str | None = None) -> SearchClient:
    return SearchClient(
        endpoint=_SETTINGS.search_endpoint,
        index_name=index_name or _SETTINGS.search_index,
        credential=_CRED,
    )


def embed(text: str) -> list[float]:
    """Embed a single query string via the Foundry project's OpenAI client."""
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            resp = client.embeddings.create(
                model=_SETTINGS.embedding_deployment,
                input=[text],
            )
    return resp.data[0].embedding


def search_vector(query: str, top_k: int = 5, index: str | None = None) -> list[dict]:
    """Pure vector search — top_k by cosine similarity on the embedding field."""
    vector = embed(query)
    vq = VectorizedQuery(vector=vector, k_nearest_neighbors=top_k, fields="embedding")
    with _client(index) as client:
        results = client.search(
            search_text=None,
            vector_queries=[vq],
            select=["id", "source", "chunk"],
            top=top_k,
        )
        return [
            {"id": r["id"], "source": r["source"], "chunk": r["chunk"], "score": r["@search.score"]}
            for r in results
        ]


def search_hybrid(query: str, top_k: int = 5, index: str | None = None) -> list[dict]:
    """Hybrid — BM25 keyword + vector, merged via RRF. No semantic ranker."""
    vector = embed(query)
    # Semantic ranker docs recommend k=50 vector matches feeding L2; we give it
    # top_k*10 so the RRF stage has meaningful input for small indexes too.
    vq = VectorizedQuery(vector=vector, k_nearest_neighbors=50, fields="embedding")
    with _client(index) as client:
        results = client.search(
            search_text=query,
            vector_queries=[vq],
            select=["id", "source", "chunk"],
            top=top_k,
        )
        return [
            {"id": r["id"], "source": r["source"], "chunk": r["chunk"], "score": r["@search.score"]}
            for r in results
        ]


def search_semantic_hybrid(query: str, top_k: int = 5, index: str | None = None) -> list[dict]:
    """Hybrid + semantic ranker L2 reranking. Requires `default` semantic config."""
    vector = embed(query)
    vq = VectorizedQuery(vector=vector, k_nearest_neighbors=50, fields="embedding")
    with _client(index) as client:
        results = client.search(
            search_text=query,
            vector_queries=[vq],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="default",
            select=["id", "source", "chunk"],
            top=top_k,
        )
        hits = []
        for r in results:
            hits.append({
                "id": r["id"],
                "source": r["source"],
                "chunk": r["chunk"],
                # Semantic reranker score appears when queryType=semantic
                "score": r.get("@search.reranker_score") or r["@search.score"],
            })
        return hits
