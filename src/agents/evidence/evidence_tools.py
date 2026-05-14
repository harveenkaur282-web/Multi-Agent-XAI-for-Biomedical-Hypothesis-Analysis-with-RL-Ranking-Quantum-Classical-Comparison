from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from .evidence_agent import EvidenceAgent

class EvidenceExtractionInput(BaseModel):
    """Input for EvidenceExtractionTool."""
    ranked_papers: List[Dict[str, Any]] = Field(..., description="List of ranked papers with abstracts.")
    hypothesis: str = Field(..., description="The biomedical hypothesis to validate.")

class EvidenceExtractionTool(BaseTool):
    name: str = "evidence_extraction_tool"
    description: str = "Analyzes abstracts of ranked papers to extract supporting and contradicting evidence for a hypothesis."
    args_schema: Type[BaseModel] = EvidenceExtractionInput

    def _run(self, ranked_papers: List[Dict[str, Any]], hypothesis: str) -> List[Dict[str, Any]]:
        agent = EvidenceAgent()
        return agent.run(ranked_papers=ranked_papers, hypothesis=hypothesis)
