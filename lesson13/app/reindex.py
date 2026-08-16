"""Exercise 2 — reindex Meridian's carrier-contract corpus at a new chunk size.

The ARM template pre-provisioned `contracts-v3` (chunk_size=512). This module
rebuilds the corpus with a different chunk_size + 15% overlap into a new index
named `contracts-v3-<size>` so the evaluate step can compare groundedness
side-by-side.

Usage:
    python -m app.reindex 256
    python -m app.reindex 1024
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    VectorSearch,
    VectorSearchProfile,
)

from azure.ai.projects import AIProjectClient

from app.config import load

_CRED = DefaultAzureCredential()
_SETTINGS = load()

EMBED_DIMS = 3072  # text-embedding-3-large

# Meridian's carrier-contract corpus (kept small so the lab runs fast). In a
# production pipeline this would stream from a blob container.
CORPUS = [
    ("MSA-Cascadia-2025", """Master Services Agreement between Meridian Freight & Analytics ("Shipper") and Cascadia Regional Logistics ("Carrier") effective 2025-03-01. Section 1.1 — Scope: Carrier will provide dry-van and reefer capacity across the Pacific Northwest lane cluster (Seattle, Portland, Boise). Section 2.3 — Rate Table: Base linehaul $2.15 per mile, fuel surcharge indexed weekly to DOE #2 diesel. Section 4.2 — Detention: $75 per hour after 2 free hours, capped at $600 per stop. Section 6.1 — Indemnity: Each party indemnifies the other for third-party claims arising from its own negligence, cap of $2,000,000 per occurrence. Section 8.4 — Termination: Either party may terminate for cause on 30 days' written notice; convenience termination on 90 days."""),
    ("MSA-Nordfjord-2024", """Master Services Agreement between Meridian Freight & Analytics ("Shipper") and Nordfjord Intermodal ("Carrier") effective 2024-11-15. Section 1.1 — Scope: Intermodal container capacity between Long Beach, Chicago, and Kansas City. Section 2.3 — Rate Table: Container rate $1,850 per 40' ISO plus IPI drayage at published tariff. Section 3.7 — Free time: 48 hours at origin ramp, 72 hours at destination ramp. Section 4.2 — Storage: $95 per container per day after free time expires. Section 6.1 — Indemnity: Mutual, per-occurrence cap $5,000,000. Section 8.4 — Termination: 60 days' notice either party; auto-renews annually unless notice served 90 days before renewal."""),
    ("SOW-Auberdine-2025", """Statement of Work between Meridian Freight & Analytics and Auberdine Cold Chain, effective 2025-06-01. Section 1.1 — Scope: Temperature-controlled LTL for pharmaceutical shipments, 2-8°C. Section 2.3 — Rate Table: $0.42 per pound plus $180 minimum stop charge. Section 4.2 — Temperature deviation: Full-shipment refund on any deviation exceeding 1.5°C for more than 30 minutes documented by GPS-linked probe. Section 5.6 — Chain of custody: Signed BOL and photograph at every pickup and delivery. Section 6.1 — Indemnity: Carrier indemnifies Shipper for cargo loss up to invoice value plus $50,000 in spoilage costs. Section 8.4 — Termination: 45 days for cause, 90 days for convenience."""),
    ("MSA-Redwood-2024", """Master Services Agreement between Meridian Freight & Analytics and Redwood Cartage Group, effective 2024-01-10. Section 1.1 — Scope: Regional dry-van capacity in Northern California. Section 2.3 — Rate Table: Base linehaul $2.05 per mile, no fuel surcharge (fixed all-in). Section 4.2 — Detention: $65 per hour after 2 free hours. Section 4.7 — Layover: $250 per 24-hour layover, capped at 3 consecutive layovers per trip. Section 6.1 — Indemnity: Mutual, $1,000,000 cap. Section 8.4 — Termination: 30 days for cause, 60 days for convenience. Section 9.2 — Insurance: Carrier maintains $1M auto liability, $100K cargo, $1M general liability, all naming Meridian as additional insured."""),
    ("MSA-Kestrel-2025", """Master Services Agreement between Meridian Freight & Analytics and Kestrel Expedited effective 2025-02-20. Section 1.1 — Scope: Same-day and next-day expedited nationwide, cargo van + straight truck. Section 2.3 — Rate Table: Tiered — $1.85/mi (van), $2.60/mi (straight truck), plus $150 dispatch fee. Section 4.2 — Detention: $90/hour after 1 free hour; expedited premium. Section 4.5 — Cancellation: 100% cancellation fee if load cancelled after driver dispatched. Section 6.1 — Indemnity: Carrier's cargo liability capped at $100,000 unless declared higher value. Section 8.4 — Termination: 30 days either party; no cause required."""),
]


def _chunk(text: str, size: int, overlap_pct: int = 15) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= size:
        return [text]
    overlap = max(1, int(size * overlap_pct / 100))
    step = max(1, size - overlap)
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start += step
    return chunks


def _embed_batch(texts: list[str]) -> list[list[float]]:
    with AIProjectClient(endpoint=_SETTINGS.project_endpoint, credential=_CRED) as project:
        with project.get_openai_client() as client:
            resp = client.embeddings.create(
                model=_SETTINGS.embedding_deployment,
                input=texts,
            )
    return [item.embedding for item in resp.data]


def _make_index(name: str) -> SearchIndex:
    return SearchIndex(
        name=name,
        fields=[
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True, searchable=True),
            SearchField(name="chunk", type=SearchFieldDataType.String, searchable=True),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                vector_search_dimensions=EMBED_DIMS,
                vector_search_profile_name="default",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
            profiles=[VectorSearchProfile(name="default", algorithm_configuration_name="default-hnsw")],
        ),
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        content_fields=[SemanticField(field_name="chunk")],
                        title_field=SemanticField(field_name="source"),
                    ),
                )
            ]
        ),
    )


def reindex(chunk_size: int) -> str:
    index_name = f"{_SETTINGS.search_index}-{chunk_size}"
    idx_client = SearchIndexClient(endpoint=_SETTINGS.search_endpoint, credential=_CRED)
    idx_client.create_or_update_index(_make_index(index_name))

    docs = []
    doc_id = 0
    for source, text in CORPUS:
        chunks = _chunk(text, chunk_size)
        vectors = _embed_batch(chunks)
        for chunk, vector in zip(chunks, vectors):
            docs.append({
                "id": f"{source}-{doc_id}",
                "source": source,
                "chunk": chunk,
                "embedding": vector,
            })
            doc_id += 1

    with SearchClient(endpoint=_SETTINGS.search_endpoint, index_name=index_name, credential=_CRED) as client:
        client.upload_documents(documents=docs)

    print(json.dumps({"index": index_name, "documents": len(docs), "chunk_size": chunk_size}, indent=2))
    return index_name


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m app.reindex <chunk_size>")
        sys.exit(1)
    reindex(int(sys.argv[1]))
