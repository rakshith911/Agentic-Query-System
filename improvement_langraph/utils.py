import pandas as pd


def compute_clarity(df: pd.DataFrame) -> pd.DataFrame:
    """Compute clarity as width x height if not already present."""
    if "CLARITY" not in df.columns:
        df["CLARITY"] = df["RES_W"] * df["RES_H"]
    return df
