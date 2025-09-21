# improvement_codegen/utils.py
"""
Cursor AI-Generated Utility Functions

This module provides utility functions for the agentic query system:
- Data processing and analysis
- System information display
- Helper functions for clarity computation
- Demo query generation
"""

import pandas as pd
import json
from typing import Dict, List, Any, Optional


def compute_clarity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute clarity score for camera feeds
    
    Args:
        df: DataFrame with camera feed data
        
    Returns:
        DataFrame with added CLARITY column
    """
    df = df.copy()
    df["CLARITY"] = df["RES_W"] * df["RES_H"]
    return df


def display_system_info(workflow_info: Dict[str, Any]) -> None:
    """
    Display system information in a formatted way
    
    Args:
        workflow_info: Dictionary with workflow information
    """
    print(f"   Workflow Type: {workflow_info.get('workflow_type', 'Unknown')}")
    
    if 'nodes' in workflow_info:
        print(f"   Nodes: {', '.join(workflow_info['nodes'])}")
    
    if 'mcp_tools' in workflow_info:
        print(f"   MCP Tools: {', '.join(workflow_info['mcp_tools'])}")
    
    if 'features' in workflow_info:
        print(f"   Features: {', '.join(workflow_info['features'])}")


def get_demo_queries() -> List[str]:
    """
    Get a list of demo queries for testing
    
    Returns:
        List of demo query strings
    """
    return [
        "What are the camera IDs in the Pacific region with the best clarity?",
        "Show me the highest frame rate feeds in Europe",
        "Which feeds have the lowest latency in CONUS?",
        "What are the encoder parameters?",
        "Compare performance metrics across all regions",
        "Are the Pacific feeds encrypted?",
        "What is the average frame rate of Pacific feeds compared to Europe?",
        "Find all feeds using H265 codec",
        "Show me feeds with resolution higher than 1920x1080",
        "What are the decoder parameters?"
    ]


def format_query_response(query: str, data: Any, response_type: str = "feeds") -> str:
    """
    Format query response based on data type and query context with natural language
    
    Args:
        query: Original query string
        data: Response data
        response_type: Type of response (feeds, encoder, decoder)
        
    Returns:
        Formatted natural language response string
    """
    if response_type == "feeds":
        if isinstance(data, pd.DataFrame):
            if len(data) == 0:
                return "I couldn't find any camera feeds matching your criteria. Please try adjusting your search parameters."
            
            # Format DataFrame response with natural language
            if "camera id" in query.lower() or "camera ids" in query.lower():
                camera_ids = data["FEED_ID"].tolist()
                if len(camera_ids) == 1:
                    return f"I found 1 camera feed: {camera_ids[0]}"
                else:
                    return f"I found {len(camera_ids)} camera feeds: {', '.join(camera_ids)}"
            else:
                # Provide natural language summary
                total_feeds = len(data)
                regions = data["THEATER"].unique().tolist() if "THEATER" in data.columns else []
                
                response_parts = [f"I found {total_feeds} camera feeds"]
                if regions:
                    response_parts.append(f"across {len(regions)} region(s): {', '.join(regions)}")
                
                response_parts.append("Here are the details:")
                for i, (_, row) in enumerate(data.head(5).iterrows()):
                    feed_info = f"  {i+1}. {row['FEED_ID']}"
                    if "THEATER" in row:
                        feed_info += f" ({row['THEATER']})"
                    if "FRRATE" in row:
                        feed_info += f" - {row['FRRATE']} fps"
                    if "LAT_MS" in row:
                        feed_info += f", {row['LAT_MS']} ms latency"
                    if "CLARITY" in row:
                        feed_info += f", {row['CLARITY']:,} pixels"
                    response_parts.append(feed_info)
                
                return "\n".join(response_parts)
        
        elif isinstance(data, dict):
            # Format comparison or analysis results with natural language
            if "PAC" in data or "EUR" in data or "ME" in data or "CONUS" in data:
                formatted = ["Here's a comparison across regions:"]
                for region, stats in data.items():
                    formatted.append(f"\n{region} region:")
                    formatted.append(f"  • {stats['feed_count']} camera feeds")
                    formatted.append(f"  • Average frame rate: {stats['avg_frame_rate']} fps")
                    formatted.append(f"  • Average latency: {stats['avg_latency']} ms")
                    formatted.append(f"  • Average clarity: {stats['avg_clarity']:,} pixels")
                return "\n".join(formatted)
            else:
                # Generic dict formatting
                formatted = ["Here's what I found:"]
                for key, value in data.items():
                    if isinstance(value, dict):
                        formatted.append(f"\n{key.replace('_', ' ').title()}:")
                        for sub_key, sub_value in value.items():
                            formatted.append(f"  • {sub_key.replace('_', ' ').title()}: {sub_value}")
                    else:
                        formatted.append(f"  • {key.replace('_', ' ').title()}: {value}")
                return "\n".join(formatted)
    
    elif response_type in ["encoder", "decoder"]:
        if isinstance(data, dict):
            formatted = [f"Here are the {response_type} parameters:"]
            
            # Group parameters by category
            categories = {
                "codec": [],
                "quality": [],
                "performance": [],
                "other": []
            }
            
            for key, value in data.items():
                if key in ["codec", "profile", "level", "preset", "tune"]:
                    categories["codec"].append(f"  • {key.replace('_', ' ').title()}: {value}")
                elif key in ["bit_depth", "chroma_subsampling", "color_primaries", "transfer_characteristics", "deblock", "sao", "denoise"]:
                    categories["quality"].append(f"  • {key.replace('_', ' ').title()}: {value}")
                elif key in ["framerate", "gop_size", "b_frames", "ref_frames", "bitrate_kbps", "max_threads", "dpb_size"]:
                    categories["performance"].append(f"  • {key.replace('_', ' ').title()}: {value}")
                else:
                    categories["other"].append(f"  • {key.replace('_', ' ').title()}: {value}")
            
            # Add categories that have content
            if categories["codec"]:
                formatted.append("\nCodec Configuration:")
                formatted.extend(categories["codec"])
            
            if categories["quality"]:
                formatted.append("\nQuality Settings:")
                formatted.extend(categories["quality"])
            
            if categories["performance"]:
                formatted.append("\nPerformance Settings:")
                formatted.extend(categories["performance"])
            
            if categories["other"]:
                formatted.append("\nOther Settings:")
                formatted.extend(categories["other"])
            
            return "\n".join(formatted)
    
    return f"Here's what I found: {str(data)}"


def analyze_feeds_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze camera feeds performance metrics
    
    Args:
        df: DataFrame with camera feed data
        
    Returns:
        Dictionary with performance analysis
    """
    analysis = {}
    
    # Overall statistics
    analysis["total_feeds"] = len(df)
    analysis["unique_regions"] = df["THEATER"].nunique()
    analysis["unique_codecs"] = df["CODEC"].nunique()
    
    # Performance metrics
    analysis["avg_frame_rate"] = round(df["FRRATE"].mean(), 2)
    analysis["avg_latency"] = round(df["LAT_MS"].mean(), 2)
    analysis["avg_clarity"] = round(df["CLARITY"].mean(), 2)
    
    # Regional analysis
    regional_stats = {}
    for region in df["THEATER"].unique():
        region_data = df[df["THEATER"] == region]
        regional_stats[region] = {
            "feed_count": len(region_data),
            "avg_frame_rate": round(region_data["FRRATE"].mean(), 2),
            "avg_latency": round(region_data["LAT_MS"].mean(), 2),
            "avg_clarity": round(region_data["CLARITY"].mean(), 2)
        }
    analysis["regional_stats"] = regional_stats
    
    # Codec analysis
    codec_stats = {}
    for codec in df["CODEC"].unique():
        codec_data = df[df["CODEC"] == codec]
        codec_stats[codec] = {
            "feed_count": len(codec_data),
            "avg_frame_rate": round(codec_data["FRRATE"].mean(), 2),
            "avg_latency": round(codec_data["LAT_MS"].mean(), 2),
            "avg_clarity": round(codec_data["CLARITY"].mean(), 2)
        }
    analysis["codec_stats"] = codec_stats
    
    return analysis


def generate_performance_report(df: pd.DataFrame, output_file: Optional[str] = None) -> str:
    """
    Generate a comprehensive performance report
    
    Args:
        df: DataFrame with camera feed data
        output_file: Optional output file path
        
    Returns:
        Report content as string
    """
    analysis = analyze_feeds_performance(df)
    
    report = []
    report.append("=" * 80)
    report.append("CAMERA FEEDS PERFORMANCE REPORT")
    report.append("=" * 80)
    
    # Overall statistics
    report.append(f"\nOVERALL STATISTICS:")
    report.append(f"  Total Feeds: {analysis['total_feeds']}")
    report.append(f"  Unique Regions: {analysis['unique_regions']}")
    report.append(f"  Unique Codecs: {analysis['unique_codecs']}")
    report.append(f"  Average Frame Rate: {analysis['avg_frame_rate']} fps")
    report.append(f"  Average Latency: {analysis['avg_latency']} ms")
    report.append(f"  Average Clarity: {analysis['avg_clarity']} pixels")
    
    # Regional analysis
    report.append(f"\nREGIONAL ANALYSIS:")
    for region, stats in analysis["regional_stats"].items():
        report.append(f"  {region}:")
        report.append(f"    Feeds: {stats['feed_count']}")
        report.append(f"    Avg Frame Rate: {stats['avg_frame_rate']} fps")
        report.append(f"    Avg Latency: {stats['avg_latency']} ms")
        report.append(f"    Avg Clarity: {stats['avg_clarity']} pixels")
    
    # Codec analysis
    report.append(f"\nCODEC ANALYSIS:")
    for codec, stats in analysis["codec_stats"].items():
        report.append(f"  {codec}:")
        report.append(f"    Feeds: {stats['feed_count']}")
        report.append(f"    Avg Frame Rate: {stats['avg_frame_rate']} fps")
        report.append(f"    Avg Latency: {stats['avg_latency']} ms")
        report.append(f"    Avg Clarity: {stats['avg_clarity']} pixels")
    
    report.append("\n" + "=" * 80)
    
    report_content = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_content)
        print(f"Report saved to: {output_file}")
    
    return report_content


def validate_query_syntax(query: str) -> Dict[str, Any]:
    """
    Validate query syntax and provide suggestions
    
    Args:
        query: Natural language query string
        
    Returns:
        Dictionary with validation results
    """
    validation = {
        "valid": True,
        "suggestions": [],
        "warnings": []
    }
    
    query_lower = query.lower()
    
    # Check for common query patterns
    if not any(keyword in query_lower for keyword in ["camera", "feed", "encoder", "decoder", "pacific", "europe", "latency", "clarity", "frame"]):
        validation["warnings"].append("Query doesn't contain common camera feed keywords")
    
    # Check for region keywords
    regions = ["pacific", "europe", "middle east", "conus", "pac", "eur", "me"]
    if not any(region in query_lower for region in regions):
        validation["suggestions"].append("Consider specifying a region (Pacific, Europe, Middle East, CONUS)")
    
    # Check for metric keywords
    metrics = ["clarity", "resolution", "frame rate", "framerate", "latency"]
    if not any(metric in query_lower for metric in metrics):
        validation["suggestions"].append("Consider specifying a metric (clarity, frame rate, latency)")
    
    return validation


def get_system_status() -> Dict[str, Any]:
    """
    Get current system status and health information
    
    Returns:
        Dictionary with system status
    """
    status = {
        "data_loader": "operational",
        "mcp_tools": "operational", 
        "langgraph_workflow": "operational",
        "cursor_ai": "operational",
        "overall_status": "healthy"
    }
    
    # Check data directory
    data_dir = "../Data"
    if not os.path.exists(data_dir):
        status["data_loader"] = "error"
        status["overall_status"] = "degraded"
    
    # Check required files
    required_files = [
        "Table_feeds_v2.csv",
        "encoder_params.json",
        "decoder_params.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(data_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        status["data_loader"] = "warning"
        status["overall_status"] = "degraded"
    
    return status


def pretty_print_feeds(df: pd.DataFrame, columns: Optional[List[str]] = None, max_rows: int = 5) -> None:
    """
    Print a clean summary of camera feeds for analysts
    
    Args:
        df: DataFrame with camera feed data
        columns: Optional list of columns to display
        max_rows: Maximum number of rows to display
    """
    if columns:
        print(df[columns].head(max_rows))
    else:
        print(df.head(max_rows))


def get_cursor_insights() -> Dict[str, Any]:
    """
    Get insights about the Cursor AI integration
    
    Returns:
        Dictionary with Cursor AI insights
    """
    return {
        "features": [
            "AI-powered query understanding",
            "Dynamic code generation",
            "Intelligent workflow orchestration",
            "MCP tool integration",
            "Natural language processing",
            "Context-aware responses"
        ],
        "capabilities": [
            "Real-time code generation",
            "Adaptive query processing",
            "Multi-modal data handling",
            "Error recovery and fallbacks",
            "Performance optimization"
        ],
        "benefits": [
            "Reduced development time",
            "Improved code quality",
            "Enhanced user experience",
            "Scalable architecture",
            "Maintainable codebase"
        ]
    }