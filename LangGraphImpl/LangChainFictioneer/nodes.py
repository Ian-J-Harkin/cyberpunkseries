"""
nodes.py — All LangGraph node functions for the Narrative Physics Engine.

Each function takes a state dict and returns an updated state dict.
Nodes are pure functions — no side effects beyond LLM calls.
LLM model selection:
  - Setup pipeline  → claude-opus-4-6   (runs once, quality matters)
  - Writing loop    → claude-sonnet-4-6  (runs per scene, cost matters)
"""

from datetime import datetime

from langchain_anthropic import ChatAnthropic
from langgraph.types import Send

from prompts import (
    PHYSICS_PROMPT,
    CHARACTER_PROMPT,
    RELATIONSHIP_PROMPT,
    DRAFTING_PROMPT,
    ROLLING_STATE_PROMPT,
)
from persistence import load_store_from_state, save_store_to_state
from state import EngineStore, SceneBriefInput


# ---------------------------------------------------------------------------
# LLM instances
# ---------------------------------------------------------------------------

# Opus for setup — one-time document generation where quality is worth the cost
opus = ChatAnthropic(model="claude-opus-4-6", max_tokens=2048)

# Sonnet for writing loop — repeated calls, strong prose output
sonnet = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=3000)

# Sonnet for rolling state updates — structured summaries, doesn't need Opus
sonnet_state = ChatAnthropic(model="claude-sonnet-4-6", max_tokens=1000)


# ---------------------------------------------------------------------------
# Setup Pipeline Nodes
# ---------------------------------------------------------------------------

def node_generate_physics(state: dict) -> dict:
    """
    Stage 1 — Generate the Narrative Physics Document.
    Reads: state['setup_input']
    Writes: state['physics_doc']
    """
    setup = state["setup_input"]
    chain = PHYSICS_PROMPT | opus
    response = chain.invoke({
        "premise": setup.premise,
        "genre_tone": setup.genre_tone,
    })
    state["physics_doc"] = response.content
    return state


def node_generate_character(state: dict) -> dict:
    """
    Stage 2 — Generate a single Character State Machine.
    Called once per character via LangGraph Send API fan-out.
    Reads: state['character'], state['physics_doc']
    Writes: state['character_result'] = {name: doc}
    """
    character = state["character"]
    chain = CHARACTER_PROMPT | opus
    response = chain.invoke({
        "physics_doc": state["physics_doc"],
        "character_name": character.name,
        "character_description": character.description,
    })
    state["character_result"] = {character.name: response.content}
    return state


def node_collect_characters(state: dict) -> dict:
    """
    Collect fan-out results from node_generate_character into a single dict.
    Reads: state['character_results'] (list of {name: doc} dicts)
    Writes: state['character_machines']
    """
    character_machines = {}
    for result in state.get("character_results", []):
        character_machines.update(result)
    state["character_machines"] = character_machines
    return state


def node_generate_relationship(state: dict) -> dict:
    """
    Stage 3 — Generate a single Relationship Force Field.
    Called once per pair via LangGraph Send API fan-out.
    Reads: state['pair'], state['character_machines'], state['physics_doc']
    Writes: state['relationship_result'] = {"CharA_CharB": doc}
    """
    pair = state["pair"]
    machines = state["character_machines"]
    chain = RELATIONSHIP_PROMPT | opus

    machine_a = machines.get(pair.char_a, f"[No state machine for {pair.char_a}]")
    machine_b = machines.get(pair.char_b, f"[No state machine for {pair.char_b}]")

    response = chain.invoke({
        "char_a": pair.char_a,
        "char_b": pair.char_b,
        "machine_a": machine_a,
        "machine_b": machine_b,
        "physics_doc": state["physics_doc"],
    })

    key = f"{pair.char_a}_{pair.char_b}"
    state["relationship_result"] = {key: response.content}
    return state


def node_collect_relationships(state: dict) -> dict:
    """
    Collect fan-out results from node_generate_relationship.
    Reads: state['relationship_results'] (list of {"CharA_CharB": doc} dicts)
    Writes: state['relationships']
    """
    relationships = {}
    for result in state.get("relationship_results", []):
        relationships.update(result)
    state["relationships"] = relationships
    return state


