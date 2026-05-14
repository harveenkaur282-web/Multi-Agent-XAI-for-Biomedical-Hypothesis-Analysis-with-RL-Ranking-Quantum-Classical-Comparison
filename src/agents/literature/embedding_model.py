from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Union

class EmbeddingModel:
    """Wrapper for semantic embeddings using SentenceTransformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a pre-trained model. 
        'all-MiniLM-L6-v2' is fast.
        'NeuML/pubmedbert-base-embeddings' is better for biomedical.
        """
        print(f"[EmbeddingModel] Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for a single string or a list of strings."""
        return self.model.encode(texts, convert_to_tensor=True)

    def calculate_similarity(self, query_embedding, doc_embeddings) -> List[float]:
        """Calculate cosine similarity between query and documents."""
        cos_scores = util.cos_sim(query_embedding, doc_embeddings)[0]
        return cos_scores.tolist()

if __name__ == "__main__":
    # Quick test
    model = EmbeddingModel()
    hyp = "Vitamin D deficiency"
    docs = ["Low levels of vitamin D", "Sunlight exposure helps", "Random medical text"]
    
    hyp_emb = model.get_embeddings(hyp)
    doc_embs = model.get_embeddings(docs)
    
    scores = model.calculate_similarity(hyp_emb, doc_embs)
    for doc, score in zip(docs, scores):
        print(f"Score: {score:.4f} | {doc}")
