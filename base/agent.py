import os
import json
import pandas as pd
from openai import OpenAI
from data_loader import (
    load_table_feeds,
    load_encoder_params,
    load_decoder_params,
)
from utils import compute_clarity


'''
In this I have implemented an Agent class that can operate in two modes: mock for rule-based parsing 
and llm for AI-driven responses using OpenAI's GPT models. 
The agent here handles queries as mentioned in the requirements about camera feeds, 
and assumes that the person using this will use natural language to get answers.
'''



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # I have used my OpenAI API key 


class Agent:
    def __init__(self, mode="mock", model="gpt-4o-mini"):
        """
        mode = "mock" -> rule-based parsing (offline, free)
        mode = "llm"  -> AI agent with tool-calling
        """
        self.mode = mode
        self.model = model
        self.feeds = compute_clarity(load_table_feeds())
        self.encoder_params = load_encoder_params()
        self.decoder_params = load_decoder_params()

    def ask(self, query: str):
        if self.mode == "mock":
            return self._mock_answer(query)
        elif self.mode == "llm":
            return self._llm_answer(query)
        else:
            raise ValueError("Mode must be 'mock' or 'llm'")

    def _mock_answer(self, query: str):
        q = query.lower()
        df = self.feeds.copy()

        df["THEATER"] = df["THEATER"].astype(str).str.strip().str.upper()

        region_map = {
            "pacific": "PAC",
            "pac": "PAC",
            "europe": "EUR",
            "eur": "EUR",
            "middle east": "ME",
            "me": "ME",
            "conus": "CONUS",
            "us": "CONUS",
        } # mapping for region keywords using a dictionary for simplicity

        applied_region = None
        for k, v in region_map.items():
            if k in q:
                applied_region = v
                df = df[df["THEATER"] == v]
                break 

        # encoder/decoder queries are below

        if "encoder" in q:
            return f"Encoder parameters:\n{json.dumps(self.encoder_params, indent=2)}"
        if "decoder" in q:
            return f"Decoder parameters:\n{json.dumps(self.decoder_params, indent=2)}"

        # metrics-based queries

        if "frame rate" in q or "framerate" in q:
            if df.empty:
                return f"No feeds found for region={applied_region}."
            df = df.sort_values("FRRATE", ascending=False)
            return df[["FEED_ID", "THEATER", "FRRATE"]].head(10).to_string(index=False)

        if "clarity" in q or "resolution" in q:
            if df.empty:
                return f"No feeds found for region={applied_region}."
            df = df.sort_values("CLARITY", ascending=False)
            return df[["FEED_ID", "THEATER", "RES_W", "RES_H", "CLARITY"]].head(10).to_string(index=False)

        if "latency" in q:
            if df.empty:
                return f"No feeds found for region={applied_region}."
            df = df.sort_values("LAT_MS", ascending=True)
            return df[["FEED_ID", "THEATER", "LAT_MS"]].head(10).to_string(index=False)

        # default: if nothing return no matches found
        if df.empty:
            return "No matching feeds found."
        return df[["FEED_ID", "THEATER"]].head(10).to_string(index=False)


    def _llm_answer(self, query: str):
        system_prompt = """You are an agent that helps analysts query camera feeds.
You may use the tools to retrieve data. 
After receiving tool results, summarize them in plain English.
Always explain findings clearly and concisely."""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "query_feeds",
                        "description": "Look up feeds with optional filters and sorting",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filters": {"type": "object"},
                                "sort": {"type": "object"},
                            },
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_encoder",
                        "description": "Retrieve encoder parameters",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "query_decoder",
                        "description": "Retrieve decoder parameters",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
            ],
        )

        message = response.choices[0].message
        tool_call = message.tool_calls[0] if message.tool_calls else None

        if tool_call:
            if tool_call.function.name == "query_feeds":
                data = self._tool_query_feeds(tool_call.function.arguments)
                return self._summarize_with_llm(query, data)
            elif tool_call.function.name == "query_encoder":
                return json.dumps(self.encoder_params, indent=2)
            elif tool_call.function.name == "query_decoder":
                return json.dumps(self.decoder_params, indent=2)

        return message.content or "I could not understand the query."


    def _tool_query_feeds(self, args: str):
        try:
            params = json.loads(args)
        except Exception:
            params = {}

        df = self.feeds.copy()
        df["THEATER"] = df["THEATER"].astype(str).str.strip().str.upper()

        # filtering
        for col, val in params.get("filters", {}).items():
            if col in df.columns:
                if col == "THEATER":
                    val = str(val).strip().upper()
                df = df[df[col] == val]

        # sorting
        sort = params.get("sort")
        if sort:
            col = sort.get("column")
            order = sort.get("order", "desc") == "desc"
            if col in df.columns:
                df = df.sort_values(col, ascending=not order)

        # Return only filtered records
        return df.head(10).to_dict(orient="records")


    # I use the below function to summarize the data using LLM

    def _summarize_with_llm(self, query: str, data: list):
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Summarize the data for the analyst in plain English."},
                {"role": "user", "content": f"Query: {query}\nData: {json.dumps(data, indent=2)}"},
            ],
        )
        return response.choices[0].message.content