import os
import json
from agent import build_agent

def run_evaluation(query_file="queries.txt", output_file="results_langraph.json"):
    with open(query_file, "r") as f:
        queries = [q.strip() for q in f.readlines() if q.strip()]

    agent = build_agent()

    results = []

    for q in queries:
        try:
            state = {"question": q, "data": None, "answer": ""}
            result = agent.invoke(state)
            results.append({
                "query": q,
                "answer": result["answer"]
            })
            print(f"✅ Query: {q}\n   → Answer: {result['answer']}\n")
        except Exception as e:
            results.append({
                "query": q,
                "error": str(e)
            })
            print(f"⚠️ Query: {q} failed with error: {e}\n")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Evaluation complete. Results saved to {output_file}")


if __name__ == "__main__":
    run_evaluation()
