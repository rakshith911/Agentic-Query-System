# improvement_codegen/agent.py
"""
Cursor AI-Generated Agentic Query System with LangGraph + MCP Tools

This implementation demonstrates Cursor's AI code generation capabilities
for building an agentic system that answers natural language questions
about camera feeds, encoders, and decoders.

Features:
- LangGraph workflow orchestration
- MCP tools for modular data operations
- Natural language responses
- OpenAI API integration
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from data_loader import (
    load_table_feeds,
    load_encoder_params,
    load_decoder_params,
    load_encoder_schema,
    load_decoder_schema,
)
from utils import compute_clarity
from tools.retrieval import retrieve_feeds, retrieve_encoder_params, retrieve_decoder_params
from tools.filtering import filter_by_region, filter_and_sort


# ---------------------------
# LangGraph State Definition
# ---------------------------
class AgentState(TypedDict):
    """State object for LangGraph workflow"""
    question: str
    parsed_intent: Dict[str, Any]
    data: Any
    answer: str
    route: str
    mcp_tools_used: List[str]


# ---------------------------
# Main Agent Class
# ---------------------------
class CursorGeneratedAgent:
    """
    AI-generated agent using LangGraph workflow orchestration and MCP tools
    """
    
    def __init__(self, mode: str = "ai", model: str = "gpt-4o-mini"):
        """
        Initialize the Cursor AI-generated agent
        
        Args:
            mode: "ai" for full AI mode, "mock" for testing
            model: OpenAI model to use
        """
        self.mode = mode
        self.model = model
        self.llm = ChatOpenAI(model=model, temperature=0)
        
        # Load data
        self.feeds = compute_clarity(load_table_feeds())
        self.encoder_params = load_encoder_params()
        self.decoder_params = load_decoder_params()
        self.encoder_schema = load_encoder_schema()
        self.decoder_schema = load_decoder_schema()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow using AI-generated nodes"""
        workflow = StateGraph(AgentState)
        
        # Add workflow nodes
        workflow.add_node("router", self._parse_intent_node)
        workflow.add_node("feeds", self._process_feeds_node)
        workflow.add_node("encoders", self._process_encoder_node)
        workflow.add_node("decoders", self._process_decoder_node)
        workflow.add_node("summarize", self._generate_response_node)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "feeds": "feeds",
                "encoders": "encoders",
                "decoders": "decoders"
            }
        )
        
        # All tools go to summarizer
        workflow.add_edge("feeds", "summarize")
        workflow.add_edge("encoders", "summarize")
        workflow.add_edge("decoders", "summarize")
        workflow.add_edge("summarize", END)
        
        return workflow.compile()
    
    def _parse_intent_node(self, state: AgentState) -> AgentState:
        """Route queries to appropriate tool"""
        question = state["question"].lower()
        
        if "encoder" in question:
            state["route"] = "encoders"
        elif "decoder" in question:
            state["route"] = "decoders"
        else:
            state["route"] = "feeds"
        
        return state
    
    def _route_query_node(self, state: AgentState) -> AgentState:
        """Route query to appropriate processor"""
        return state
    
    def _process_feeds_node(self, state: AgentState) -> AgentState:
        """Process camera feeds queries using MCP tools"""
        question = state["question"]
        
        try:
            # Step 1: Retrieve data using MCP tool
            feeds_data = retrieve_feeds()
            
            if feeds_data.empty:
                state["data"] = []
                return state
            
            # Step 2: Apply regional filtering using MCP tool
            feeds_data = filter_by_region(feeds_data, question)
            
            # Step 3: Apply sorting using MCP tool
            feeds_data = filter_and_sort(feeds_data, question)
            
            # Convert to list for JSON serialization
            state["data"] = feeds_data.to_dict('records')
            return state
            
        except Exception as e:
            state["data"] = []
            return state
    
    def _process_encoder_node(self, state: AgentState) -> AgentState:
        """Process encoder queries using MCP tools"""
        try:
            question = state["question"].lower()
            
            if "summary" in question or "summarize" in question:
                result = self._summarize_encoders()
                state["data"] = {"summary": result}
            else:
                result = retrieve_encoder_params()
                state["data"] = result
                
            return state
            
        except Exception as e:
            state["data"] = []
            return state
    
    def _process_decoder_node(self, state: AgentState) -> AgentState:
        """Process decoder queries using MCP tools"""
        try:
            question = state["question"].lower()
            
            if "summary" in question or "summarize" in question:
                result = self._summarize_decoders()
                state["data"] = {"summary": result}
            else:
                result = retrieve_decoder_params()
                state["data"] = result
                
            return state
            
        except Exception as e:
            state["data"] = []
            return state
    
    def _summarize_encoders(self) -> str:
        """Summarize encoder parameters"""
        try:
            params = retrieve_encoder_params()
            if not params:
                return "No encoder parameters found."
            
            summary = "Encoder Configuration Summary:\n"
            summary += f"• Codec: {params.get('codec', 'N/A')}\n"
            summary += f"• Profile: {params.get('profile', 'N/A')}\n"
            summary += f"• Bitrate: {params.get('bitrate_kbps', 'N/A')} kbps\n"
            summary += f"• Frame Rate: {params.get('framerate', 'N/A')} fps\n"
            summary += f"• Resolution: {params.get('width', 'N/A')}x{params.get('height', 'N/A')}"
            
            return summary
        except Exception as e:
            return f"Error summarizing encoders: {e}"
    
    def _summarize_decoders(self) -> str:
        """Summarize decoder parameters"""
        try:
            params = retrieve_decoder_params()
            if not params:
                return "No decoder parameters found."
            
            summary = "Decoder Configuration Summary:\n"
            summary += f"• Max Threads: {params.get('max_threads', 'N/A')}\n"
            summary += f"• Error Concealment: {params.get('error_concealment', 'N/A')}\n"
            summary += f"• Deblocking: {params.get('deblock', 'N/A')}\n"
            summary += f"• SAO: {params.get('sao', 'N/A')}\n"
            summary += f"• Output Format: {params.get('output_format', 'N/A')}"
            
            return summary
        except Exception as e:
            return f"Error summarizing decoders: {e}"
    
    def _generate_response_node(self, state: AgentState) -> AgentState:
        """Generate natural language response using LLM"""
        try:
            if not state["data"] or len(state["data"]) == 0:
                state["answer"] = "No information found for your question."
                return state

            # Handle summary responses
            if isinstance(state["data"], dict) and "summary" in state["data"]:
                state["answer"] = state["data"]["summary"]
                return state

            question = state["question"]
            data = state["data"]
            
            # Special handling for camera ID requests
            if "camera id" in question.lower() and isinstance(data, list):
                camera_ids = []
                for item in data:
                    if isinstance(item, dict) and "FEED_ID" in item:
                        camera_ids.append(str(item["FEED_ID"]))
                
                if camera_ids:
                    state["answer"] = f"The camera IDs are: {', '.join(camera_ids)}"
                    return state

            # Use LLM for complex summarization
            prompt = f"""
You are a precise analyst helping with camera feed queries.
Question: {question}
Data: {json.dumps(data, indent=2, default=str)}

Rules:
- Answer ONLY using the provided data
- Give a natural language summary, not just lists
- If asking for camera IDs, list them clearly
- If multiple results exist, group and compare as needed
- Be concise and direct
- If no relevant data, say "No information found"
"""

            response = self.llm.invoke(prompt)
            state["answer"] = response.content.strip()
            return state
            
        except Exception as e:
            state["answer"] = f"Error processing your question: {str(e)}"
            return state
    
    
    def _route_decision(self, state: AgentState) -> str:
        """Route to appropriate tool"""
        return state.get("route", "feeds")
    
    def ask(self, query: str) -> str:
        """Main entry point for query processing"""
        if self.mode == "mock":
            return self._mock_answer(query)
        else:
            # Run LangGraph workflow
            initial_state = {
                "question": query,
                "parsed_intent": {},
                "data": None,
                "answer": "",
                "route": "",
                "mcp_tools_used": []
            }
            
            result = self.workflow.invoke(initial_state)
            return result["answer"]
    
    def _mock_answer(self, query: str) -> str:
        """Mock implementation for testing"""
        q = query.lower()
        df = self.feeds.copy()
        
        # Simple region filtering
        if "pacific" in q or "pac" in q:
            df = df[df["THEATER"] == "PAC"]
        elif "europe" in q or "eur" in q:
            df = df[df["THEATER"] == "EUR"]
        elif "middle east" in q or "me" in q:
            df = df[df["THEATER"] == "ME"]
        elif "conus" in q or "us" in q:
            df = df[df["THEATER"] == "CONUS"]
        
        # Simple metric sorting
        if "clarity" in q or "resolution" in q:
            df = df.sort_values("CLARITY", ascending=False)
        elif "frame rate" in q or "framerate" in q:
            df = df.sort_values("FRRATE", ascending=False)
        elif "latency" in q:
            df = df.sort_values("LAT_MS", ascending=True)
        
        # Encoder/Decoder queries
        if "encoder" in q:
            return self._generate_encoder_response(query, self.encoder_params)
        if "decoder" in q:
            return self._generate_decoder_response(query, self.decoder_params)
        
        # Return results
        if df.empty:
            return "No matching feeds found."
        
        # Generate natural language response
        if "camera id" in q or "camera ids" in q:
            camera_ids = df["FEED_ID"].tolist()
            return f"I found {len(camera_ids)} camera feeds: {', '.join(camera_ids)}"
        
        response_parts = [f"I found {len(df)} camera feeds"]
        response_parts.append("Here are the details:")
        for i, (_, row) in enumerate(df.head(5).iterrows()):
            feed_info = f"  {i+1}. {row['FEED_ID']} ({row['THEATER']}) - {row['FRRATE']} fps, {row['LAT_MS']} ms latency"
            response_parts.append(feed_info)
        
        return "\n".join(response_parts)
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the workflow and tools used"""
        return {
            "workflow_type": "LangGraph + MCP Tools (Cursor AI Generated)",
            "nodes": [
                "parse_intent",
                "route_query",
                "process_feeds",
                "process_encoder",
                "process_decoder",
                "generate_response"
            ],
            "mcp_tools": [
                "retrieve_feeds",
                "filter_by_region",
                "filter_by_metric",
                "filter_by_encryption",
                "analyze_performance",
                "compare_regions",
                "get_top_feeds"
            ],
            "features": [
                "Natural language query processing",
                "Intelligent routing and orchestration",
                "Modular MCP tool operations",
                "Context-aware responses"
            ]
        }


# Backward compatibility
Agent = CursorGeneratedAgent