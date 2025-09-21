# tools/analysis.py
"""
MCP Tool: Data Analysis Operations

This module provides MCP tools for analyzing camera feeds data:
- Performance analysis
- Regional comparisons
- Top feeds identification
- Statistical analysis
"""

import pandas as pd
from typing import Dict, List, Any, Optional


def analyze_performance(df: pd.DataFrame, region: Optional[str] = None) -> Dict[str, Any]:
    """
    MCP Tool: Analyze performance metrics for feeds
    
    Args:
        df: DataFrame with camera feeds data
        region: Optional region to focus analysis on
        
    Returns:
        Dictionary with performance analysis
    """
    if df.empty:
        return {}
    
    # Filter by region if specified
    analysis_df = df.copy()
    if region:
        analysis_df = analysis_df[analysis_df["THEATER"] == region.upper()]
    
    if analysis_df.empty:
        return {}
    
    # Calculate performance metrics
    analysis = {
        "total_feeds": len(analysis_df),
        "region": region,
        "avg_frame_rate": round(analysis_df["FRRATE"].mean(), 2),
        "avg_latency": round(analysis_df["LAT_MS"].mean(), 2),
        "avg_clarity": round(analysis_df["CLARITY"].mean(), 2),
        "min_latency": int(analysis_df["LAT_MS"].min()),
        "max_latency": int(analysis_df["LAT_MS"].max()),
        "min_frame_rate": round(analysis_df["FRRATE"].min(), 2),
        "max_frame_rate": round(analysis_df["FRRATE"].max(), 2),
        "min_clarity": int(analysis_df["CLARITY"].min()),
        "max_clarity": int(analysis_df["CLARITY"].max()),
    }
    
    # Add codec distribution
    codec_counts = analysis_df["CODEC"].value_counts().to_dict()
    analysis["codec_distribution"] = codec_counts
    
    # Add encryption stats
    encryption_stats = analysis_df["ENCR"].value_counts().to_dict()
    analysis["encryption_stats"] = encryption_stats
    
    return analysis


