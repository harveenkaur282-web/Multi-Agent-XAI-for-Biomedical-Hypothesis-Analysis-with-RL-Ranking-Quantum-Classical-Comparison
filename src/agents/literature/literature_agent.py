import json
import os

class LiteratureAgent:
    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "data",
            "sample",
            "sample_pubmed_results.json",
        )
        self.papers = []

    def load_papers(self):
      with open(self.data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

      if isinstance(data, dict):
        self.papers = data.get("results", [])
      elif isinstance(data, list):
        self.papers = data
      else:
        self.papers = []

      return self.papers

    # ----------------------------
    # STEP 2: Dummy "fetch"
    # (later replace with PubMed API)
    # ----------------------------
    def fetch_papers(self, hypothesis: str):
        print(f"\n🔍 Fetching papers for: {hypothesis}\n")
        return self.load_papers()

    # ----------------------------
    # STEP 3: Simple scoring
    # (baseline heuristic)
    # ----------------------------
    def score_paper(self, paper, hypothesis: str):
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()

        hyp_words = set(hypothesis.lower().split())

        # simple overlap score
        text = title + " " + abstract
        score = sum(1 for word in hyp_words if word in text)

        # small boost for longer abstracts (optional bias)
        score += len(abstract) * 0.001

        return score

    # ----------------------------
    # STEP 4: Rank papers
    # ----------------------------
    def rank_papers(self, hypothesis: str):
        scored = []

        for paper in self.papers:
            score = self.score_paper(paper, hypothesis)
            paper["score"] = score
            scored.append(paper)

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    # ----------------------------
    # FULL PIPELINE
    # ----------------------------
    def run(self, hypothesis: str, top_k: int = 5):
        papers = self.fetch_papers(hypothesis)
        ranked = self.rank_papers(hypothesis)

        return ranked[:top_k]