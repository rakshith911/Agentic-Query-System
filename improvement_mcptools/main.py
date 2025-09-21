import sys
from agent import build_agent

"""
Main entrypoint for MCP Tools Agentic Query System.
"""


def main():
    print("MCP Tools Agentic Query System")
    print("Type 'exit' to quit")
    
    try:
        agent = build_agent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return 1

    while True:
        try:
            question = input("\n> ").strip()
            
            if question.lower() in {"exit", "quit"}:
                break
            
            if not question:
                continue
                
            result = agent.invoke({"question": question})
            print(f"\n{result.get('answer', 'No response generated.')}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    sys.exit(main())