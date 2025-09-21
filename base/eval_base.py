import os
import json
from agent import Agent  # Import your Base agent

def run_evaluation(query_file="queries.txt", output_file="results_base.json"):
    # Load queries
    with open(query_file, "r") as f:
        queries = [q.strip() for q in f.readlines() if q.strip()]

    # Init base agent
    agent = Agent(mode="llm")  # Or "mock" depending on what you want

    results = []

    for q in queries:
        try:
            answer = agent.ask(q)
            results.append({
                "query": q,
                "answer": answer
            })
            print(f"✅ Query: {q}\n   → Answer: {answer}\n")
        except Exception as e:
            results.append({
                "query": q,
                "error": str(e)
            })
            print(f"⚠️ Query: {q} failed with error: {e}\n")

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Evaluation complete. Results saved to {output_file}")


if __name__ == "__main__":
    run_evaluation()
