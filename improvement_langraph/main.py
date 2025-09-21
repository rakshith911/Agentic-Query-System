import os
from agent import build_agent
'''
A simple command-line interface to interact with the LangGraph agent.
'''

def main():
    agent = build_agent()

    print("LangGraph Agentic Query System (type 'exit' to quit)")
    while True:
        q = input("> ")
        if q.lower() in ["exit", "quit"]:
            break

        state = {"question": q, "data": None, "answer": ""}
        result = agent.invoke(state)

        print("\n[Answer]\n", result["answer"], "\n")

if __name__ == "__main__":
    main()
