import pandas as pd


def compute_clarity(df: pd.DataFrame) -> pd.DataFrame:
    if "CLARITY" not in df.columns and "RES_W" in df.columns and "RES_H" in df.columns:
        df["CLARITY"] = df["RES_W"] * df["RES_H"]
    return df


def safe_lower(val):
    return val.lower() if isinstance(val, str) else val
