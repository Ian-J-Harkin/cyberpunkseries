import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
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
    scene_brief     = state.get("scene_brief", {})

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=(
                f"Current Beat: {current_beat}\n\n"
                f"Scene Brief:\n"
                f"- Act Position: {scene_brief.get('act_position', 'Unknown')}\n"
                f"- Plot Function: {scene_brief.get('scene_plot_function', 'Unknown')}\n"
                f"- New State Goal: {scene_brief.get('new_state_goal', 'Unknown')}\n"
                f"- Char Knowledge: {scene_brief.get('character_knowledge', 'Unknown')}\n"
                f"- Char Emotions: {scene_brief.get('character_emotional_states', 'Unknown')}\n\n"
                f"World Compass (boundaries):\n{compass_context}\n\n"
                f"Supporting Cast:\n{cast_context}"
            )
        )
    ]
    response = llm.invoke(messages)

    existing = state.get("manuscript", "")
    updated_manuscript = (existing + "\n\n" + response.content).strip()
    return {"manuscript": updated_manuscript}


# ── Continuity Extractor Schemas ──────────────────────────────────────────────
class TrustUpdate(BaseModel):
    name: str = Field(description="Name of the supporting cast member")
    delta: int = Field(description="Change in trust level (-10 to +10)")

class LucidityIncrements(BaseModel):
    empathy: int = Field(default=0)
    vault: int = Field(default=0)
    schmuck: int = Field(default=0)

class ContinuityUpdates(BaseModel):
    inventory_additions: List[str] = Field(default_factory=list, description="New items gained in the prose")
    inventory_removals: List[str] = Field(default_factory=list, description="Items lost or consumed in the prose")
    trust_updates: List[TrustUpdate] = Field(default_factory=list, description="Trust level changes for NPCs based on interactions")
    infrastructure_update: Optional[str] = Field(None, description="Updated fraying / infrastructure description, if mentioned")
    lucidity_increments: LucidityIncrements = Field(default_factory=LucidityIncrements, description="Lucidity moments triggered by Ad-Man")
    vig_collection_event: bool = Field(default=False, description="True if Dex refuses a job and Luce demands a portion of the vig")
    rolling_state_update: str = Field(description="The structured bullet-point ROLLING STATE UPDATE")


# ── Node D: Continuity Extractor ──────────────────────────────────────────────
def continuity_extractor(state: NarrativeState) -> dict:
    """Analyzes new prose; updates inventory and cast trust; logs state changes.
    
    Upgraded to use Pydantic `with_structured_output` for strict JSON enforcement.
    The SessionLog is written here.
    """
    system_prompt = build_system_prompt("continuity_extractor.txt")

    latest_prose    = state.get("manuscript", "")
    current_inv     = state.get("inventory_log", [])
    current_cast    = state.get("supporting_cast", [])
    current_rolling = state.get("rolling_state", "No rolling state yet.")

    instruction = (
        "Analyze the latest prose excerpt and extract structured continuity updates AND a rolling state update.\n\n"
        f"Previous Rolling State:\n{current_rolling}\n\n"
        f"Current inventory: {json.dumps(current_inv)}\n"
        f"Current cast: {json.dumps(current_cast)}\n\n"
        f"Latest prose (last 2000 chars):\n{latest_prose[-2000:]}"
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=instruction)
    ]
    
    # Use LangChain's structured output mechanism
    structured_llm = llm.with_structured_output(ContinuityUpdates)
    updates_obj = structured_llm.invoke(messages)

    if not updates_obj:
        updates_obj = ContinuityUpdates()

    # Apply inventory changes (includes Vig collection)
    new_inventory = list(current_inv)
    
    if getattr(updates_obj, "vig_collection_event", False) and new_inventory:
        import random
        removed_item = random.choice(new_inventory)
        new_inventory.remove(removed_item)
        if removed_item not in updates_obj.inventory_removals:
            updates_obj.inventory_removals.append(removed_item)

    for item in updates_obj.inventory_additions:
        if item not in new_inventory:
            new_inventory.append(item)
    for item in updates_obj.inventory_removals:
        new_inventory = [i for i in new_inventory if i != item]

    # Apply trust deltas
    cast_by_name = {c["name"]: dict(c) for c in current_cast}
    trust_changes = {}
    for update in updates_obj.trust_updates:
        if update.name in cast_by_name:
            old = cast_by_name[update.name].get("trust_level", 50)
            cast_by_name[update.name]["trust_level"] = max(0, min(100, old + update.delta))
            trust_changes[update.name] = update.delta
    updated_cast = list(cast_by_name.values())

    # Apply lucidity increments
    new_lucidity = dict(state.get("lucidity_counts", {"empathy": 0, "vault": 0, "schmuck": 0}))
    if updates_obj.lucidity_increments:
        new_lucidity["empathy"] += getattr(updates_obj.lucidity_increments, "empathy", 0)
        new_lucidity["vault"]   += getattr(updates_obj.lucidity_increments, "vault", 0)
        new_lucidity["schmuck"] += getattr(updates_obj.lucidity_increments, "schmuck", 0)

    # Medical loop balance stays persistent unless intentionally updated by other logic
    # The Vig collection event results in inventory loss instead of debt increase based on new rules
    new_medical_loan_balance = state.get("medical_loan_balance", 0.20)

    # Write to session log
    session_log = state.get("_session_log")
    beat_index  = state.get("current_beat_index", 0)
    beats       = state.get("scene_beats", [])
    beat_text   = beats[beat_index] if beat_index < len(beats) else "N/A"

    if session_log is not None:
        if new_inventory != current_inv:
            session_log.record("INVENTORY_CHANGE", {
                "beat": beat_text,
                "added":   updates_obj.inventory_additions,
                "removed": updates_obj.inventory_removals
            })
        if trust_changes:
            session_log.record("TRUST_UPDATE", {
                "beat": beat_text,
                "changes": trust_changes
            })
        if updates_obj.infrastructure_update:
            session_log.record("INFRASTRUCTURE_UPDATE", {
                "beat":  beat_text,
                "value": updates_obj.infrastructure_update
            })
        if getattr(updates_obj, "vig_collection_event", False):
            session_log.record("VIG_COLLECTION_EVENT", {
                "beat": beat_text,
                "action": "Inventory item removed due to job refusal"
            })
        if updates_obj.lucidity_increments:
            incs = {
                "empathy": getattr(updates_obj.lucidity_increments, "empathy", 0),
                "vault": getattr(updates_obj.lucidity_increments, "vault", 0),
                "schmuck": getattr(updates_obj.lucidity_increments, "schmuck", 0)
            }
            if any(v > 0 for v in incs.values()):
                session_log.record("LUCIDITY_UPDATE", {
                    "beat": beat_text,
                    "increments": incs
                })

    result = {
        "inventory_log":   new_inventory,
        "supporting_cast": updated_cast,
        "lucidity_counts": new_lucidity,
        "medical_loan_balance": new_medical_loan_balance,
        "current_beat_index": beat_index + 1,
        "rolling_state": getattr(updates_obj, "rolling_state_update", "") or state.get("rolling_state", "")
    }
    if updates_obj.infrastructure_update:
        result["infrastructure"] = updates_obj.infrastructure_update

    return result
