"""
state.py — All data models for the Narrative Physics Engine.

EngineStore is the central persisted document.
Input models validate user-provided data.
Graph state dicts flow through LangGraph pipelines.
"""

from typing import Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class CharacterInput(BaseModel):
    name: str
    description: str


class RelationshipPairInput(BaseModel):
    char_a: str
    char_b: str


class SetupInput(BaseModel):
    premise: str
    genre_tone: str
    characters: list[CharacterInput]
    pairs: list[RelationshipPairInput]


class SceneBriefInput(BaseModel):
    characters_in_scene: list[str]
    act_position: str
    previous_scene_summary: str
    scene_plot_function: str
    new_state_goal: str
    character_knowledge: str
    character_emotional_states: str = ""


# ---------------------------------------------------------------------------
# Engine Store — the persisted heart of the system
# ---------------------------------------------------------------------------

class EngineStore(BaseModel):
    """
    Central state document. Written during setup, read and updated
    during every scene in the writing loop. Persisted via LangGraph
    SQLite checkpointer between sessions.
    """
    premise: str = ""
    genre_tone: str = ""

    # Generated during setup pipeline
    physics_doc: str = ""
    character_machines: dict[str, str] = Field(default_factory=dict)
    relationships: dict[str, str] = Field(default_factory=dict)

    # Updated after every scene in the writing loop
    rolling_state: str = "No scenes written yet. This is the start of the project."
    scene_history: list[dict[str, Any]] = Field(default_factory=list)

    setup_complete: bool = False

    def get_character(self, name: str) -> str:
        """Return character state machine doc, or a warning if not found."""
        return self.character_machines.get(
            name,
            f"[Warning: No state machine found for '{name}'. "
            "Add this character during setup.]"
        )

    def get_relationship(self, char_a: str, char_b: str) -> str:
        """Return relationship doc for a pair in either order, or empty string."""
        return (
            self.relationships.get(f"{char_a}_{char_b}")
            or self.relationships.get(f"{char_b}_{char_a}")
            or ""
        )

    def assemble_scene_context(self, brief: SceneBriefInput) -> dict[str, str]:
        """
        Pull all relevant documents for a scene brief into a single
        context dict ready for the drafting prompt.
        """
        chars = brief.characters_in_scene

        character_context = "\n\n".join(
            self.get_character(name) for name in chars
        )

        relationship_blocks = []
        for i in range(len(chars)):
            for j in range(i + 1, len(chars)):
                doc = self.get_relationship(chars[i], chars[j])
                if doc:
                    relationship_blocks.append(doc)

        relationship_context = "\n\n".join(relationship_blocks) or (
            "No relationship document defined for this pairing."
        )

        return {
            "physics_doc": self.physics_doc,
            "character_context": character_context,
            "relationship_context": relationship_context,
            "rolling_state": self.rolling_state,
        }


# ---------------------------------------------------------------------------
# LangGraph graph state dicts
# ---------------------------------------------------------------------------

class SetupGraphState(dict):
    """
    State dict flowing through the setup pipeline graph.

    Keys populated at each stage:
        setup_input         SetupInput
        physics_doc         str
        character_machines  dict[str, str]
        relationships       dict[str, str]
        engine_store        EngineStore
    """


class WritingGraphState(dict):
    """
    State dict flowing through the writing loop graph.

    Keys populated at each stage:
        scene_brief             SceneBriefInput
        engine_store            EngineStore
        scene_context           dict[str, str]
        scene_draft             str
        rolling_state_update    str
    """
