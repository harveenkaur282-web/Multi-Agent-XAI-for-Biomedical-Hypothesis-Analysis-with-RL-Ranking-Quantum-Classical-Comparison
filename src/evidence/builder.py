"""
EvidenceBuilder — Day 2
Takes raw evidence records from EvidenceAgent and builds a structured
EvidenceStore: a dict keyed by paper_id with aggregated stats.

This is what later modules (ReasoningAgent, HypothesisScorer) will consume.
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime


class EvidenceBuilder:
    """
    Assembles evidence records into a queryable EvidenceStore.

    Structure of the store:
    {
        "hypothesis": str,
        "created_at": ISO timestamp,
        "summary": {
            "total_papers": int,
            "supporting": int,
            "contradicting": int,
            "neutral": int,
            "overall_verdict": "SUPPORTED" | "CONTRADICTED" | "INCONCLUSIVE"
        },
        "records": [ EvidenceRecord, ... ]  # sorted by relevance
    }
    """

    def __init__(self, store_path: str = None):
        self.store_path = store_path or os.path.join(
            os.path.dirname(__file__), "../../data/evidence_store/evidence_store.json"
        )

    def build(
        self,
        hypothesis: str,
        evidence_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build an EvidenceStore from a list of evidence records.

        Args:
            hypothesis: The hypothesis being evaluated.
            evidence_records: Output from EvidenceAgent.run()

        Returns:
            Structured EvidenceStore dict.
        """
        supporting = [r for r in evidence_records if r["overall_stance"] == "SUPPORT"]
        contradicting = [r for r in evidence_records if r["overall_stance"] == "CONTRADICT"]
        neutral = [r for r in evidence_records if r["overall_stance"] == "NEUTRAL"]

        # Verdict logic: simple majority vote
        if len(supporting) > len(contradicting) and len(supporting) > len(neutral):
            verdict = "SUPPORTED"
        elif len(contradicting) > len(supporting):
            verdict = "CONTRADICTED"
        else:
            verdict = "INCONCLUSIVE"

        store = {
            "hypothesis": hypothesis,
            "created_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_papers": len(evidence_records),
                "supporting": len(supporting),
                "contradicting": len(contradicting),
                "neutral": len(neutral),
                "overall_verdict": verdict,
            },
            "records": sorted(
                evidence_records,
                key=lambda x: x["relevance_score"],
                reverse=True,
            ),
        }
        return store

    def save(self, store: Dict[str, Any]) -> None:
        """Persist evidence store to JSON."""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump(store, f, indent=2)
        print(f"[EvidenceBuilder] Store saved → {self.store_path}")

    def load(self) -> Dict[str, Any]:
        """Load a previously saved evidence store."""
        if not os.path.exists(self.store_path):
            return {}
        with open(self.store_path, "r") as f:
            return json.load(f)

    def print_summary(self, store: Dict[str, Any]) -> None:
        """Pretty-print the evidence store summary."""
        s = store.get("summary", {})
        print("\n" + "=" * 60)
        print(f"  HYPOTHESIS: {store['hypothesis']}")
        print(f"  VERDICT:    {s.get('overall_verdict', 'N/A')}")
        print(f"  Papers:     {s.get('total_papers', 0)} total")
        print(f"  ✅ Support:  {s.get('supporting', 0)}")
        print(f"  ❌ Contradict: {s.get('contradicting', 0)}")
        print(f"  ⚪ Neutral:  {s.get('neutral', 0)}")
        print("=" * 60)

        # Show top supporting sentences across all papers
        all_support_sents = []
        for rec in store.get("records", []):
            for sent_obj in rec.get("evidence_sentences", []):
                if sent_obj["label"] == "SUPPORT":
                    all_support_sents.append({
                        "title": rec["title"],
                        "sentence": sent_obj["sentence"],
                        "relevance": sent_obj["relevance"],
                    })

        all_support_sents.sort(key=lambda x: x["relevance"], reverse=True)

        if all_support_sents:
            print("\n  📌 Top supporting sentences:")
            for item in all_support_sents[:3]:
                print(f"    [{item['title'][:40]}...]")
                print(f"    → {item['sentence'][:120]}")