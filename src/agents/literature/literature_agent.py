
import json
import os
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class LiteratureAgent:
    """
    Fetches and ranks biomedical papers against a hypothesis using TF-IDF.

    Day 1: keyword overlap + abstract length bias  (removed)
    Day 2: TF-IDF vectorisation + cosine similarity (current)
    """

    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.join(
            os.path.dirname(__file__), "../../data/raw/sample_papers.json"
        )
        self.papers: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),   # unigrams + bigrams catch phrases like "beta amyloid"
            max_features=5000,
        )
        self._load_papers()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_papers(self) -> None:
        """Load papers from JSON. Handles both list and dict formats."""
        if not os.path.exists(self.data_path):
            print(f"[LiteratureAgent] WARNING: data file not found at {self.data_path}")
            return
        with open(self.data_path, "r") as f:
            raw = json.load(f)
        self.papers = raw if isinstance(raw, list) else raw.get("papers", [])
        print(f"[LiteratureAgent] Loaded {len(self.papers)} papers.")

    # ------------------------------------------------------------------
    # Core ranking
    # ------------------------------------------------------------------

    def _build_document(self, paper: Dict[str, Any]) -> str:
        """
        Combine title + abstract into one document for TF-IDF.
        Title is doubled to give it slightly higher weight.
        """
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")
        return f"{title} {title} {abstract}"

    def rank_papers(self, hypothesis: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Rank papers by cosine similarity to the hypothesis using TF-IDF.

        Args:
            hypothesis: The biomedical claim/question to evaluate.
            top_k: Number of top papers to return.

        Returns:
            List of paper dicts with added 'relevance_score' field, sorted desc.
        """
        if not self.papers:
            print("[LiteratureAgent] No papers loaded — returning empty list.")
            return []

        # Build corpus: hypothesis first, then all papers
        documents = [hypothesis] + [self._build_document(p) for p in self.papers]

        # Fit + transform in one shot
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # Hypothesis is row 0; papers are rows 1..N
        hypothesis_vec = tfidf_matrix[0]
        paper_vecs = tfidf_matrix[1:]

        scores = cosine_similarity(hypothesis_vec, paper_vecs).flatten()

        # Attach scores to paper dicts (copy to avoid mutating originals)
        scored = []
        for paper, score in zip(self.papers, scores):
            entry = dict(paper)
            entry["relevance_score"] = round(float(score), 4)
            scored.append(entry)

        # Sort descending and return top_k
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, hypothesis: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Main entry point used by pipelines."""
        print(f"\n[LiteratureAgent] Hypothesis: '{hypothesis}'")
        results = self.rank_papers(hypothesis, top_k)
        print(f"[LiteratureAgent] Top {len(results)} papers ranked.")
        return results