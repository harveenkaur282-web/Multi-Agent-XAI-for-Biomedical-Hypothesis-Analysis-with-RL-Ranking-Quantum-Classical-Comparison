import os
from crewai import Agent, Task, Crew, Process
from src.agents.literature.literature_tools import LiteratureSearchTool
from src.agents.evidence.evidence_tools import EvidenceExtractionTool

class BiomedicalResearchCrew:
    """Manages the CrewAI agents and tasks for biomedical hypothesis analysis."""

    def __init__(self):
        # Initialize tools
        self.lit_tool = LiteratureSearchTool()
        self.ev_tool = EvidenceExtractionTool()

    def researcher_agent(self) -> Agent:
        return Agent(
            role='Senior Biomedical Researcher',
            goal='Identify and retrieve relevant scientific literature for a hypothesis: {hypothesis}',
            backstory="""You are an expert in medical informatics and literature retrieval. 
            You know how to navigate PubMed and extract the most relevant papers to validate or refute medical claims.""",
            tools=[self.lit_tool],
            verbose=True,
            allow_delegation=False
        )

    def analyst_agent(self) -> Agent:
        return Agent(
            role='Evidence Analyst',
            goal='Analyze retrieved papers to find supporting and contradicting evidence for: {hypothesis}',
            backstory="""You are a clinical researcher specializing in evidence-based medicine. 
            You excel at parsing complex medical abstracts and identifying high-quality evidence.""",
            tools=[self.ev_tool],
            verbose=True,
            allow_delegation=False
        )

    def auditor_agent(self) -> Agent:
        return Agent(
            role='XAI Auditor',
            goal='Provide a transparent, explainable summary of the findings for: {hypothesis}',
            backstory="""You are a specialist in Explainable AI and medical ethics. 
            Your job is to ensure that the reasoning behind the final verdict is crystal clear and grounded in the evidence provided by other agents.""",
            verbose=True,
            allow_delegation=False
        )

    def kickoff(self, hypothesis: str):
        """Starts the multi-agent research process."""
        
        # Define Agents
        researcher = self.researcher_agent()
        analyst = self.analyst_agent()
        auditor = self.auditor_agent()

        # Define Tasks
        search_task = Task(
            description=f"Search for papers related to the hypothesis: {hypothesis}",
            expected_output="A list of ranked papers with their relevance scores and abstracts.",
            agent=researcher
        )

        analysis_task = Task(
            description=f"Extract evidence from the papers found in the search task for the hypothesis: {hypothesis}",
            expected_output="Structured evidence records showing support/contradiction for each paper.",
            agent=analyst,
            context=[search_task]
        )

        audit_task = Task(
            description=f"Summarize the overall stance on the hypothesis: {hypothesis} based on the evidence analyst's report.",
            expected_output="A final explainable report with a verdict and detailed reasoning traces.",
            agent=auditor,
            context=[analysis_task]
        )

        # Form the Crew
        crew = Crew(
            agents=[researcher, analyst, auditor],
            tasks=[search_task, analysis_task, audit_task],
            process=Process.sequential,
            verbose=True
        )

        return crew.kickoff(inputs={'hypothesis': hypothesis})

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    manager = BiomedicalResearchCrew()
    result = manager.kickoff(hypothesis="Vitamin D deficiency is linked to depression")
    print("\n\n########################")
    print("## FINAL REPORT")
    print("########################\n")
    print(result)
