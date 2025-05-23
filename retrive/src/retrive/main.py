#!/usr/bin/env python3
"""
Retrieval QA da Qdrant con **Llama-Index 0.12+** e valutazione
automatica via **Deepeval**.

Esegui:

    uv run -- python -m retrive.main \
        --question "Qual è la missione di OpenAI?"

Se una qualsiasi metrica scende sotto soglia, lo script termina con exit-code 1.
"""

from __future__ import annotations

import argparse
import os
from typing import Dict

# ── Deepeval ─────────────────────────────────────────────────────────
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv

# ── Llama-Index ──────────────────────────────────────────────────────
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# ── Env vars (.env accanto al file) ─────────────────────────────────
load_dotenv()


# --------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Retrieval QA da Qdrant")
    p.add_argument(
        "-q",
        "--question",
        required=True,
        help="Domanda da porre all'indice",
    )
    return p.parse_args()


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
def main() -> None:
    args = parse_args()

    # 1️⃣  Config -------------------------------------------------------
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY mancante in .env")

    embed_model_id = os.getenv("EMBED_MODEL", "text-embedding-3-large")
    llm_model_id = os.getenv("LLM_MODEL", "gpt-4o-mini")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = os.getenv("QDRANT_COLLECTION", "md_embeddings")

    # 2️⃣  Vector store -------------------------------------------------
    client = QdrantClient(url=qdrant_url)
    vector_store = QdrantVectorStore(client=client, collection_name=collection)

    # 3️⃣  Modelli Llama-Index -----------------------------------------
    Settings.embed_model = OpenAIEmbedding(
        model=embed_model_id,
        openai_api_key=openai_key,
    )
    Settings.llm = OpenAI(
        model=llm_model_id,
        api_key=openai_key,
        temperature=0.0,
    )

    # 4️⃣  Indice & Query engine ---------------------------------------
    index = VectorStoreIndex.from_vector_store(vector_store)
    query_engine = index.as_query_engine(similarity_top_k=5, streaming=False)

    # 5️⃣  Esegui la query ---------------------------------------------
    response = query_engine.query(args.question)

    # 6️⃣  Deepeval metrics --------------------------------------------
    metrics = {
        "relevancy": AnswerRelevancyMetric(threshold=0.60),
        "faithfulness": FaithfulnessMetric(threshold=0.50),
    }

    context_docs = [
        src.node.text if hasattr(src, "node") else src.text
        for src in response.source_nodes
    ]

    test_case = LLMTestCase(
        input=args.question,
        actual_output=str(response),
        retrieval_context=context_docs,
    )

    scores: Dict[str, float] = {
        name: metric.measure(test_case) for name, metric in metrics.items()
    }

    # 7️⃣  Output & exit-code ------------------------------------------
    print("\n=== RISPOSTA ===\n")
    print(response, "\n")
    print("=== METRICHE Deepeval ===")
    for name, score in scores.items():
        threshold = metrics[name].threshold  # type: ignore[attr-defined]
        status = "PASS" if score >= threshold else "FAIL"
        print(f"{name.capitalize():12}: {score:.3f}  (≥ {threshold} → {status})")

    if any(score < metrics[n].threshold for n, score in scores.items()):
        raise SystemExit("[✗] Output non soddisfa le metriche minime.")


if __name__ == "__main__":
    main()
