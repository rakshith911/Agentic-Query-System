# improvement_codegen/main.py
"""
Cursor AI-Generated Main CLI Runner

This is the main entry point for the agentic query system built using
Cursor's AI code generation capabilities. It provides an interactive
CLI for querying camera feeds, encoders, and decoders.
"""

import os
import sys
from typing import Dict, Any
import json

from agent import CursorGeneratedAgent
from data_loader import validate_data_integrity
from utils import display_system_info, get_demo_queries


def main():
    """Main function to run the agentic query system"""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        mode = "mock"
    else:
        mode = "ai"
    
    # Initialize agent
    try:
        agent = CursorGeneratedAgent(mode=mode)
    except Exception as e:
        print(f"ERROR: Failed to initialize agent: {e}")
        return
    
    # Interactive query loop
    print("Ask questions about camera feeds, encoders, and decoders")
    print("Type 'help' for examples or 'exit' to quit")
    
    while True:
        try:
            query = input("\nQuery: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            
            if query.lower() == "help":
                show_help_examples()
                continue
            
            if query.lower() == "info":
                show_system_info(agent)
                continue
            
            if query.lower() == "demo":
                run_demo_queries(agent)
                continue
            
            if query.lower() == "validate":
                show_validation_results()
                continue
            
            # Process query
            answer = agent.ask(query)
            print(f"\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nERROR: Error processing query: {e}")
            print("Please try again or type 'help' for examples.")


def show_help_examples():
    """Show example queries"""
    examples = [
        "Camera Feed Queries:",
        "  - What are the camera IDs in the Pacific region with the best clarity?",
        "  - Show me the highest frame rate feeds in Europe",
        "  - Which feeds have the lowest latency in CONUS?",
        "  - Find all encrypted feeds in the Middle East",
        "  - Are the Pacific feeds encrypted?",
        "",
        "Encoder/Decoder Queries:",
        "  - What are the encoder parameters?",
        "  - Show me the decoder configuration",
        "  - Compare encoder settings across different codecs",
        "",
        "Analysis Queries:",
        "  - Compare performance metrics across all regions",
        "  - What is the average frame rate of Pacific feeds compared to Europe?",
        "  - Find feeds with resolution higher than 1920x1080",
        "  - Show me feeds using H265 codec with encryption enabled"
    ]
    
    print("\nExample Queries:")
    for example in examples:
        print(example)


def show_system_info(agent: CursorGeneratedAgent):
    """Show detailed system information"""
    print("\nSystem Information:")
    
    # Workflow info
    workflow_info = agent.get_workflow_info()
    print(f"   Workflow Type: {workflow_info['workflow_type']}")
    print(f"   Nodes: {', '.join(workflow_info['nodes'])}")
    print(f"   MCP Tools: {', '.join(workflow_info['mcp_tools'])}")
    print(f"   Features: {', '.join(workflow_info['features'])}")
    
    # Data info
    try:
        validation_results = validate_data_integrity()
        if validation_results["overall_valid"]:
            print(f"   Camera Feeds: {validation_results['feeds_data']['record_count']} records")
            print(f"   Encoder Params: {validation_results['encoder_params']['param_count']} parameters")
            print(f"   Decoder Params: {validation_results['decoder_params']['param_count']} parameters")
    except Exception as e:
        print(f"   Data Status: Error - {e}")


def show_validation_results():
    """Show detailed validation results"""
    print("\nData Validation Results:")
    try:
        validation_results = validate_data_integrity()
        
        for component, result in validation_results.items():
            if component == "overall_valid":
                continue
            
            status = "Valid" if result["valid"] else "Invalid"
            print(f"   {component.replace('_', ' ').title()}: {status}")
            
            if not result["valid"] and result["issues"]:
                for issue in result["issues"]:
                    print(f"     - {issue}")
            
            if "record_count" in result:
                print(f"     Records: {result['record_count']}")
            if "param_count" in result:
                print(f"     Parameters: {result['param_count']}")
        
        overall_status = "All systems valid" if validation_results["overall_valid"] else "Issues detected"
        print(f"\n   Overall Status: {overall_status}")
        
    except Exception as e:
        print(f"   Validation error: {e}")


def run_demo_queries(agent: CursorGeneratedAgent):
    """Run a set of demo queries to showcase the system"""
    demo_queries = [
        "What are the camera IDs in the Pacific region with the best clarity?",
        "Show me the highest frame rate feeds in Europe",
        "What are the encoder parameters?",
        "Compare performance metrics across all regions",
        "Are the Pacific feeds encrypted?",
        "What is the average frame rate of Pacific feeds compared to Europe?"
    ]
    
    print("\nRunning Demo Queries:")
    print("=" * 60)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        try:
            answer = agent.ask(query)
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo completed!")


def run_single_query(query: str):
    """Run a single query and return the result"""
    try:
        agent = CursorGeneratedAgent(mode="mock")  # Use mock mode for single queries
        return agent.ask(query)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Check if demo mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("Running in demo mode...")
        agent = CursorGeneratedAgent(mode="mock")
        run_demo_queries(agent)
    elif len(sys.argv) > 1 and sys.argv[1] == "query":
        # Single query mode
        if len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            print(f"Query: {query}")
            result = run_single_query(query)
            print(f"Answer: {result}")
        else:
            print("Please provide a query. Usage: python main.py query 'your question here'")
    else:
        # Interactive mode
        main()