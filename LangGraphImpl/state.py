from typing import TypedDict, List


class SupportingCast(TypedDict):
    name: str
    internal_frequency: str   # e.g. Ad-Man's "Neural-Scraped Sloganeering"
    noticing_rule: str        # What this character notices about the protagonist
    physical_anchor: str      # e.g. Glimmer's "ozone tea and cushion height"
    trust_level: int          # 0-100


class Protagonist(TypedDict):
    name: str
    mbti: str                 # ESTP
    enneagram: str            # 7w8
    arc_version: str          # Which chapter-arc the protagonist is currently on
    physical_status: str      # e.g. "No injuries"
    health_flags: List[str]   # Active conditions / modifiers


class SceneBrief(TypedDict):
    act_position: str
    previous_scene_summary: str
    scene_plot_function: str
    new_state_goal: str
    character_knowledge: str
    character_emotional_states: str
    physical_status: str
    health_flags: List[str]


class NarrativeState(TypedDict):
    """The Continuity Log — Central repository of truth.
    
    Every agent reads from and writes to this object to prevent narrative drift.
    Field names match the spec in instructions.md exactly.
    """
    # Narrative DNA
    governance: str           # The "Warm Neon" North Star
    boundaries: dict          # N/S/E/W World Compass (masked when vault_access_level < 1)

    # Character Data (The Persona Matrix)
    protagonist: Protagonist
    supporting_cast: List[SupportingCast]

    # Material Continuity
    infrastructure: str       # Current "Fraying" level (80/20 Rule)
    inventory_log: List[str]  # Objects currently in play
    
    # Specific Character Mechanics
    lucidity_counts: dict       # Tracks {"empathy": 0, "vault": 0, "schmuck": 0}
    medical_debt_percent: int   # Starts at 20

    # Development
    scene_beats: List[str]    # Structural plan for the current chapter
    current_beat_index: int   # Tracks which beat is being drafted
    scene_brief: SceneBrief
    rolling_state: str
    manuscript: str           # The cumulative prose generated

    # Vault
    vault_access_level: int   # 0 = Earthside only, 1 = Lunar secrets accessible
