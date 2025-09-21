from typing import Dict, Any, List
from tools.retrieval import retrieve_decoder_params

"""
Decoder Tools — MCP tool for working with decoder parameters.
"""

def get_decoder_params() -> Dict[str, Any]:
    return retrieve_decoder_params()


def filter_decoders_by_codec(codec: str) -> List[Dict[str, Any]]:
    data = retrieve_decoder_params()
    results = []
    for dec_id, dec_data in data.items():
        if dec_data.get("codec", "").lower() == codec.lower():
            results.append({"DECODER_ID": dec_id, **dec_data})
    return results


def list_all_decoders() -> List[Dict[str, Any]]:
    data = retrieve_decoder_params()
    return [{"DECODER_ID": dec_id, **dec_data} for dec_id, dec_data in data.items()]


def summarize_decoders() -> str:
    data = retrieve_decoder_params()
    total = len(data)
    codecs = {}
    for dec in data.values():
        codec = dec.get("codec", "Unknown")
        codecs[codec] = codecs.get(codec, 0) + 1

    summary = f"There are {total} decoders available. "
    summary += "The codec distribution is as follows:\n"
    for codec, count in codecs.items():
        summary += f"- {codec}: {count} decoders\n"
    return summary.strip()
