import json
from typing import List, Dict, Any

def format_debate_data(json_data: List[Dict[str, Any]]) -> str:
    """
    Transforms debate JSON transcripts into an elegant, readable text format.
    """
    # If the input arrives as a raw string instead of a Python list, parse it
    if isinstance(json_data, str):
        json_data = json.loads(json_data)

    lines = []
    lines.append("=" * 60)
    lines.append("                   🔥 DEBATE TRANSCRIPT 🔥")
    lines.append("=" * 60 + "\n")

    for round_data in json_data:
        round_num = round_data.get("round_number", 1)
        lines.append(f"--- 📍 ROUND {round_num} 📍 ---")
        lines.append("-" * 30)

        for turn in round_data.get("turns", []):
            speaker = turn.get("agent_id", "Unknown Speaker")
            argument = turn.get("argument", "").strip()
            
            # Format speaker header nicely
            lines.append(f"🗣️  [{speaker}]:")
            lines.append(f"   \"{argument}\"")
            lines.append("") # Empty spacer line between turns
            
    lines.append("=" * 60)
    lines.append("                   📝 END OF TRANSCRIPT")
    lines.append("=" * 60)

    return "\n".join(lines)
