import pandas as pd
import json
import os

"""
MCP Tool: Data Retrieval
"""

def retrieve_feeds() -> pd.DataFrame:
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "Data")
    
    csv_path = os.path.join(data_dir, "Table_feeds_v2.csv")
    xlsx_path = os.path.join(data_dir, "Table_feeds_v2.xlsx")
    
    df = pd.DataFrame()
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(xlsx_path):
        df = pd.read_excel(xlsx_path)
    
    if not df.empty:
        if "CLARITY" not in df.columns and "RES_W" in df.columns and "RES_H" in df.columns:
            df["CLARITY"] = df["RES_W"] * df["RES_H"]
        
        if "THEATER" in df.columns:
            df["THEATER"] = df["THEATER"].astype(str).str.strip().str.upper()
        
        if "FEED_ID" in df.columns and "CAMERA_ID" not in df.columns:
            df["CAMERA_ID"] = df["FEED_ID"]
    
    return df

def retrieve_encoder_params() -> dict:
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "Data")
    json_path = os.path.join(data_dir, "encoder_params.json")
    
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return {}

def retrieve_decoder_params() -> dict:
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "Data")
    json_path = os.path.join(data_dir, "decoder_params.json")
    
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            return json.load(f)
    return {}