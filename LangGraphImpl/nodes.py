import os
import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from state import NarrativeState
from context import build_system_prompt

# ── LLM selection ──────────────────────────────────────────────────────────────
if os.environ.get("GEMINI_API_KEY"):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.7,
        google_api_key=os.environ.get("GEMINI_API_KEY")
    )
else:
    llm = ChatOpenAI(
        model="openai/gpt-4o",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
        temperature=0.7
    )


# ── Node A: DNA Architect ─────────────────────────────────────────────────────
def dna_architect(state: NarrativeState) -> dict:
    """Injects governance and boundaries into state.
    
    Receives the Series Bible + Character Matrix as global context,
    so its understanding of the world is grounded from the first token.
    """
    system_prompt = build_system_prompt("dna_architect.txt")

    context = (
        f"Current Infrastructure (Fraying Level): {state.get('infrastructure', 'Unknown')}\n"
        f"Protagonist: {json.dumps(state.get('protagonist', {}), indent=2)}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Initialize the narrative DNA for this session.\n\n{context}")
    ]
    response = llm.invoke(messages)

    try:
        parsed = json.loads(response.content)
        return {
            "governance":    parsed.get("governance", response.content[:120]),
            "boundaries":    parsed.get("boundaries", {"north": "TBD", "south": "TBD", "east": "TBD", "west": "TBD"}),
            "infrastructure": parsed.get("infrastructure", state.get("infrastructure", "Moderate fraying"))
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "governance": response.content[:120],
            "boundaries": {"north": "TBD", "south": "TBD", "east": "TBD", "west": "TBD"}
        }


# ── Node B: Scene Plotter ─────────────────────────────────────────────────────
def scene_plotter(state: NarrativeState) -> dict:
    """Generates 10-15 raw beats — friction enforcement happens in the Auditor."""
    system_prompt = build_system_prompt("scene_plotter.txt")

    protagonist = state.get("protagonist", {})
    context = (
        f"Protagonist MBTI: {protagonist.get('mbti', 'ESTP')}\n"
        f"Protagonist Enneagram: {protagonist.get('enneagram', '7w8')}\n"
        f"Arc Version: {protagonist.get('arc_version', 'Chapter 1')}\n"
        f"Infrastructure: {state.get('infrastructure', 'Unknown')}\n"
        f"Governance: {state.get('governance', '')}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Generate 10-15 scene beats for the current chapter.\n\n{context}")
    ]
    response = llm.invoke(messages)

    beats = [b.strip() for b in response.content.split("\n") if b.strip()]
    return {
        "scene_beats": beats,
        "current_beat_index": 0
    }


# ── Node B½: Friction Auditor ─────────────────────────────────────────────────
def friction_auditor(state: NarrativeState) -> dict:
    """Dedicated critic node (translated from n8n Step 3).
    
    Reviews the plotter's raw beats and enforces:
    - The 80/20 Friction Quota (one Friction Event per 3 beats)
    - Motion check (no internal brooding beats)
    - Vocabulary Quarantine
    Marks modified beats with [AUDITED] so the drafter knows what changed.
    """
    system_prompt = build_system_prompt("friction_auditor.txt")

    raw_beats = state.get("scene_beats", [])
    beat_text = "\n".join(f"{i+1}. {b}" for i, b in enumerate(raw_beats))

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Audit and revise these scene beats:\n\n{beat_text}")
    ]
    response = llm.invoke(messages)

    audited_beats = [b.strip() for b in response.content.split("\n") if b.strip()]
    return {"scene_beats": audited_beats}


