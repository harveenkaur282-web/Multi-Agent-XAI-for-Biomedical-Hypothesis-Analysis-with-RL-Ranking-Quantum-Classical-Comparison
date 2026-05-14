import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

class BioRxivFetcher:
    """Fetcher for BioRxiv pre-prints using their API."""
    
    BASE_URL = "https://api.biorxiv.org/details/biorxiv"

    def __init__(self):
        pass

    def fetch_recent_preprints(self, days: int = 30) -> List[Dict[str, Any]]:
        """Fetch preprints from the last N days."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        url = f"{self.BASE_URL}/{start_date}/{end_date}/0"
        
        response = requests.get(url)
        if response.status_code != 200:
            return []
            
        data = response.json()
        collection = data.get("collection", [])
        
        papers = []
        for item in collection:
            papers.append({
                "paper_id": item.get("doi", ""),
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "authors": item.get("authors", "").split(", "),
                "journal": "BioRxiv (Preprint)",
                "year": item.get("date", "")[:4],
                "source": "BioRxiv"
            })
        return papers

    def run(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        BioRxiv API doesn't support keyword search directly through the 'details' endpoint easily.
        We will fetch recent papers and filter by query keywords for now.
        Note: For a full implementation, one would use their R-based search or a third-party wrapper.
        """
        print(f"[BioRxivFetcher] Fetching recent preprints and filtering for: {query}...")
        
        # We'll fetch the last 60 days of preprints
        all_recent = self.fetch_recent_preprints(days=60)
        
        query_words = set(query.lower().split())
        filtered = []
        
        for paper in all_recent:
            text = (paper["title"] + " " + paper["abstract"]).lower()
            if any(word in text for word in query_words):
                filtered.append(paper)
                if len(filtered) >= max_results:
                    break
        
        print(f"[BioRxivFetcher] Found {len(filtered)} relevant preprints.")
        return filtered

if __name__ == "__main__":
    fetcher = BioRxivFetcher()
    results = fetcher.run("Vitamin D depression", max_results=5)
    for p in results:
        print(f"- {p['title']}")