def node_build_engine_store(state: dict) -> dict:
    """
    Assemble all setup outputs into the EngineStore and persist it.
    Reads: state['setup_input'], state['physics_doc'],
           state['character_machines'], state['relationships']
    Writes: state (with engine_store_json key via save_store_to_state)
    """
    setup = state["setup_input"]
    store = EngineStore(
        premise=setup.premise,
        genre_tone=setup.genre_tone,
        physics_doc=state["physics_doc"],
        character_machines=state["character_machines"],
        relationships=state["relationships"],
        setup_complete=True,
    )
    state = save_store_to_state(state, store)
    state["engine_store"] = store
    return state


# ---------------------------------------------------------------------------
# Fan-out router functions (used with LangGraph Send API)
# ---------------------------------------------------------------------------

def route_characters(state: dict) -> list[Send]:
    """
    Router: dispatch one node_generate_character task per character.
    Each task receives its own copy of the state with 'character' set.
    """
    setup = state["setup_input"]
    return [
        Send("generate_character", {
            **state,
            "character": char,
        })
        for char in setup.characters
    ]


def route_relationships(state: dict) -> list[Send]:
    """
    Router: dispatch one node_generate_relationship task per pair.
    """
    setup = state["setup_input"]
    machines = state["character_machines"]
    return [
        Send("generate_relationship", {
            **state,
            "pair": pair,
            "character_machines": machines,
        })
        for pair in setup.pairs
    ]


# ---------------------------------------------------------------------------
# Writing Loop Nodes
# ---------------------------------------------------------------------------

def node_load_engine_store(state: dict) -> dict:
    """
    Load the persisted EngineStore from checkpoint state.
    Reads: checkpoint state
    Writes: state['engine_store']
    """
    store = load_store_from_state(state)
    if not store.setup_complete:
        raise RuntimeError(
            "Engine store is empty or setup is incomplete. "
            "Run the setup pipeline first."
        )
    state["engine_store"] = store
    return state


def node_assemble_context(state: dict) -> dict:
    """
    Pull all relevant documents for the current scene brief.
    Reads: state['engine_store'], state['scene_brief']
    Writes: state['scene_context']
    """
    store: EngineStore = state["engine_store"]
    brief: SceneBriefInput = state["scene_brief"]
    state["scene_context"] = store.assemble_scene_context(brief)
    return state


def node_draft_scene(state: dict) -> dict:
    """
    Stage 4 — Draft the scene using the assembled context.
    Reads: state['scene_context'], state['scene_brief']
    Writes: state['scene_draft']
    """
    ctx = state["scene_context"]
    brief: SceneBriefInput = state["scene_brief"]
    chain = DRAFTING_PROMPT | sonnet

    response = chain.invoke({
        "physics_doc": ctx["physics_doc"],
        "character_context": ctx["character_context"],
        "relationship_context": ctx["relationship_context"],
        "rolling_state": ctx["rolling_state"],
        "act_position": brief.act_position,
        "previous_scene_summary": brief.previous_scene_summary,
        "scene_plot_function": brief.scene_plot_function,
        "new_state_goal": brief.new_state_goal,
        "character_knowledge": brief.character_knowledge,
        "character_emotional_states": brief.character_emotional_states,
    })

    state["scene_draft"] = response.content
    return state


def node_generate_rolling_state(state: dict) -> dict:
    """
    Stage 5 — Generate the Rolling State Update from the new scene.
    Reads: state['scene_draft'], state['engine_store'].rolling_state
    Writes: state['rolling_state_update']
    """
    store: EngineStore = state["engine_store"]
    chain = ROLLING_STATE_PROMPT | sonnet_state

    response = chain.invoke({
        "previous_rolling_state": store.rolling_state,
        "scene_draft": state["scene_draft"],
    })

    state["rolling_state_update"] = response.content
    return state


def node_update_engine_store(state: dict) -> dict:
    """
    Update the EngineStore with the new scene and rolling state,
    then persist it back to the checkpoint.
    Reads: state['engine_store'], state['scene_draft'],
           state['rolling_state_update'], state['scene_brief']
    Writes: state (with updated engine_store_json)
    """
    store: EngineStore = state["engine_store"]
    brief: SceneBriefInput = state["scene_brief"]
    scene_number = len(store.scene_history) + 1

    # Append scene to history
    store.scene_history.append({
        "scene_number": scene_number,
        "timestamp": datetime.now().isoformat(),
        "act_position": brief.act_position,
        "brief": brief.scene_plot_function,
        "draft": state["scene_draft"],
        "rolling_state_after": state["rolling_state_update"],
    })

    # Overwrite rolling state for next scene
    store.rolling_state = state["rolling_state_update"]

    # Persist back to checkpoint state
    state = save_store_to_state(state, store)
    state["engine_store"] = store
    state["scene_number"] = scene_number
    return state
