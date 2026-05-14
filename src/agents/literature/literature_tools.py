from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from src.agents.literature.literature_agent import LiteratureAgent

class LiteratureSearchInput(BaseModel):
    """Input for LiteratureSearchTool."""
    hypothesis: str = Field(..., description="The biomedical hypothesis to search for.")
    top_k: int = Field(default=5, description="Number of top papers to return.")

class LiteratureSearchTool(BaseTool):
    name: str = "literature_search_tool"
    description: str = "Searches PubMed for scientific papers related to a biomedical hypothesis and ranks them by relevance."
    args_schema: Type[BaseModel] = LiteratureSearchInput

    def _run(self, hypothesis: str, top_k: int = 5) -> List[Dict[str, Any]]:
        agent = LiteratureAgent()
        return agent.run(hypothesis=hypothesis, top_k=top_k)
