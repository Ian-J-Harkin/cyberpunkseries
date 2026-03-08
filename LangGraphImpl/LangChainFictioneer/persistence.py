"""
persistence.py — Checkpointer configuration and EngineStore load/save helpers.

The EngineStore is serialised as JSON and stored under a fixed key in the
LangGraph SQLite checkpoint. One DB file = one project. To start a new
project, point DB_PATH at a new file or call reset_store().
"""

import json
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from state import EngineStore


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default DB path — override by passing db_path to get_checkpointer()
DEFAULT_DB_PATH = "narrative_engine.db"

# Thread ID used for all checkpoints in a single project.
# Each project should use its own DB file; thread ID stays constant.
THREAD_ID = "narrative-engine-main"

# Key under which the EngineStore JSON is stored in checkpoint state
STORE_KEY = "engine_store_json"


# ---------------------------------------------------------------------------
# Checkpointer
# ---------------------------------------------------------------------------

def get_checkpointer(db_path: str = DEFAULT_DB_PATH) -> SqliteSaver:
    """
    Return a SqliteSaver checkpointer backed by the given DB file.
    The file is created automatically if it doesn't exist.

    For production use, swap for PostgresSaver:
        from langgraph.checkpoint.postgres import PostgresSaver
        return PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])
    """
    return SqliteSaver.from_conn_string(db_path)


def get_config(thread_id: str = THREAD_ID) -> dict:
    """Return the LangGraph config dict for a given thread."""
    return {"configurable": {"thread_id": thread_id}}


# ---------------------------------------------------------------------------
# EngineStore serialisation helpers
# ---------------------------------------------------------------------------

def store_to_json(store: EngineStore) -> str:
    """Serialise an EngineStore to a JSON string."""
    return store.model_dump_json()


def store_from_json(raw: str) -> EngineStore:
    """Deserialise an EngineStore from a JSON string."""
    return EngineStore.model_validate_json(raw)


# ---------------------------------------------------------------------------
# Load / save from checkpoint state dict
# ---------------------------------------------------------------------------

def load_store_from_state(state: dict) -> EngineStore:
    """
    Extract and deserialise the EngineStore from a LangGraph state dict.
    Returns a fresh empty EngineStore if none exists yet.
    """
    raw = state.get(STORE_KEY)
    if not raw:
        return EngineStore()
    return store_from_json(raw)


def save_store_to_state(state: dict, store: EngineStore) -> dict:
    """
    Serialise the EngineStore and write it into the state dict.
    Returns the updated state dict.
    """
    state[STORE_KEY] = store_to_json(store)
    return state


# ---------------------------------------------------------------------------
# File export helpers (optional, for human-readable backups)
# ---------------------------------------------------------------------------

def export_store_to_file(store: EngineStore, path: str = "engine_store_backup.json") -> None:
    """Write the current EngineStore to a JSON file for inspection or backup."""
    Path(path).write_text(store.model_dump_json(indent=2), encoding="utf-8")
    print(f"Engine store exported to {path}")


def import_store_from_file(path: str) -> EngineStore:
    """Load an EngineStore from a previously exported JSON file."""
    raw = Path(path).read_text(encoding="utf-8")
    return store_from_json(raw)


def export_scenes_to_markdown(store: EngineStore, path: str = "scenes_output.md") -> None:
    """
    Append all scenes in the store's history to a Markdown file.
    Safe to call repeatedly — uses 'a' mode so existing content is preserved.
    """
    with open(path, "a", encoding="utf-8") as f:
        for scene in store.scene_history:
            scene_num = scene.get("scene_number", "?")
            act = scene.get("act_position", "")
            brief = scene.get("brief", "")
            draft = scene.get("draft", "")
            timestamp = scene.get("timestamp", "")

            f.write(f"\n\n---\n")
            f.write(f"## Scene {scene_num} — {act}\n")
            f.write(f"*{timestamp}*\n\n")
            f.write(f"**Brief:** {brief}\n\n")
            f.write(draft)
            f.write("\n")

    print(f"Scenes exported to {path}")


def reset_store(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Delete the SQLite DB file to start a fresh project.
    Use with caution — this is irreversible.
    """
    p = Path(db_path)
    if p.exists():
        p.unlink()
        print(f"Deleted {db_path}. Engine store reset.")
    else:
        print(f"No DB file found at {db_path}. Nothing to reset.")
