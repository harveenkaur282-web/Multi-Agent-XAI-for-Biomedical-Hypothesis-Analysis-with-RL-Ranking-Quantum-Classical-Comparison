import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any


class PubMedFetcher:
    BASE_ESEARCH_URL = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    )

    BASE_EFETCH_URL = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    )

    def __init__(
        self,
        email: str = "harveenkaur282@gmail.com",
        tool_name: str = "multi_agent_biomedical_hypothesis_system",
    ):
        self.email = email
        self.tool_name = tool_name

    def search(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[str]:

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "tool": self.tool_name,
            "email": self.email,
        }

        response = requests.get(
            self.BASE_ESEARCH_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        ids = data.get("esearchresult", {}).get("idlist", [])

        return ids
    
    def fetch_details(
        self,
        pubmed_ids: List[str],
    ) -> List[Dict[str, Any]]:

        if not pubmed_ids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pubmed_ids),
            "retmode": "xml",
            "tool": self.tool_name,
            "email": self.email,
        }

        response = requests.get(
            self.BASE_EFETCH_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        root = ET.fromstring(response.text)

        papers = []

        for article in root.findall(".//PubmedArticle"):

            try:
                medline = article.find("MedlineCitation")
                article_data = medline.find("Article")

                pmid = medline.findtext("PMID", default="")

                title = article_data.findtext(
                    "ArticleTitle",
                    default=""
                )

                abstract_parts = article_data.findall(
                    ".//AbstractText"
                )

                abstract = " ".join(
                    [
                        part.text.strip()
                        for part in abstract_parts
                        if part.text
                    ]
                )

                journal = article_data.findtext(
                    ".//Journal/Title",
                    default=""
                )

                year = article_data.findtext(
                    ".//PubDate/Year",
                    default=""
                )

                authors = []

                for author in article_data.findall(".//Author"):

                    last_name = author.findtext("LastName", "")
                    fore_name = author.findtext("ForeName", "")

                    full_name = f"{fore_name} {last_name}".strip()

                    if full_name:
                        authors.append(full_name)

                papers.append({
                    "paper_id": pmid,
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "source": "PubMed",
                })

            except Exception as e:
                print(f"[PubMedFetcher] Error parsing article: {e}")

        return papers

    def run(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:

        print(f"\n[PubMedFetcher] Searching PubMed...")
        print(f"[PubMedFetcher] Query: {query}")

        ids = self.search(query, max_results=max_results)

        print(f"[PubMedFetcher] Retrieved {len(ids)} PubMed IDs.")

        papers = self.fetch_details(ids)

        print(f"[PubMedFetcher] Parsed {len(papers)} papers.")

        return papers


if __name__ == "__main__":

    fetcher = PubMedFetcher(
        email="harveenkaur282@gmail.com"
    )

    papers = fetcher.run(
        query="Vitamin D deficiency depression",
        max_results=5,
    )

    print("\n--- SAMPLE OUTPUT ---\n")

    for i, paper in enumerate(papers, 1):

        print(f"{i}. {paper['title']}")
        print(f"   PMID: {paper['paper_id']}")
        print(f"   Journal: {paper['journal']}")
        print(f"   Year: {paper['year']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}")

        abstract_preview = paper["abstract"][:250]

        print(f"   Abstract: {abstract_preview}...\n")