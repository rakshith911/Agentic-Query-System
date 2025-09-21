import os
import json
import pandas as pd


'''
This is only for loading the given data.    
'''


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_table_feeds() -> pd.DataFrame:
    csv_path = os.path.join(DATA_DIR, "Table_feeds_v2.csv")
    xlsx_path = os.path.join(DATA_DIR, "Table_feeds_v2.xlsx")

    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    elif os.path.exists(xlsx_path):
        return pd.read_excel(xlsx_path)
    else:
        raise FileNotFoundError("No Table_feeds file found in data/")


def load_table_defs() -> pd.DataFrame:
    csv_path = os.path.join(DATA_DIR, "Table_defs_v2.csv")
    xlsx_path = os.path.join(DATA_DIR, "Table_defs_v2.xlsx")

    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    elif os.path.exists(xlsx_path):
        return pd.read_excel(xlsx_path)
    else:
        raise FileNotFoundError("No Table_defs file found in data/")


def load_json(filename: str) -> dict:

    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"{filename} not found in data/")
    with open(path, "r") as f:
        return json.load(f)


def load_encoder_schema() -> dict:
    return load_json("encoder_schema.json")


def load_decoder_schema() -> dict:
    return load_json("decoder_schema.json")


def load_encoder_params() -> dict:
    return load_json("encoder_params.json")


def load_decoder_params() -> dict:
    return load_json("decoder_params.json")
