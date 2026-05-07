#heuristic evidence extraction

import re
from typing import List, Dict, Any

SUPPORT_CUES = [
    "show", "shows", "showed", "demonstrate", "demonstrates", "demonstrated",
    "confirm", "confirms", "confirmed", "support", "supports", "supported",
    "evidence", "suggest", "suggests", "suggested", "indicate", "indicates",
    "found", "find", "reveal", "reveals", "revealed", "consistent with",
    "associated with", "significantly increased", "significantly decreased",
    "significantly improved", "beneficial", "effective", "efficacious",
    "positive", "upregulated", "downregulated",
]

CONTRADICT_CUES = [
    "no significant", "not significant", "failed to", "did not", "does not",
    "no evidence", "contradict", "contradicts", "contradicted", "refute",
    "refutes", "refuted", "inconsistent", "no association", "no effect",
    "not associated", "null result", "negative result", "no difference",
    "no improvement", "no benefit", "ineffective", "no correlation",
]

HEDGE_CUES = [
    "may", "might", "could", "possibly", "potentially", "unclear",
    "uncertain", "unknown", "further study", "future work", "warrants",
    "limited", "preliminary",
]


class EvidenceAgent:
    """
    Extracts evidence sentences from paper abstracts.

    For each ranked paper, it:
      1. Splits the abstract into sentences.
      2. Classifies each sentence as SUPPORT / CONTRADICT / NEUTRAL.
      3. Returns a structured EvidenceRecord.

    Day 2: heuristic lexicon-based classification.
    Day 5+: replace/augment with transformer-based NLI (zero-shot).
    """

    def __init__(self, min_sentence_length: int = 20):
        """
        Args:
            min_sentence_length: Skip very short sentences (e.g. "Results.")
        """
        self.min_sentence_length = min_sentence_length

    def _split_sentences(self, text: str) -> List[str]:
        """Basic sentence splitter. Good enough for structured abstracts."""
        # Split on period/exclamation/question followed by space+capital
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
        return [s.strip() for s in sentences if len(s.strip()) >= self.min_sentence_length]

    def _classify_sentence(self, sentence: str) -> str:
        """
        Returns 'SUPPORT', 'CONTRADICT', or 'NEUTRAL'.
        Contradiction cues take priority over support cues.
        """
        lower = sentence.lower()

        # Count cue hits
        contradict_hits = sum(1 for cue in CONTRADICT_CUES if cue in lower)
        support_hits = sum(1 for cue in SUPPORT_CUES if cue in lower)
        hedge_hits = sum(1 for cue in HEDGE_CUES if cue in lower)

        if contradict_hits > 0:
            return "CONTRADICT"
        if support_hits > 0:
            # Downgrade to NEUTRAL if heavily hedged
            if hedge_hits >= 2:
                return "NEUTRAL"
            return "SUPPORT"
        return "NEUTRAL"

    def _score_sentence_relevance(self, sentence: str, hypothesis: str) -> float:
        """
        Simple word overlap score between sentence and hypothesis.
        Range: 0.0 - 1.0. Used to filter low-relevance sentences.
        """
        hyp_words = set(hypothesis.lower().split())
        sent_words = set(sentence.lower().split())
        # Remove very short words (stop-word-like)
        hyp_words = {w for w in hyp_words if len(w) > 3}
        sent_words = {w for w in sent_words if len(w) > 3}
        if not hyp_words:
            return 0.0
        overlap = hyp_words & sent_words
        return len(overlap) / len(hyp_words)

    # ------------------------------------------------------------------
    # Core extraction
    # ------------------------------------------------------------------

    def extract_evidence(
        self,
        paper: Dict[str, Any],
        hypothesis: str,
        min_relevance: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Extract structured evidence from a single paper.

        Args:
            paper: Paper dict with at least 'abstract', 'title', 'paper_id'.
            hypothesis: The hypothesis being evaluated.
            min_relevance: Minimum word overlap to include a sentence.

        Returns:
            EvidenceRecord dict.
        """
        abstract = paper.get("abstract", "")
        sentences = self._split_sentences(abstract)

        evidence_sentences = []
        support_count = 0
        contradict_count = 0

        for sent in sentences:
            relevance = self._score_sentence_relevance(sent, hypothesis)
            if relevance < min_relevance:
                continue  # skip completely off-topic sentences

            label = self._classify_sentence(sent)
            if label == "SUPPORT":
                support_count += 1
            elif label == "CONTRADICT":
                contradict_count += 1

            evidence_sentences.append({
                "sentence": sent,
                "label": label,
                "relevance": round(relevance, 3),
            })

        # Overall stance: whichever has more hits wins; tie → NEUTRAL
        if support_count > contradict_count:
            overall_stance = "SUPPORT"
        elif contradict_count > support_count:
            overall_stance = "CONTRADICT"
        else:
            overall_stance = "NEUTRAL"

        return {
            "paper_id": paper.get("paper_id", paper.get("id", "unknown")),
            "title": paper.get("title", ""),
            "relevance_score": paper.get("relevance_score", 0.0),
            "overall_stance": overall_stance,
            "support_count": support_count,
            "contradict_count": contradict_count,
            "evidence_sentences": evidence_sentences,
            "total_sentences_extracted": len(evidence_sentences),
        }

    # ------------------------------------------------------------------
    # Batch processing
    # ------------------------------------------------------------------

    def run(
        self,
        ranked_papers: List[Dict[str, Any]],
        hypothesis: str,
    ) -> List[Dict[str, Any]]:
        """
        Process all ranked papers and return evidence records.

        Args:
            ranked_papers: Output from LiteratureAgent.run()
            hypothesis: The biomedical hypothesis being tested.

        Returns:
            List of EvidenceRecord dicts, sorted by relevance_score desc.
        """
        print(f"\n[EvidenceAgent] Extracting evidence from {len(ranked_papers)} papers...")
        records = []
        for paper in ranked_papers:
            record = self.extract_evidence(paper, hypothesis)
            records.append(record)
            stance_icon = {"SUPPORT": "✅", "CONTRADICT": "❌", "NEUTRAL": "⚪"}.get(
                record["overall_stance"], "?"
            )
            print(
                f"  {stance_icon} [{record['overall_stance']:10s}] "
                f"score={record['relevance_score']:.3f} | "
                f"+{record['support_count']} -{record['contradict_count']} | "
                f"{record['title'][:60]}"
            )

        print(f"[EvidenceAgent] Done. {len(records)} evidence records produced.")
        return records