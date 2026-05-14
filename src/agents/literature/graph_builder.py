import networkx as nx
from typing import List, Dict, Any

class GraphBuilder:
    """Builds a Knowledge Graph from extracted biomedical entities."""
    
    def __init__(self):
        self.graph = nx.Graph()

    def build_from_papers(self, papers: List[Dict[str, Any]]) -> nx.Graph:
        """
        Creates nodes for entities and edges for co-occurrence.
        """
        print(f"[GraphBuilder] Building graph from {len(papers)} papers...")
        
        for paper in papers:
            entities = paper.get("entities", [])
            entity_texts = [e["text"].lower() for e in entities]
            
            # Add nodes
            for ent in entities:
                text = ent["text"].lower()
                if not self.graph.has_node(text):
                    self.graph.add_node(text, label=ent["label"], count=1)
                else:
                    self.graph.nodes[text]['count'] += 1
            
            # Add edges for co-occurrence in the same abstract
            for i in range(len(entity_texts)):
                for j in range(i + 1, len(entity_texts)):
                    u, v = entity_texts[i], entity_texts[j]
                    if u != v:
                        if not self.graph.has_edge(u, v):
                            self.graph.add_edge(u, v, weight=1)
                        else:
                            self.graph.edges[u, v]['weight'] += 1
                            
        print(f"[GraphBuilder] Graph built with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
        return self.graph

    def get_neighbors(self, entity: str) -> List[str]:
        """Find related entities for a given term."""
        entity = entity.lower()
        if self.graph.has_node(entity):
            return list(self.graph.neighbors(entity))
        return []

    def save_graph(self, path: str = "data/knowledge_graph.gpickle"):
        """Save the graph for later visualization (e.g. in Streamlit)."""
        # Note: nx.write_gpickle is deprecated in newer networkx, using ad-hoc save or json
        import json
        from networkx.readwrite import json_graph
        data = json_graph.node_link_data(self.graph)
        with open(path.replace(".gpickle", ".json"), "w") as f:
            json.dump(data, f)
        print(f"[GraphBuilder] Graph saved to {path.replace('.gpickle', '.json')}")

if __name__ == "__main__":
    builder = GraphBuilder()
    mock_papers = [
        {
            "entities": [
                {"text": "Vitamin D", "label": "CHEMICAL"},
                {"text": "Depression", "label": "DISEASE"}
            ]
        },
        {
            "entities": [
                {"text": "Vitamin D", "label": "CHEMICAL"},
                {"text": "Serotonin", "label": "CHEMICAL"}
            ]
        }
    ]
    g = builder.build_from_papers(mock_papers)
    print(f"Connections for Vitamin D: {builder.get_neighbors('Vitamin D')}")
