#!/usr/bin/env python3
"""Benchmark embedding models for Hebbian memory — multilingual comparison.

Compares latency, throughput, and embedding quality across recommended models
for English and French text. Useful for choosing the right memory.model.

Usage:
    python benchmarks/model_benchmark.py
    python benchmarks/model_benchmark.py --models all-MiniLM-L6-v2 BAAI/bge-m3

⚠️ Contenu généré par IA — validation humaine requise avant utilisation.
"""

from __future__ import annotations

import argparse
import statistics
import time
from typing import Any

# Sample texts for benchmarking (English + French)
SAMPLE_TEXTS = {
    "en": [
        "Always run unit tests before pushing to the main branch",
        "The deployment pipeline requires Docker and a valid API key",
        "Hebbian memory strengthens connections between co-activated concepts",
        "Use environment variables for secrets, never hardcode them",
        "The security audit found 3 critical vulnerabilities in the gateway",
    ],
    "fr": [
        "Toujours exécuter les tests unitaires avant de pousser sur la branche main",
        "Le pipeline de déploiement nécessite Docker et une clé API valide",
        "La mémoire hebbienne renforce les connexions entre concepts co-activés",
        "Utiliser des variables d'environnement pour les secrets, ne jamais les coder en dur",
        "L'audit de sécurité a trouvé 3 vulnérabilités critiques dans la gateway",
    ],
}

# Cross-lingual pairs (EN → FR) for similarity check
CROSS_LINGUAL_PAIRS = [
    ("Always run tests before deploying", "Toujours exécuter les tests avant le déploiement"),
    ("The API key must be kept secret", "La clé API doit rester secrète"),
    ("Memory weights are updated after each session", "Les poids mémoire sont mis à jour après chaque session"),
]

DEFAULT_MODELS = [
    "all-MiniLM-L6-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def benchmark_model(model_name: str) -> dict[str, Any]:
    """Benchmark a single embedding model."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return {"model": model_name, "error": "pip install sentence-transformers"}

    print(f"\n{'='*60}")
    print(f"  Model: {model_name}")
    print(f"{'='*60}")

    # Load model (measure load time)
    t0 = time.perf_counter()
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        return {"model": model_name, "error": str(e)}
    load_time = time.perf_counter() - t0
    print(f"  Load time: {load_time:.2f}s")

    dim = model.get_sentence_embedding_dimension()
    print(f"  Dimensions: {dim}")

    results: dict[str, Any] = {
        "model": model_name,
        "dimensions": dim,
        "load_time_s": round(load_time, 3),
    }

    # Encoding speed (English)
    all_texts = SAMPLE_TEXTS["en"] + SAMPLE_TEXTS["fr"]
    times = []
    for _ in range(3):  # 3 runs
        t0 = time.perf_counter()
        model.encode(all_texts)
        times.append(time.perf_counter() - t0)

    avg_time = statistics.mean(times)
    throughput = len(all_texts) / avg_time
    print(f"  Encode {len(all_texts)} texts: {avg_time:.3f}s ({throughput:.0f} texts/s)")
    results["encode_time_s"] = round(avg_time, 4)
    results["throughput_texts_per_s"] = round(throughput, 1)

    # Intra-language similarity (EN)
    en_embs = model.encode(SAMPLE_TEXTS["en"])
    en_sims = []
    for i in range(len(en_embs)):
        for j in range(i + 1, len(en_embs)):
            en_sims.append(_cosine_similarity(en_embs[i].tolist(), en_embs[j].tolist()))
    results["en_avg_similarity"] = round(statistics.mean(en_sims), 4)

    # Intra-language similarity (FR)
    fr_embs = model.encode(SAMPLE_TEXTS["fr"])
    fr_sims = []
    for i in range(len(fr_embs)):
        for j in range(i + 1, len(fr_embs)):
            fr_sims.append(_cosine_similarity(fr_embs[i].tolist(), fr_embs[j].tolist()))
    results["fr_avg_similarity"] = round(statistics.mean(fr_sims), 4)

    # Cross-lingual alignment
    cross_sims = []
    for en_text, fr_text in CROSS_LINGUAL_PAIRS:
        en_emb = model.encode([en_text])[0]
        fr_emb = model.encode([fr_text])[0]
        cross_sims.append(_cosine_similarity(en_emb.tolist(), fr_emb.tolist()))
    results["cross_lingual_similarity"] = round(statistics.mean(cross_sims), 4)

    print(f"  EN intra-similarity: {results['en_avg_similarity']:.4f}")
    print(f"  FR intra-similarity: {results['fr_avg_similarity']:.4f}")
    print(f"  Cross-lingual (EN↔FR): {results['cross_lingual_similarity']:.4f}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark embedding models for firm-ecosystem")
    parser.add_argument(
        "--models", nargs="+", default=DEFAULT_MODELS,
        help="Model names to benchmark (default: MiniLM-L6 + multilingual-MiniLM-L12)",
    )
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════╗")
    print("║  Firm Ecosystem — Embedding Model Benchmark     ║")
    print("╚══════════════════════════════════════════════════╝")

    results = []
    for model_name in args.models:
        result = benchmark_model(model_name)
        results.append(result)

    # Summary table
    print(f"\n{'='*80}")
    print("  SUMMARY")
    print(f"{'='*80}")
    print(f"  {'Model':<45} {'Dim':>5} {'Speed':>8} {'EN':>6} {'FR':>6} {'EN↔FR':>7}")
    print(f"  {'-'*45} {'-'*5} {'-'*8} {'-'*6} {'-'*6} {'-'*7}")
    for r in results:
        if "error" in r:
            print(f"  {r['model']:<45} ERROR: {r['error']}")
            continue
        print(
            f"  {r['model']:<45} {r['dimensions']:>5} "
            f"{r['throughput_texts_per_s']:>6.0f}/s "
            f"{r['en_avg_similarity']:>6.4f} "
            f"{r['fr_avg_similarity']:>6.4f} "
            f"{r['cross_lingual_similarity']:>7.4f}"
        )

    # Recommendation
    valid = [r for r in results if "error" not in r]
    if valid:
        best_cross = max(valid, key=lambda r: r["cross_lingual_similarity"])
        best_speed = max(valid, key=lambda r: r["throughput_texts_per_s"])
        print(f"\n  Best cross-lingual: {best_cross['model']} ({best_cross['cross_lingual_similarity']:.4f})")
        print(f"  Fastest:            {best_speed['model']} ({best_speed['throughput_texts_per_s']:.0f} texts/s)")
        print(f"\n  Set model: firm config set memory.model {best_cross['model']}")


if __name__ == "__main__":
    main()
