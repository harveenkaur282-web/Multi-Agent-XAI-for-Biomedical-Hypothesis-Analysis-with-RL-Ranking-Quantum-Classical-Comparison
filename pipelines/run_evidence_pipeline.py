"""
run_evidence_pipeline.py — Day 2 End-to-End Pipeline

Flow:
  hypothesis
      ↓
  LiteratureAgent  → TF-IDF ranked papers
      ↓
  EvidenceAgent    → extract SUPPORT/CONTRADICT sentences per paper
      ↓
  EvidenceBuilder  → aggregate into EvidenceStore + print verdict

Run from project root:
    python pipelines/run_evidence_pipeline.py
"""

import sys
import os

# Make sure src is on path regardless of where you run from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from agents.literature_agent import LiteratureAgent
from agents.evidence_agent import EvidenceAgent
from evidence_engine.builder import EvidenceBuilder


def run_evidence_pipeline(hypothesis: str, top_k: int = 6) -> dict:
    """
    Full evidence pipeline for a given hypothesis.

    Args:
        hypothesis: Biomedical claim to evaluate.
        top_k: Number of papers to retrieve and analyse.

    Returns:
        EvidenceStore dict with verdict and structured records.
    """
    print("\n" + "=" * 60)
    print("  EVIDENCE PIPELINE — DAY 2")
    print("=" * 60)

    # Stage 1: Literature retrieval + TF-IDF ranking
    lit_agent = LiteratureAgent()
    ranked_papers = lit_agent.run(hypothesis, top_k=top_k)

    if not ranked_papers:
        print("No papers retrieved. Check your data path.")
        return {}

    # Stage 2: Evidence extraction
    ev_agent = EvidenceAgent()
    evidence_records = ev_agent.run(ranked_papers, hypothesis)

    # Stage 3: Build and save store
    builder = EvidenceBuilder()
    store = builder.build(hypothesis, evidence_records)
    builder.save(store)
    builder.print_summary(store)

    return store


if __name__ == "__main__":
    # Test with a clear biomedical hypothesis
    hypothesis = (
        "Neuroinflammation and microglial activation drive amyloid-beta "
        "accumulation and cognitive decline in Alzheimer's disease"
    )

    store = run_evidence_pipeline(hypothesis, top_k=6)

    # Optional: print full JSON output
    import json
    print("\n--- Raw Store (first record) ---")
    if store.get("records"):
        print(json.dumps(store["records"][0], indent=2))