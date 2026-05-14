import spacy
from typing import List, Dict, Any

class NLPExtractor:
    """Extracts biomedical entities (genes, diseases, chemicals) from text."""
    
    def __init__(self, model_name: str = "en_core_sci_md"):
        """
        Initialize with a scispaCy model.
        Note: You must install the model first:
        pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_md-0.5.4.tar.gz
        """
        print(f"[NLPExtractor] Loading model: {model_name}...")
        try:
            self.nlp = spacy.load(model_name)
        except Exception as e:
            print(f"[NLPExtractor] Warning: Could not load {model_name}. Fallback to en_core_web_sm if available.")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract entities and their labels from text."""
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities

    def run(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of papers and enrich them with entities."""
        print(f"[NLPExtractor] Extracting entities from {len(papers)} abstracts...")
        for paper in papers:
            text = paper.get("abstract", "")
            paper["entities"] = self.extract_entities(text)
        return papers

if __name__ == "__main__":
    extractor = NLPExtractor()
    sample = "Vitamin D deficiency might lead to secondary hyperparathyroidism."
    ents = extractor.extract_entities(sample)
    for e in ents:
        print(f"[{e['label']}] {e['text']}")
