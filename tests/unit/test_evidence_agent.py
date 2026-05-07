"""
tests/test_evidence_agent.py

Run with:
    pytest tests/test_evidence_agent.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from agents.evidence_agent import EvidenceAgent


HYPOTHESIS = "neuroinflammation drives amyloid accumulation in Alzheimer's disease"

MOCK_PAPER_SUPPORT = {
    "paper_id": "test_001",
    "title": "Neuroinflammation Test Paper",
    "relevance_score": 0.75,
    "abstract": (
        "We demonstrate that microglial activation is significantly increased in AD. "
        "Evidence confirms that neuroinflammation supports amyloid-beta plaque formation. "
        "These findings support the hypothesis that inflammation drives cognitive decline."
    ),
}

MOCK_PAPER_CONTRADICT = {
    "paper_id": "test_002",
    "title": "Anti-inflammation Paper",
    "relevance_score": 0.40,
    "abstract": (
        "Anti-inflammatory treatment did not result in significant improvement. "
        "No significant reduction in amyloid burden was observed. "
        "These findings are inconsistent with the hypothesis."
    ),
}

MOCK_PAPER_EMPTY = {
    "paper_id": "test_003",
    "title": "Empty Abstract",
    "relevance_score": 0.10,
    "abstract": "",
}


def test_support_detection():
    agent = EvidenceAgent()
    record = agent.extract_evidence(MOCK_PAPER_SUPPORT, HYPOTHESIS)
    assert record["overall_stance"] == "SUPPORT", f"Expected SUPPORT, got {record['overall_stance']}"
    assert record["support_count"] > 0


def test_contradict_detection():
    agent = EvidenceAgent()
    record = agent.extract_evidence(MOCK_PAPER_CONTRADICT, HYPOTHESIS)
    assert record["overall_stance"] == "CONTRADICT", f"Expected CONTRADICT, got {record['overall_stance']}"
    assert record["contradict_count"] > 0


def test_empty_abstract_handled():
    agent = EvidenceAgent()
    record = agent.extract_evidence(MOCK_PAPER_EMPTY, HYPOTHESIS)
    assert record["total_sentences_extracted"] == 0
    assert record["overall_stance"] == "NEUTRAL"


def test_batch_run():
    agent = EvidenceAgent()
    papers = [MOCK_PAPER_SUPPORT, MOCK_PAPER_CONTRADICT, MOCK_PAPER_EMPTY]
    records = agent.run(papers, HYPOTHESIS)
    assert len(records) == 3
    stances = {r["paper_id"]: r["overall_stance"] for r in records}
    assert stances["test_001"] == "SUPPORT"
    assert stances["test_002"] == "CONTRADICT"
    assert stances["test_003"] == "NEUTRAL"


def test_evidence_sentences_have_required_keys():
    agent = EvidenceAgent()
    record = agent.extract_evidence(MOCK_PAPER_SUPPORT, HYPOTHESIS)
    for sent_obj in record["evidence_sentences"]:
        assert "sentence" in sent_obj
        assert "label" in sent_obj
        assert "relevance" in sent_obj
        assert sent_obj["label"] in ("SUPPORT", "CONTRADICT", "NEUTRAL")


if __name__ == "__main__":
    test_support_detection()
    test_contradict_detection()
    test_empty_abstract_handled()
    test_batch_run()
    test_evidence_sentences_have_required_keys()
    print("\n✅ All tests passed.")