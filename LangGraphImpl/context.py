import os
import json
from datetime import datetime, timezone


# ── Global context loader ──────────────────────────────────────────────────────
_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")

def load_prompt(filename: str) -> str:
    """Load a single prompt file from the Knowledge Base."""
    path = os.path.join(_PROMPT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def parse_character_matrix(file_content: str) -> list[dict]:
    """Parse character_matrix.txt text blocks into SupportingCast dicts dynamically."""
    import re
    cast = []
    current_char = None
    char_data = {}
    
    for line in file_content.split('\n'):
        # Detect character headers dynamically
        if re.match(r'^(SUPPORTING CAST:|THE PATRON:|THE ENFORCERS:|THE ORACLE:|LUCE \(|ROOK —)', line):
            if current_char and "name" in char_data:
                cast.append(char_data)
            
            # Extract name
            name = "Unknown"
            if "GLIMMER" in line: name = "Glimmer"
            elif "CASTOR VINE" in line: name = "Castor Vine"
            elif "LUCE" in line: name = "Luce"
            elif "ROOK" in line: name = "Rook"
            elif "AD-MAN" in line: name = "Ad-Man"
            else: name = line.split(':')[0]
            
            current_char = name
            char_data = {
                "name": current_char,
                "internal_frequency": "",
                "noticing_rule": "",
                "physical_anchor": "",
                "trust_level": 50 # Default starting trust
            }
            continue

        if current_char:
            lower_line = line.lower()
            if "anchor" in lower_line:
                char_data["physical_anchor"] = str(char_data.get("physical_anchor", "")) + line + " "
            elif "rule" in lower_line or "palette" in lower_line or "trigger" in lower_line:
                char_data["noticing_rule"] = str(char_data.get("noticing_rule", "")) + line + " "
            elif len(line.strip()) > 0:
                char_data["internal_frequency"] = str(char_data.get("internal_frequency", "")) + line + " "

    if current_char and "name" in char_data:
        cast.append(char_data)

    # Clean up empty strings and generic headers
    for c in cast:
        for k in ["internal_frequency", "noticing_rule", "physical_anchor"]:
            c[k] = c[k].strip() or "See character matrix for details."
            
    # Filter out generic grouping headers
    cast = [c for c in cast if c["name"] not in ["THE ENFORCERS", "Unknown"]]
    
    return cast


def load_global_context() -> str:
    """Load the Series Bible, Character Matrix, and Relationship Force Fields.
    
    This mirrors the n8n 'Digital Library' step: every node receives
    the same shared world foundation prepended to its system prompt,
    so no agent can develop an inconsistent picture of the world.
    """
    bible   = load_prompt("series_bible.txt")
    matrix  = load_prompt("character_matrix.txt")
    rels    = load_prompt("relationship_matrix.txt")
    physics = load_prompt("physics_doc.txt")  # Add this line
      
    return (
        "════════════════════════════════════════\n"
        "GLOBAL CONTEXT — NARRATIVE PHYSICS (SERIES BIBLE)\n"
        "════════════════════════════════════════\n"
        f"SERIES BIBLE:\n{bible}\n\n"
        f"PHYSICS LAWS:\n{physics}\n\n"
        "════════════════════════════════════════\n"
        "GLOBAL CONTEXT — CHARACTER STATE MACHINES\n"
        "════════════════════════════════════════\n"
        f"{matrix}\n\n"
        "════════════════════════════════════════\n"
        "GLOBAL CONTEXT — RELATIONSHIP FORCE FIELDS\n"
        "════════════════════════════════════════\n"
        f"{rels}\n\n"
        "════════════════════════════════════════\n"
        "NODE-SPECIFIC INSTRUCTIONS FOLLOW\n"
        "════════════════════════════════════════\n"
    )

def build_system_prompt(node_prompt_file: str) -> str:
    """Combine global context + node-specific instructions into one system prompt."""
    global_ctx   = load_global_context()
    node_prompt  = load_prompt(node_prompt_file)
    return global_ctx + node_prompt


# ── Session event log ──────────────────────────────────────────────────────────
class SessionLog:
    """Append-only structured JSON log of discrete state-change events.
    
    Mirrors the n8n Step 5 PostgreSQL/Airtable write — each continuity
    update is recorded as a timestamped event so the full session history
    is human-readable and queryable outside the graph checkpoint.
    """

    def __init__(self, session_id: str, log_dir: str | None = None):
        self.session_id = session_id
        log_dir = log_dir or os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        self.path = os.path.join(log_dir, f"{session_id}.jsonl")

    def record(self, event_type: str, payload: dict) -> None:
        """Append one event to the JSONL log."""
        entry = {
            "session_id":  self.session_id,
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "event_type":  event_type,
            "payload":     payload,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def read_all(self) -> list[dict]:
        """Return all events for this session as a list."""
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def summary(self) -> str:
        """Human-readable summary of all events so far."""
        events = self.read_all()
        if not events:
            return "No events logged yet."
        lines = [f"Session: {self.session_id} — {len(events)} events"]
        for e in events:
            ts = e["timestamp"][11:19]  # HH:MM:SS
            lines.append(f"  [{ts}] {e['event_type']}: {e['payload']}")
        return "\n".join(lines)
