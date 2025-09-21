'''
Utility functions for data processing and analysis.
'''


def compute_clarity(df):
    df = df.copy()
    df["CLARITY"] = df["RES_W"] * df["RES_H"]
    return df


# made this to print only a few dataframes

def pretty_print(df, columns=None, max_rows=5):
    if columns:
        print(df[columns].head(max_rows))
    else:
        print(df.head(max_rows))
