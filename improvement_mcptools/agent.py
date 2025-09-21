import json
from typing import TypedDict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


# mcp tools
from tools.retrieval import retrieve_feeds, retrieve_encoder_params, retrieve_decoder_params
from tools.filtering import filter_by_region, filter_and_sort
from tools.encoder_tools import list_all_encoders, summarize_encoders
from tools.decoder_tools import list_all_decoders, summarize_decoders

class AgentState(TypedDict):
    question: str
    data: Any
    answer: str
    route: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# route queries to appropriate tool
def route_query(state: AgentState) -> AgentState:
    
    question = state["question"].lower()
    
    if "encoder" in question:
        state["route"] = "encoders"
    elif "decoder" in question:
        state["route"] = "decoders"
    else:
        state["route"] = "feeds"
    
    return state

# Process camera feed queries using MCP tools
def query_feeds(state: AgentState) -> AgentState:
    
    try:
        question = state["question"]
        
        #Retrieve all feeds
        feeds_data = retrieve_feeds()
        
        if feeds_data.empty:
            state["data"] = []
            return state
        
        # apply region filtering if specified
        feeds_data = filter_by_region(feeds_data, question)
        
        # apply sorting/filtering based on question
        feeds_data = filter_and_sort(feeds_data, question)
        
        state["data"] = feeds_data.to_dict('records')
        return state
        
    except Exception as e:
        state["data"] = []
        return state


def query_encoders(state: AgentState) -> AgentState:
    try:
        question = state["question"].lower()
        
        if "summary" in question or "summarize" in question:
            result = summarize_encoders()
            state["data"] = {"summary": result}
        else:
            result = list_all_encoders()
            state["data"] = result
            
        return state
        
    except Exception as e:
        state["data"] = []
        return state


def query_decoders(state: AgentState) -> AgentState:
    try:
        question = state["question"].lower()
        
        if "summary" in question or "summarize" in question:
            result = summarize_decoders()
            state["data"] = {"summary": result}
        else:
            result = list_all_decoders()
            state["data"] = result
            
        return state
        
    except Exception as e:
        state["data"] = []
        return state


def summarize(state: AgentState) -> AgentState:
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
        
        if "camera id" in question.lower() and isinstance(data, list):
            camera_ids = []
            for item in data:
                if isinstance(item, dict) and "CAMERA_ID" in item:
                    camera_ids.append(str(item["CAMERA_ID"]))
            
            if camera_ids:
                state["answer"] = f"The camera IDs are: {', '.join(camera_ids)}"
                return state

        # Use LLM for summarization
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

        response = llm.invoke(prompt)
        state["answer"] = response.content.strip()
        return state
        
    except Exception as e:
        state["answer"] = f"Error processing your question: {str(e)}"
        return state

# route to appropriate tool
def route_to_tool(state: AgentState) -> str:
    return state.get("route", "feeds")

def build_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_query)
    workflow.add_node("feeds", query_feeds)
    workflow.add_node("encoders", query_encoders)
    workflow.add_node("decoders", query_decoders)
    workflow.add_node("summarize", summarize)


    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_to_tool,
        {
            "feeds": "feeds",
            "encoders": "encoders",
            "decoders": "decoders"
        }
    )
    
    workflow.add_edge("feeds", "summarize")
    workflow.add_edge("encoders", "summarize")
    workflow.add_edge("decoders", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()