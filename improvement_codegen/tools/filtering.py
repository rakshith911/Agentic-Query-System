# tools/filtering.py
"""
MCP Tool: Data Filtering Operations

This module provides MCP tools for filtering camera feeds data:
- Regional filtering
- Metric-based filtering
- Encryption filtering
- Codec filtering
"""

import pandas as pd
from typing import Optional, List


def filter_by_region(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """MCP Tool: Filter feeds by region based on query"""
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
    """MCP Tool: Sort feeds based on query keywords"""
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


def filter_by_metric(df: pd.DataFrame, metric: str, query: str = "") -> pd.DataFrame:
    """
    MCP Tool: Filter and sort feeds by metric
    
    Args:
        df: DataFrame with camera feeds data
        metric: Metric type (clarity, framerate, latency)
        query: Original query for context
        
    Returns:
        Filtered and sorted DataFrame
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    if metric == "clarity":
        # Sort by clarity (highest first)
        df = df.sort_values("CLARITY", ascending=False)
        
    elif metric == "framerate":
        # Sort by frame rate (highest first)
        df = df.sort_values("FRRATE", ascending=False)
        
    elif metric == "latency":
        # Sort by latency (lowest first for "lowest latency" queries)
        if "lowest" in query.lower():
            df = df.sort_values("LAT_MS", ascending=True)
        else:
            df = df.sort_values("LAT_MS", ascending=False)
    
    return df


def filter_by_encryption(df: pd.DataFrame, encrypted: bool) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by encryption status
    
    Args:
        df: DataFrame with camera feeds data
        encrypted: True for encrypted feeds, False for unencrypted
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    return df[df["ENCR"] == encrypted].copy()


def filter_by_codec(df: pd.DataFrame, codec: str) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by codec type
    
    Args:
        df: DataFrame with camera feeds data
        codec: Codec type (H265, VP9, MPEG2, etc.)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or not codec:
        return df
    
    codec = codec.upper().strip()
    return df[df["CODEC"] == codec].copy()


def filter_by_resolution(df: pd.DataFrame, min_width: Optional[int] = None, 
                        min_height: Optional[int] = None) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by minimum resolution
    
    Args:
        df: DataFrame with camera feeds data
        min_width: Minimum width in pixels
        min_height: Minimum height in pixels
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    if min_width is not None:
        result = result[result["RES_W"] >= min_width]
    
    if min_height is not None:
        result = result[result["RES_H"] >= min_height]
    
    return result


def filter_by_frame_rate(df: pd.DataFrame, min_fps: Optional[float] = None,
                        max_fps: Optional[float] = None) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by frame rate range
    
    Args:
        df: DataFrame with camera feeds data
        min_fps: Minimum frame rate
        max_fps: Maximum frame rate
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    if min_fps is not None:
        result = result[result["FRRATE"] >= min_fps]
    
    if max_fps is not None:
        result = result[result["FRRATE"] <= max_fps]
    
    return result


def filter_by_latency(df: pd.DataFrame, max_latency: Optional[int] = None) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by maximum latency
    
    Args:
        df: DataFrame with camera feeds data
        max_latency: Maximum latency in milliseconds
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or max_latency is None:
        return df
    
    return df[df["LAT_MS"] <= max_latency].copy()


def filter_by_civilian_ok(df: pd.DataFrame, civilian_ok: bool) -> pd.DataFrame:
    """
    MCP Tool: Filter feeds by civilian access status
    
    Args:
        df: DataFrame with camera feeds data
        civilian_ok: True for civilian-accessible feeds
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    return df[df["CIV_OK"] == civilian_ok].copy()


def apply_multiple_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    MCP Tool: Apply multiple filters in sequence
    
    Args:
        df: DataFrame with camera feeds data
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered DataFrame
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    # Apply filters in order
    if "region" in filters:
        result = filter_by_region(result, filters["region"])
    
    if "codec" in filters:
        result = filter_by_codec(result, filters["codec"])
    
    if "encrypted" in filters:
        result = filter_by_encryption(result, filters["encrypted"])
    
    if "min_width" in filters or "min_height" in filters:
        result = filter_by_resolution(result, 
                                    filters.get("min_width"), 
                                    filters.get("min_height"))
    
    if "min_fps" in filters or "max_fps" in filters:
        result = filter_by_frame_rate(result, 
                                    filters.get("min_fps"), 
                                    filters.get("max_fps"))
    
    if "max_latency" in filters:
        result = filter_by_latency(result, filters["max_latency"])
    
    if "civilian_ok" in filters:
        result = filter_by_civilian_ok(result, filters["civilian_ok"])
    
    return result
