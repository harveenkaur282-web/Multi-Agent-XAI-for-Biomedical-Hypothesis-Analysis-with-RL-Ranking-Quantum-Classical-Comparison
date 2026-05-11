from src.agents.literature.literature_agent import LiteratureAgent


def main():
    agent = LiteratureAgent()

    hypothesis = "Vitamin D deficiency is linked to depression"

    results = agent.run(hypothesis, top_k=5)

    print("\n Top Papers:\n")

    for i, p in enumerate(results, 1):
        print(f"{i}. {p.get('title')}")
        print(f"   Score: {p['score']:.3f}")
        print(f"   Abstract: {p.get('abstract', '')[:120]}...\n")


if __name__ == "__main__":
    main()