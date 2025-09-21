import pandas as pd

"""
Analysis tools for MCP agent.
Provides comparison, statistical summaries, and aggregation methods.
"""

def analyze_comparison(df1: pd.DataFrame, df2: pd.DataFrame, column: str) -> str:
    """
    Compare two dataframes based on a numeric column (e.g., FRRATE, LAT_MS).
    """
    if df1.empty and df2.empty:
        return "No data available for comparison."

    avg1 = df1[column].mean() if not df1.empty else None
    avg2 = df2[column].mean() if not df2.empty else None

    if avg1 is None and avg2 is None:
        return "No data found in either dataset."
    elif avg1 is None:
        return f"Only the second dataset has data. Its average {column} is {avg2:.2f}."
    elif avg2 is None:
        return f"Only the first dataset has data. Its average {column} is {avg1:.2f}."
    else:
        diff = avg1 - avg2
        return (
            f"The average {column} in the first dataset is {avg1:.2f}, "
            f"while in the second dataset it is {avg2:.2f}. "
            f"The difference between them is {diff:.2f}."
        )


def summarize_statistics(df: pd.DataFrame, column: str) -> str:
    if df.empty:
        return f"No data available to summarize {column}."

    minimum = df[column].min()
    maximum = df[column].max()
    avg = df[column].mean()

    return (
        f"For {column}: Minimum = {minimum}, Maximum = {maximum}, "
        f"Average = {avg:.2f}."
    )
