from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.agents.literature.query_builder import QueryBuilder
from src.agents.literature.pubmed_fetcher import PubMedFetcher


class LiteratureAgent:

    def __init__(
        self,
        email: str = "harveenkaur282@gmail.com",
        max_results: int = 15,
    ):

        self.max_results = max_results
        self.query_builder = QueryBuilder()

        self.fetcher = PubMedFetcher(
            email=email,
            tool_name="multi_agent_biomedical_reasoning_system",
        )
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )

    def _build_document(
        self,
        paper: Dict[str, Any]
    ) -> str:
        title = paper.get("title", "")
        abstract = paper.get("abstract", "")

        return f"{title} {title} {abstract}"

#ranking using tfidf cosine similarity
    def rank_papers(
        self,
        hypothesis: str,
        papers: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        if not papers:
            print("[LiteratureAgent] No papers retrieved.")
            return []

        documents = [
            hypothesis
        ] + [
            self._build_document(p)
            for p in papers
        ]

        tfidf_matrix = self.vectorizer.fit_transform(documents)

        hypothesis_vec = tfidf_matrix[0]

        paper_vecs = tfidf_matrix[1:]

        scores = cosine_similarity(
            hypothesis_vec,
            paper_vecs
        ).flatten()

        scored = []

        for paper, score in zip(papers, scores):

            entry = dict(paper)

            entry["relevance_score"] = round(
                float(score),
                4
            )

            scored.append(entry)

        scored.sort(
            key=lambda x: x["relevance_score"],
            reverse=True,
        )

        return scored[:top_k]

    def retrieve_papers(
        self,
        hypothesis: str,
    ) -> List[Dict[str, Any]]:


        query = self.query_builder.run(hypothesis)

        papers = self.fetcher.run(
            query=query,
            max_results=self.max_results,
        )

        return papers

    def run(
        self,
        hypothesis: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:

        print("\n" + "=" * 60)
        print("  LITERATURE RETRIEVAL PIPELINE")
        print("=" * 60)

        print(f"\n[LiteratureAgent] Hypothesis:")
        print(f"  {hypothesis}")

        papers = self.retrieve_papers(hypothesis)

        print(f"\n[LiteratureAgent] Retrieved {len(papers)} papers.")

        ranked = self.rank_papers(
            hypothesis=hypothesis,
            papers=papers,
            top_k=top_k,
        )

        print(f"[LiteratureAgent] Top {len(ranked)} papers ranked.")

        return ranked

if __name__ == "__main__":

    agent = LiteratureAgent(
        email="harveenkaur282@gmail.com"
    )

    hypothesis = (
        "Vitamin D deficiency is linked to depression"
    )

    results = agent.run(
        hypothesis=hypothesis,
        top_k=5,
    )

    print("\n--- TOP RESULTS ---\n")

    for i, paper in enumerate(results, 1):

        print(f"{i}. {paper['title']}")

        print(
            f"   Relevance Score: "
            f"{paper['relevance_score']}"
        )

        print(
            f"   Journal: "
            f"{paper.get('journal', 'N/A')}"
        )

        print(
            f"   Year: "
            f"{paper.get('year', 'N/A')}"
        )

        abstract_preview = (
            paper.get("abstract", "")[:250]
        )

        print(
            f"   Abstract: "
            f"{abstract_preview}...\n"
        )