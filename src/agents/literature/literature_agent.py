from typing import List, Dict, Any
import os

from src.agents.literature.query_builder import QueryBuilder
from src.agents.literature.pubmed_fetcher import PubMedFetcher
from src.agents.literature.biorxiv_fetcher import BioRxivFetcher
from src.agents.literature.embedding_model import EmbeddingModel
from src.agents.literature.nlp_extractor import NLPExtractor
from src.agents.literature.graph_builder import GraphBuilder

class LiteratureAgent:
    """
    Advanced Literature Agent that retrieves from multiple sources,
    ranks via semantic embeddings, and builds a Knowledge Graph.
    """

    def __init__(
        self,
        email: str = "harveenkaur282@gmail.com",
        max_results: int = 15,
        use_semantic_ranking: bool = True
    ):
        self.max_results = max_results
        self.use_semantic_ranking = use_semantic_ranking
        
        self.query_builder = QueryBuilder()
        self.pubmed_fetcher = PubMedFetcher(email=email)
        self.biorxiv_fetcher = BioRxivFetcher()
        
        if self.use_semantic_ranking:
            # We use a lightweight model for the demo
            self.embedder = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        
        self.nlp = NLPExtractor()
        self.graph_builder = GraphBuilder()

    def run(self, hypothesis: str, top_k: int = 5) -> Dict[str, Any]:
        print("\n" + "="*60)
        print("  ADVANCED LITERATURE ANALYSIS PIPELINE")
        print("="*60)

        # 1. Build Query
        query = self.query_builder.run(hypothesis)

        # 2. Retrieve from Multiple Sources
        pubmed_papers = self.pubmed_fetcher.run(query, max_results=self.max_results)
        biorxiv_papers = self.biorxiv_fetcher.run(query, max_results=self.max_results // 2)
        
        all_papers = pubmed_papers + biorxiv_papers
        print(f"\n[LiteratureAgent] Total papers gathered: {len(all_papers)}")

        # 3. Rank Papers
        if self.use_semantic_ranking and all_papers:
            print(f"[LiteratureAgent] Ranking {len(all_papers)} papers using Semantic Embeddings...")
            hyp_emb = self.embedder.get_embeddings(hypothesis)
            doc_texts = [p.get("title", "") + " " + p.get("abstract", "") for p in all_papers]
            doc_embs = self.embedder.get_embeddings(doc_texts)
            
            scores = self.embedder.calculate_similarity(hyp_emb, doc_embs)
            
            for paper, score in zip(all_papers, scores):
                paper["relevance_score"] = round(float(score), 4)
            
            all_papers.sort(key=lambda x: x["relevance_score"], reverse=True)
            ranked_papers = all_papers[:top_k]
        else:
            # Fallback to simple slice if ranking is disabled
            ranked_papers = all_papers[:top_k]

        # 4. Extract Entities (NER)
        ranked_papers = self.nlp.run(ranked_papers)

        # 5. Build Knowledge Graph
        graph = self.graph_builder.build_from_papers(ranked_papers)
        
        # Save graph for the UI
        os.makedirs("data", exist_ok=True)
        self.graph_builder.save_graph("data/current_knowledge_graph.json")

        return {
            "hypothesis": hypothesis,
            "ranked_papers": ranked_papers,
            "graph_summary": {
                "nodes": graph.number_of_nodes(),
                "edges": graph.number_of_edges()
            }
        }

if __name__ == "__main__":
    agent = LiteratureAgent()
    results = agent.run("Vitamin D deficiency is linked to depression", top_k=3)
    
    print("\n--- TOP SEMANTIC RESULTS ---")
    for p in results["ranked_papers"]:
        print(f"\nTitle: {p['title']}")
        print(f"Score: {p['relevance_score']}")
        print(f"Entities: {[e['text'] for e in p['entities'][:5]]}")