# ── Node C: Persona Drafter ───────────────────────────────────────────────────
# Receives beats AFTER the Auditor has enforced friction. Boundaries may be
# masked at graph level (_masked_drafter in graph.py) before this is called.
def persona_drafter(state: NarrativeState) -> dict:
    """Drafts prose from the current (audited) beat using Voice Anchor rules."""
    system_prompt = build_system_prompt("persona_drafter.txt")

    beats = state.get("scene_beats", [])
    index = state.get("current_beat_index", 0)
    current_beat = beats[index] if index < len(beats) else "No beat available."

    compass_context = json.dumps(state.get("boundaries", {}), indent=2)
    cast_context    = json.dumps(state.get("supporting_cast", []), indent=2)

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Current Beat: {current_beat}\n\n"
                f"World Compass (boundaries):\n{compass_context}\n\n"
                f"Supporting Cast:\n{cast_context}"
            )
        )
    ]
    response = llm.invoke(messages)

    existing = state.get("manuscript", "")
    updated_manuscript = (existing + "\n\n" + response.content).strip()
    return {"manuscript": updated_manuscript}


# ── Node D: Continuity Extractor ──────────────────────────────────────────────
def continuity_extractor(state: NarrativeState) -> dict:
    """Analyzes new prose; updates inventory and cast trust; logs state changes.
    
    The SessionLog is written here (mirrors n8n Step 5 → database write).
    The log object is passed in via state['_session_log'] by engine.py.
    """
    system_prompt = build_system_prompt("continuity_extractor.txt")

    latest_prose    = state.get("manuscript", "")
    current_inv     = state.get("inventory_log", [])
    current_cast    = state.get("supporting_cast", [])

    instruction = (
        "Analyze the latest prose excerpt and return a JSON object with these keys:\n"
        "  inventory_additions: list of new items gained\n"
        "  inventory_removals: list of items lost/used\n"
        "  trust_updates: list of {name, delta} objects for NPCs whose trust changed\n"
        "  infrastructure_update: updated fraying description string, or null if unchanged\n\n"
        f"Current inventory: {json.dumps(current_inv)}\n"
        f"Current cast: {json.dumps(current_cast)}\n\n"
        f"Latest prose (last 2000 chars):\n{latest_prose[-2000:]}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=instruction)
    ]
    response = llm.invoke(messages)

    try:
        updates = json.loads(response.content)
    except (json.JSONDecodeError, AttributeError):
        updates = {}

    # Apply inventory changes
    new_inventory = list(current_inv)
    for item in updates.get("inventory_additions", []):
        if item not in new_inventory:
            new_inventory.append(item)
    for item in updates.get("inventory_removals", []):
        new_inventory = [i for i in new_inventory if i != item]

    # Apply trust deltas
    cast_by_name = {c["name"]: dict(c) for c in current_cast}
    trust_changes = {}
    for entry in updates.get("trust_updates", []):
        name  = entry.get("name")
        delta = entry.get("delta", 0)
        if name in cast_by_name:
            old = cast_by_name[name].get("trust_level", 50)
            cast_by_name[name]["trust_level"] = max(0, min(100, old + delta))
            trust_changes[name] = delta
    updated_cast = list(cast_by_name.values())

    # Write to session log (mirrors n8n → database write)
    session_log = state.get("_session_log")
    beat_index  = state.get("current_beat_index", 0)
    beats       = state.get("scene_beats", [])
    beat_text   = beats[beat_index] if beat_index < len(beats) else "N/A"

    if session_log is not None:
        if new_inventory != current_inv:
            session_log.record("INVENTORY_CHANGE", {
                "beat": beat_text,
                "added":   updates.get("inventory_additions", []),
                "removed": updates.get("inventory_removals", [])
            })
        if trust_changes:
            session_log.record("TRUST_UPDATE", {
                "beat": beat_text,
                "changes": trust_changes
            })
        if updates.get("infrastructure_update"):
            session_log.record("INFRASTRUCTURE_UPDATE", {
                "beat":  beat_text,
                "value": updates["infrastructure_update"]
            })

    result = {
        "inventory_log":   new_inventory,
        "supporting_cast": updated_cast,
        "current_beat_index": beat_index + 1
    }
    infra = updates.get("infrastructure_update")
    if infra:
        result["infrastructure"] = infra

    return result
