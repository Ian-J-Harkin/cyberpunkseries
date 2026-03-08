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

def _masked_drafter(state: NarrativeState) -> dict:
    """Graph-level vault wrapper around persona_drafter.
    
    When vault_access_level < 1, BOUNDARIES are swapped for the text under
    [VAULT_MASK] in physics_doc.txt BEFORE the LLM ever touches the state.
    """
    if state.get("vault_access_level", 0) < 1:
        masked = dict(state)
        
        from context import load_prompt
        import re
        physics_text = load_prompt("physics_doc.txt")
        mask_match = re.search(r'\[VAULT_MASK\]\n(.*)', physics_text, re.DOTALL)
        
        mask_dict = {}
        if mask_match:
            for line in mask_match.group(1).strip().split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    mask_dict[k.strip()] = v.strip()
                    
        masked["boundaries"] = mask_dict if mask_dict else {"error": "mask not found in physics_doc"}
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