def compare_regions(df: pd.DataFrame, regions: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    MCP Tool: Compare performance metrics across regions
    
    Args:
        df: DataFrame with camera feeds data
        regions: List of region codes to compare
        
    Returns:
        Dictionary with regional comparison data
    """
    if df.empty:
        return {}
    
    comparison = {}
    
    for region in regions:
        region_data = df[df["THEATER"] == region.upper()]
        
        if not region_data.empty:
            comparison[region] = {
                "feed_count": len(region_data),
                "avg_frame_rate": round(region_data["FRRATE"].mean(), 2),
                "avg_latency": round(region_data["LAT_MS"].mean(), 2),
                "avg_clarity": round(region_data["CLARITY"].mean(), 2),
                "min_latency": int(region_data["LAT_MS"].min()),
                "max_latency": int(region_data["LAT_MS"].max()),
                "best_clarity_feed": region_data.loc[region_data["CLARITY"].idxmax(), "FEED_ID"],
                "best_clarity_value": int(region_data["CLARITY"].max()),
                "lowest_latency_feed": region_data.loc[region_data["LAT_MS"].idxmin(), "FEED_ID"],
                "lowest_latency_value": int(region_data["LAT_MS"].min()),
            }
    
    return comparison


def get_top_feeds(df: pd.DataFrame, metric: Optional[str] = None, limit: int = 10) -> pd.DataFrame:
    """
    MCP Tool: Get top feeds by specified metric
    
    Args:
        df: DataFrame with camera feeds data
        metric: Metric to sort by (clarity, framerate, latency)
        limit: Number of top feeds to return
        
    Returns:
        DataFrame with top feeds
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    if metric == "clarity":
        result = result.sort_values("CLARITY", ascending=False)
    elif metric == "framerate":
        result = result.sort_values("FRRATE", ascending=False)
    elif metric == "latency":
        result = result.sort_values("LAT_MS", ascending=True)
    else:
        # Default sort by clarity
        result = result.sort_values("CLARITY", ascending=False)
    
    return result.head(limit)


def get_best_performers(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    MCP Tool: Get best performing feeds across different metrics
    
    Args:
        df: DataFrame with camera feeds data
        
    Returns:
        Dictionary with best performers
    """
    if df.empty:
        return {}
    
    best_performers = {}
    
    # Best clarity
    best_clarity_idx = df["CLARITY"].idxmax()
    best_performers["best_clarity"] = {
        "feed_id": df.loc[best_clarity_idx, "FEED_ID"],
        "clarity": int(df.loc[best_clarity_idx, "CLARITY"]),
        "resolution": f"{df.loc[best_clarity_idx, 'RES_W']}x{df.loc[best_clarity_idx, 'RES_H']}",
        "region": df.loc[best_clarity_idx, "THEATER"]
    }
    
    # Best frame rate
    best_framerate_idx = df["FRRATE"].idxmax()
    best_performers["best_framerate"] = {
        "feed_id": df.loc[best_framerate_idx, "FEED_ID"],
        "framerate": df.loc[best_framerate_idx, "FRRATE"],
        "region": df.loc[best_framerate_idx, "THEATER"]
    }
    
    # Lowest latency
    best_latency_idx = df["LAT_MS"].idxmin()
    best_performers["lowest_latency"] = {
        "feed_id": df.loc[best_latency_idx, "FEED_ID"],
        "latency": int(df.loc[best_latency_idx, "LAT_MS"]),
        "region": df.loc[best_latency_idx, "THEATER"]
    }
    
    return best_performers


def analyze_codec_performance(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    MCP Tool: Analyze performance by codec type
    
    Args:
        df: DataFrame with camera feeds data
        
    Returns:
        Dictionary with codec performance analysis
    """
    if df.empty:
        return {}
    
    codec_analysis = {}
    
    for codec in df["CODEC"].unique():
        codec_data = df[df["CODEC"] == codec]
        
        codec_analysis[codec] = {
            "feed_count": len(codec_data),
            "avg_frame_rate": round(codec_data["FRRATE"].mean(), 2),
            "avg_latency": round(codec_data["LAT_MS"].mean(), 2),
            "avg_clarity": round(codec_data["CLARITY"].mean(), 2),
            "encryption_rate": round((codec_data["ENCR"].sum() / len(codec_data)) * 100, 1)
        }
    
    return codec_analysis


def get_regional_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    MCP Tool: Get summary statistics by region
    
    Args:
        df: DataFrame with camera feeds data
        
    Returns:
        Dictionary with regional summaries
    """
    if df.empty:
        return {}
    
    regional_summary = {}
    
    for region in df["THEATER"].unique():
        region_data = df[df["THEATER"] == region]
        
        regional_summary[region] = {
            "total_feeds": len(region_data),
            "avg_frame_rate": round(region_data["FRRATE"].mean(), 2),
            "avg_latency": round(region_data["LAT_MS"].mean(), 2),
            "avg_clarity": round(region_data["CLARITY"].mean(), 2),
            "codecs_used": region_data["CODEC"].unique().tolist(),
            "encryption_percentage": round((region_data["ENCR"].sum() / len(region_data)) * 100, 1)
        }
    
    return regional_summary


def find_feeds_by_criteria(df: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
    """
    MCP Tool: Find feeds matching specific criteria
    
    Args:
        df: DataFrame with camera feeds data
        criteria: Dictionary of criteria to match
        
    Returns:
        DataFrame with matching feeds
    """
    if df.empty:
        return df
    
    result = df.copy()
    
    # Apply criteria filters
    if "min_clarity" in criteria:
        result = result[result["CLARITY"] >= criteria["min_clarity"]]
    
    if "max_latency" in criteria:
        result = result[result["LAT_MS"] <= criteria["max_latency"]]
    
    if "min_framerate" in criteria:
        result = result[result["FRRATE"] >= criteria["min_framerate"]]
    
    if "encrypted" in criteria:
        result = result[result["ENCR"] == criteria["encrypted"]]
    
    if "codec" in criteria:
        result = result[result["CODEC"] == criteria["codec"]]
    
    if "region" in criteria:
        result = result[result["THEATER"] == criteria["region"]]
    
    return result
