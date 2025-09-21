# tools/__init__.py
"""
MCP Tools Package for Camera Feed Query System

This package contains modular MCP (Model Context Protocol) tools for:
- Data retrieval operations
- Data filtering operations  
- Data analysis operations
"""

from .retrieval import retrieve_feeds, retrieve_encoder_params, retrieve_decoder_params
from .filtering import filter_by_region, filter_by_metric, filter_by_encryption
from .analysis import analyze_performance, compare_regions, get_top_feeds

__all__ = [
    # Retrieval tools
    "retrieve_feeds",
    "retrieve_encoder_params", 
    "retrieve_decoder_params",
    
    # Filtering tools
    "filter_by_region",
    "filter_by_metric",
    "filter_by_encryption",
    
    # Analysis tools
    "analyze_performance",
    "compare_regions",
    "get_top_feeds",
]
