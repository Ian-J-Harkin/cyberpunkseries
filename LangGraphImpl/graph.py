import copy
from typing import Literal
from langgraph.graph import StateGraph, START, END
from state import NarrativeState
from nodes import (
    dna_architect,
    scene_plotter,
    friction_auditor,
    persona_drafter,
    continuity_extractor
)

# ── Vault mask constants ───────────────────────────────────────────────────────
_MASKED_BOUNDARIES = {
    "north": "Industrial Rumors",
    "south": "Industrial Rumors",
    "east":  "Industrial Rumors",
    "west":  "Industrial Rumors",
    "_note": "The Moon's true nature (Computational Drift/Mineral Euphoria) is classified."
}

def _masked_drafter(state: NarrativeState) -> dict:
    """Graph-level vault wrapper around persona_drafter.
    
    When vault_access_level < 1, BOUNDARIES are swapped for Industrial Rumors
    BEFORE the LLM ever touches the state. Physically incapable of leaking
    the lunar secret — equivalent to n8n's If/Else hard firewall.
    """
    if state.get("vault_access_level", 0) < 1:
        masked = dict(state)
        masked["boundaries"] = copy.deepcopy(_MASKED_BOUNDARIES)
        return persona_drafter(masked)
    return persona_drafter(state)

# ── Routing functions ──────────────────────────────────────────────────────────
def should_continue(state: NarrativeState) -> Literal["persona_drafter", "__end__"]:
    """Loop back for the next beat, or end when all beats are exhausted."""
    beats = state.get("scene_beats", [])
    index = state.get("current_beat_index", 0)
    if index < len(beats):
        return "persona_drafter"
    return END

# ── Graph builder ──────────────────────────────────────────────────────────────
def build_graph():
    builder = StateGraph(NarrativeState)

    # Nodes
    builder.add_node("dna_architect",        dna_architect)
    builder.add_node("scene_plotter",        scene_plotter)
    builder.add_node("friction_auditor",     friction_auditor)   # ← NEW: n8n Step 3
    builder.add_node("persona_drafter",      _masked_drafter)    # vault-aware
    builder.add_node("continuity_extractor", continuity_extractor)

    # Fixed edges
    builder.add_edge(START,             "dna_architect")
    builder.add_edge("dna_architect",   "scene_plotter")
    builder.add_edge("scene_plotter",   "friction_auditor")     # ← beats go to auditor first
    builder.add_edge("friction_auditor","persona_drafter")      # ← audited beats go to drafter
    builder.add_edge("persona_drafter", "continuity_extractor")

    # Beat loop: after extraction, draft next beat or end
    builder.add_conditional_edges("continuity_extractor", should_continue)

    return builder
