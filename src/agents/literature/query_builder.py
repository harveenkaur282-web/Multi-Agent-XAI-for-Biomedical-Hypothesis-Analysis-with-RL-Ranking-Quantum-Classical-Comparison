import re
from typing import List


class QueryBuilder:
    STOPWORDS = {
        "is", "are", "was", "were",
        "be", "being", "been",
        "linked", "associated",
        "with", "to", "and",
        "or", "of", "in", "the",
        "a", "an",
    }

    def __init__(self):
        pass


    def clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_keywords(self, text: str) -> List[str]:

        tokens = text.split()

        keywords = [
            token
            for token in tokens
            if token not in self.STOPWORDS
            and len(token) > 2
        ]

        return keywords

    def build_phrase_groups(
        self,
        keywords: List[str]
    ) -> List[str]:

        phrases = []

        text = " ".join(keywords)

        if "vitamin d deficiency" in text:
            phrases.append('"vitamin d deficiency"')

            keywords = [
                k for k in keywords
                if k not in {"vitamin", "d", "deficiency"}
            ]

        phrases.extend(keywords)

        return phrases

    def build_query(self, hypothesis: str) -> str:
        cleaned = self.clean_text(hypothesis)

        keywords = self.extract_keywords(cleaned)

        phrases = self.build_phrase_groups(keywords)

        if not phrases:
            return cleaned

        query = " AND ".join(phrases)

        return query

    def run(self, hypothesis: str) -> str:
        print("\n[QueryBuilder] Building search query...")
        print(f"[QueryBuilder] Hypothesis: {hypothesis}")

        query = self.build_query(hypothesis)

        print(f"[QueryBuilder] Query: {query}")

        return query


if __name__ == "__main__":

    qb = QueryBuilder()

    hypothesis = (
        "Vitamin D deficiency is linked to depression"
    )

    query = qb.run(hypothesis)

    print("\nFinal Query:")
    print(query)