from agent import Agent

if __name__ == "__main__":
    mode = input("Choose mode (mock / llm): ").strip().lower()
    agent = Agent(mode=mode)

    print("Agentic Query System (type 'exit' to quit)")
    while True:
        query = input("> ")
        if query.lower() in ["exit", "quit"]:
            break
        answer = agent.ask(query)
        print(answer)
