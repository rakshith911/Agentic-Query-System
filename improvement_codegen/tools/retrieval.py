# tools/retrieval.py
"""
MCP Tool: Data Retrieval Operations

This module provides MCP tools for retrieving data from various sources:
- Camera feeds data
- Encoder parameters
- Decoder parameters
"""

import pandas as pd
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import (
    load_table_feeds,
    load_encoder_params,
    load_decoder_params,
    load_encoder_schema,
    load_decoder_schema,
)


def retrieve_feeds() -> pd.DataFrame:
    """
    MCP Tool: Retrieve all camera feeds data
    
    Returns:
        DataFrame with camera feeds data including computed clarity
    """
    try:
        feeds = load_table_feeds()
        # Add clarity computation
        feeds["CLARITY"] = feeds["RES_W"] * feeds["RES_H"]
        return feeds
    except Exception as e:
        print(f"Error retrieving feeds: {e}")
        return pd.DataFrame()


def retrieve_encoder_params() -> Dict[str, Any]:
    """
    MCP Tool: Retrieve encoder parameters
    
    Returns:
        Dictionary with encoder parameters
    """
    try:
        return load_encoder_params()
    except Exception as e:
        print(f"Error retrieving encoder params: {e}")
        return {}


def retrieve_decoder_params() -> Dict[str, Any]:
    """
    MCP Tool: Retrieve decoder parameters
    
    Returns:
        Dictionary with decoder parameters
    """
    try:
        return load_decoder_params()
    except Exception as e:
        print(f"Error retrieving decoder params: {e}")
        return {}


def retrieve_encoder_schema() -> Dict[str, Any]:
    """
    MCP Tool: Retrieve encoder schema
    
    Returns:
        Dictionary with encoder schema
    """
    try:
        return load_encoder_schema()
    except Exception as e:
        print(f"Error retrieving encoder schema: {e}")
        return {}


def retrieve_decoder_schema() -> Dict[str, Any]:
    """
    MCP Tool: Retrieve decoder schema
    
    Returns:
        Dictionary with decoder schema
    """
    try:
        return load_decoder_schema()
    except Exception as e:
        print(f"Error retrieving decoder schema: {e}")
        return {}


def retrieve_table_definitions() -> pd.DataFrame:
    """
    MCP Tool: Retrieve table definitions
    
    Returns:
        DataFrame with table definitions
    """
    try:
        from data_loader import load_table_defs
        return load_table_defs()
    except Exception as e:
        print(f"Error retrieving table definitions: {e}")
        return pd.DataFrame()
