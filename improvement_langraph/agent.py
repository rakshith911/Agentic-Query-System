import os
import json
import pandas as pd
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Any

from data_loader import (
    load_table_feeds,
    load_encoder_params,
    load_decoder_params,
)
from utils import compute_clarity


'''
This module defines an intelligent agent using LangGraph to handle complex queries
about video feeds, encoder parameters, and decoder parameters. It includes a router
node to direct queries to the appropriate handler based on keywords in the question.'''


class AgentState(TypedDict):
    question: str
    data: Any
    answer: str


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

feeds = compute_clarity(load_table_feeds())
encoder_params = load_encoder_params()
decoder_params = load_decoder_params()



def router_node(state: AgentState) -> AgentState:
    #Route the query to appropriate handler
    q = state["question"].lower()
    
    # Store routing decision in state for conditional edges
    if "encoder" in q:
        state["route"] = "encoder"
    elif "decoder" in q:
        state["route"] = "decoder"
    else:
        state["route"] = "feeds"
    
    return state


def query_feeds(state: AgentState) -> AgentState:
    q = state["question"].lower()
    df = feeds.copy()
    df["THEATER"] = df["THEATER"].astype(str).str.strip().str.upper()

    if "compare" in q or "vs" in q or "versus" in q or "average" in q:
        results = {}
        for region in ["PAC", "EUR", "ME", "CONUS"]:
            if region.lower() in q or region in q.upper():
                subset = df[df["THEATER"] == region]
                if not subset.empty:
                    results[region] = {
                        "avg_frame_rate": round(subset["FRRATE"].mean(), 2),
                        "avg_latency": round(subset["LAT_MS"].mean(), 2),
                        "avg_clarity": round(subset["CLARITY"].mean(), 2),
                        "feed_count": len(subset),
                    }
        state["data"] = results
        return state

    if "pacific" in q or "pac" in q:
        df = df[df["THEATER"] == "PAC"]
    elif "europe" in q or "eur" in q:
        df = df[df["THEATER"] == "EUR"]
    elif "middle east" in q or "me" in q:
        df = df[df["THEATER"] == "ME"]
    elif "conus" in q or "us" in q:
        df = df[df["THEATER"] == "CONUS"]

    if df.empty:
        state["data"] = []
        return state

    if "clarity" in q or "resolution" in q:
        df = df.sort_values("CLARITY", ascending=False)
    elif "frame rate" in q or "framerate" in q:
        df = df.sort_values("FRRATE", ascending=False)
    elif "latency" in q:
        # "highest latency" → descending
        if "highest" in q or "max" in q:
            df = df.sort_values("LAT_MS", ascending=False)
        else:
            df = df.sort_values("LAT_MS", ascending=True)

    if "encrypt" in q:
        df = df[["FEED_ID", "THEATER", "ENCR", "FRRATE", "LAT_MS", "CLARITY"]]

    # return all rows and let llm summarize
    state["data"] = df.to_dict(orient="records")
    return state


def query_encoder(state: AgentState) -> AgentState:
    state["data"] = encoder_params
    return state

def query_decoder(state: AgentState) -> AgentState:
    state["data"] = decoder_params
    return state


'''
Stating the rules clearly helps the LLM provide accurate and relevant summaries.
'''

def summarize(state: AgentState) -> AgentState:
    if not state["data"]:
        state["answer"] = "No information found for your question."
        return state

    prompt = f"""
You are a precise data analyst.
Question: {state['question']}
Data: {json.dumps(state['data'], indent=2)}

Rules:
- Use ONLY the provided Data (never make up values).
- If question asks about one region → summarize only that region.
- If question compares regions → compute differences or averages clearly.
- Always answer in natural, fluent language, not just lists or JSON.
- If data is empty, respond with: "No information found."
"""

    response = llm.invoke(prompt)
    state["answer"] = response.content.strip()
    return state


def route_decision(state: AgentState):
    return state.get("route", "feeds")


#langraph workflow definition
def build_agent():
    workflow = StateGraph(AgentState)

    # all nodes
    workflow.add_node("router", router_node)
    workflow.add_node("feeds", query_feeds)
    workflow.add_node("encoder", query_encoder)
    workflow.add_node("decoder", query_decoder)
    workflow.add_node("summarize", summarize)

    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {"feeds": "feeds", "encoder": "encoder", "decoder": "decoder"}
    )
    
    workflow.add_edge("feeds", "summarize")
    workflow.add_edge("encoder", "summarize")
    workflow.add_edge("decoder", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile()