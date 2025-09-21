from typing import Dict, Any, List
from tools.retrieval import retrieve_encoder_params

"""
Encoder Tools — MCP tool for working with encoder parameters.
"""

def get_encoder_params() -> Dict[str, Any]:
    return retrieve_encoder_params()


def filter_encoders_by_codec(codec: str) -> List[Dict[str, Any]]:
    data = retrieve_encoder_params()
    results = []
    for enc_id, enc_data in data.items():
        if enc_data.get("codec", "").lower() == codec.lower():
            results.append({"ENCODER_ID": enc_id, **enc_data})
    return results


def list_all_encoders() -> List[Dict[str, Any]]:
    data = retrieve_encoder_params()
    return [{"ENCODER_ID": enc_id, **enc_data} for enc_id, enc_data in data.items()]


def summarize_encoders() -> str:
    data = retrieve_encoder_params()
    total = len(data)
    codecs = {}
    for enc in data.values():
        codec = enc.get("codec", "Unknown")
        codecs[codec] = codecs.get(codec, 0) + 1

    summary = f"There are {total} encoders available. "
    summary += "The codec distribution is as follows:\n"
    for codec, count in codecs.items():
        summary += f"- {codec}: {count} encoders\n"
    return summary.strip()
