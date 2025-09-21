import pandas as pd

"""
MCP Tool: Data Filtering and Sorting
"""

def filter_by_region(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if df.empty or "THEATER" not in df.columns:
        return df
    
    query_lower = query.lower()
    
    # Map query terms to region codes
    region_mapping = {
        'pacific': ['PAC'],
        'pac': ['PAC'],
        'europe': ['EUR'],
        'eur': ['EUR'],
        'middle east': ['ME'],
        'me': ['ME'],
        'conus': ['CONUS'],
        'us': ['CONUS']
    }
    
    target_regions = []
    for region_name, region_codes in region_mapping.items():
        if region_name in query_lower:
            target_regions.extend(region_codes)
    
    if not target_regions:
        return df
    
    # Filter the dataframe
    mask = df["THEATER"].astype(str).str.upper().isin(target_regions)
    return df[mask]

def filter_and_sort(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if df.empty:
        return df
        
    query_lower = query.lower()
    
    # Determine sort criteria from query
    if 'clarity' in query_lower or 'resolution' in query_lower:
        if 'CLARITY' in df.columns:
            ascending = 'worst' in query_lower or 'lowest' in query_lower
            return df.sort_values('CLARITY', ascending=ascending)
    
    elif 'frame rate' in query_lower or 'framerate' in query_lower or 'fps' in query_lower:
        if 'FRRATE' in df.columns:
            ascending = 'worst' in query_lower or 'lowest' in query_lower
            return df.sort_values('FRRATE', ascending=ascending)
    
    elif 'latency' in query_lower or 'delay' in query_lower:
        if 'LAT_MS' in df.columns:
            ascending = not ('worst' in query_lower or 'highest' in query_lower)
            return df.sort_values('LAT_MS', ascending=ascending)
    
    # Default: sort by clarity if "best" is mentioned
    if 'best' in query_lower and 'CLARITY' in df.columns:
        return df.sort_values('CLARITY', ascending=False)
    
    return df