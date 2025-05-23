#!/usr/bin/env python3
"""
Ingest a site (crawl ➜ markdown) into a Qdrant collection with **Llama-Index ≥ 0.12**

* No local docstore → all node text remains in Qdrant payload.
* Vector size is **auto-matched** to the embedding model (handles 1536 vs 3072).

Required env vars (.env next to this file)
    OPENAI_API_KEY          – your OpenAI key

Optional env vars (defaults shown)
    EMBED_MODEL             – text-embedding-3-small   # 1536-dim (large = 3072)
    LLM_MODEL               – gpt-4o-mini
    QDRANT_URL              – http://localhost:6333
    QDRANT_COLLECTION       – md_embeddings
    CRAWLER_API_URL         – http://localhost:8000/crawl
    CRAWL_SITE_URL          – https://www.example.com
    CRAWL_DEPTH             – 3
    CRAWL_TIMEOUT           – 30
"""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

# ── Llama-Index imports ─────────────────────────────────────────────
from llama_index.core import Settings  # ← nuovo: sostituisce ServiceContext
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# ─────────────── load .env placed next to this script ───────────────

load_dotenv()  # prints a warning if missing


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────
DIM_MAP: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


def get_embed_dim(model_name: str) -> int:
    """Return known dimension or fallback to 1536."""
    return DIM_MAP.get(model_name, 1536)


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────
def main() -> None:
    # 📌 models from env ------------------------------------------------
    embed_model_name = os.getenv("EMBED_MODEL", "text-embedding-3-large")
    llm_model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # 1️⃣  Connect / create Qdrant collection ---------------------------
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = os.getenv("QDRANT_COLLECTION", "md_embeddings")

    client = QdrantClient(url=qdrant_url)
    expected_dim = get_embed_dim(embed_model_name)

    def current_dim(col: str) -> int | None:
        """Return existing vector size or None if collection missing."""
        try:
            info = client.get_collection(collection_name=col)
            vectors = info.result.config.params.vectors  # type: ignore[attr-defined]
            return vectors[0].size if isinstance(vectors, list) else vectors.size
        except Exception:
            return None

    c_dim = current_dim(collection)
    if c_dim is not None and c_dim != expected_dim:
        print(
            f"[!] Collection '{collection}' dim={c_dim} ≠ expected {expected_dim}. Recreating…"
        )
        client.recreate_collection(
            collection_name=collection,
            vectors_config={"size": expected_dim, "distance": "Cosine"},
        )
    elif c_dim is None:
        client.recreate_collection(
            collection_name=collection,
            vectors_config={"size": expected_dim, "distance": "Cosine"},
        )

    # 2️⃣  Configure Llama-Index (global Settings) ----------------------
    embed_model = OpenAIEmbedding(
        model=embed_model_name,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    llm = OpenAI(
        model=llm_model_name,
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.0,
    )
    node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    Settings.embed_model = embed_model
    Settings.llm = llm
    Settings.node_parser = node_parser

    # 3️⃣  Call crawler API (returns markdown) --------------------------
    crawl_api = os.getenv("CRAWLER_API_URL", "http://localhost:8000/crawl")
    site_url = os.getenv("CRAWL_SITE_URL", "https://www.altermaind.com")
    depth = int(os.getenv("CRAWL_DEPTH", 3))
    timeout = int(os.getenv("CRAWL_TIMEOUT", 30))

    response = requests.post(
        crawl_api,
        json={"url": site_url, "depth": depth, "timeout": timeout},
        timeout=timeout + 5,
    )
    response.raise_for_status()
    md_text = response.text

    # 4️⃣  Build Document ----------------------------------------------
    doc = Document(
        text=md_text,
        doc_id=site_url,
        metadata={"source": site_url, "depth": depth},
    )

    # 5️⃣  Storage context (vector store only) --------------------------
    vector_store = QdrantVectorStore(client=client, collection_name=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 6️⃣  Index + upsert ----------------------------------------------
    VectorStoreIndex.from_documents([doc], storage_context=storage_context)

    print(
        f"[✓] Ingest completed: {site_url} → {collection} "
        f"(dim={expected_dim}, model={embed_model_name})"
    )


if __name__ == "__main__":
    main()
