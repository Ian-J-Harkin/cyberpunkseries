"""
graphs.py — LangGraph graph definitions for the Narrative Physics Engine.

Two compiled graphs are exported:
  setup_graph   — runs once per project, builds the EngineStore
  writing_graph — runs once per scene, drafts and updates rolling state
"""

from langgraph.graph import StateGraph, END
from langgraph.types import Send

from nodes import (
    node_generate_physics,
    node_generate_character,
    node_collect_characters,
    node_generate_relationship,
    node_collect_relationships,
    node_build_engine_store,
    node_load_engine_store,
    node_assemble_context,
    node_draft_scene,
    node_generate_rolling_state,
    node_update_engine_store,
    route_characters,
    route_relationships,
)
from persistence import get_checkpointer


# ---------------------------------------------------------------------------
# Setup Pipeline Graph
# ---------------------------------------------------------------------------
#
# Flow:
#   generate_physics
#       ↓
#   [fan-out via route_characters]
#       → generate_character (×N, parallel)
#       ↓
#   collect_characters
#       ↓
#   [fan-out via route_relationships]
#       → generate_relationship (×M, parallel)
#       ↓
#   collect_relationships
#       ↓
#   build_engine_store
#       ↓
#   END


def build_setup_graph(checkpointer=None) -> StateGraph:
    """
    Construct and compile the setup pipeline graph.
    Pass a checkpointer to enable persistence between runs.
    """
    graph = StateGraph(dict)

    # --- Node registration ---
    graph.add_node("generate_physics", node_generate_physics)
    graph.add_node("generate_character", node_generate_character)
    graph.add_node("collect_characters", node_collect_characters)
    graph.add_node("generate_relationship", node_generate_relationship)
    graph.add_node("collect_relationships", node_collect_relationships)
    graph.add_node("build_engine_store", node_build_engine_store)

    # --- Entry point ---
    graph.set_entry_point("generate_physics")

    # --- Physics → character fan-out ---
    # route_characters returns a list of Send objects, one per character
    graph.add_conditional_edges(
        "generate_physics",
        route_characters,
        ["generate_character"],
    )

    # --- Character fan-in → collect ---
    # All generate_character tasks converge here
    graph.add_edge("generate_character", "collect_characters")

    # --- Characters → relationship fan-out ---
    graph.add_conditional_edges(
        "collect_characters",
        route_relationships,
        ["generate_relationship"],
    )

    # --- Relationship fan-in → collect ---
    graph.add_edge("generate_relationship", "collect_relationships")

    # --- Relationships → build store → END ---
    graph.add_edge("collect_relationships", "build_engine_store")
    graph.add_edge("build_engine_store", END)

    return graph.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Writing Loop Graph
# ---------------------------------------------------------------------------
#
# Flow:
#   load_engine_store
#       ↓
#   assemble_context
#       ↓
#   draft_scene
#       ↓
#   generate_rolling_state
#       ↓
#   update_engine_store
#       ↓
#   END


def build_writing_graph(checkpointer=None) -> StateGraph:
    """
    Construct and compile the writing loop graph.
    Pass a checkpointer to enable EngineStore persistence.
    """
    graph = StateGraph(dict)

    # --- Node registration ---
    graph.add_node("load_engine_store", node_load_engine_store)
    graph.add_node("assemble_context", node_assemble_context)
    graph.add_node("draft_scene", node_draft_scene)
    graph.add_node("generate_rolling_state", node_generate_rolling_state)
    graph.add_node("update_engine_store", node_update_engine_store)

    # --- Linear chain ---
    graph.set_entry_point("load_engine_store")
    graph.add_edge("load_engine_store", "assemble_context")
    graph.add_edge("assemble_context", "draft_scene")
    graph.add_edge("draft_scene", "generate_rolling_state")
    graph.add_edge("generate_rolling_state", "update_engine_store")
    graph.add_edge("update_engine_store", END)

    return graph.compile(checkpointer=checkpointer)


# ---------------------------------------------------------------------------
# Convenience factory — get compiled graphs with shared checkpointer
# ---------------------------------------------------------------------------

def get_graphs(db_path: str = "narrative_engine.db"):
    """
    Return both compiled graphs sharing a single SQLite checkpointer.
    This ensures setup and writing loop share the same persisted state.

    Usage:
        setup_graph, writing_graph = get_graphs()
    """
    checkpointer = get_checkpointer(db_path)
    return (
        build_setup_graph(checkpointer=checkpointer),
        build_writing_graph(checkpointer=checkpointer),
    )
