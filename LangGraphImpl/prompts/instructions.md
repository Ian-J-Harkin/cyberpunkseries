This specification is designed to bridge the gap between Narrative Design and Technical Implementation. It treats the novel as a "Stateful System" where the software ensures that the "Warm Neon" vibe and "Fraying Infrastructure" are mathematically impossible for the AI to ignore.

Technical Specification: The "Warm Neon" Narrative Engine
Target Architecture: LangGraph (Python)

State Management: Persistent TypedDict

1. The State Schema (The Continuity Log)
The "State" is the central repository of truth. Every agent reads from and writes to this object to prevent narrative drift.

Python
from typing import TypedDict, List, Annotated

class NarrativeState(TypedDict):
    # Narrative DNA
    governance: str             # The "Warm Neon" North Star
    boundaries: dict            # N/S/E/W World Compass
    
    # Character Data (The Persona Matrix)
    protagonist: dict           # Persona, Arc Version, Physical/Health status
    supporting_cast: List[dict] # Relational matrix and specific Voice Anchors
    
    # Material Continuity
    infrastructure: str         # Current "Fraying" level (80/20 Rule)
    inventory_log: List[str]    # Objects currently in play
    
    # Development
    scene_beats: List[str]      # The structural plan for the current chapter
    manuscript: str             # The cumulative prose generated
    vault_access_level: int     # 0 = Earthside only, 1 = Lunar secrets accessible
2. Node Definitions (The Agent Roles)
Node A: The Narrative DNA Architect
Role: Initializes the session by injecting the Governance and World Compass into the state.
Prompt Logic: Uses Structured Output to generate `governance`, `boundaries`, and `infrastructure` dynamically by reading `physics_doc.txt`.

Node B: The Structural Scene Plotter
Role: Generates granular beats for the chapter.
Prompt Logic: Reads the requested volume of beats from `scene_plotter.txt` and outputs a Pydantic `BeatList`.

Node C: The Persona-Driven Drafter
Role: The primary prose engine.
Prompt Logic: Converts the audited beat into prose applying Voice Anchors, limiting Vocabulary Quarantines, and obeying Formulating Rules.

Node D: The Continuity Extractor
Role: Updates the State after each scene.
Prompt Logic: Uses Structured JSON to track Vig collections (inventory item losses dictated by LLM logic), Trust updates, Lucidity triggers (Ad-Man Oracle caps dictated by law), and provides the `Rolling State`.

3. Edge Logic (Information Gating)
To manage The Vault (The Lunar Secrets), the system uses a Conditional Edge wrapping the Drafter.
Rule: If vault_access_level < 1, the Drafter receives a masked version of the World_Compass where the Moon's true nature is dynamically pulled from the `[VAULT_MASK]` section in `physics_doc.txt`.

4. The "Character Matrix" Logic (Supporting Cast)
To prevent secondary characters from becoming "generic," each entry in the supporting_cast list must include:

Internal Frequency: (e.g., Ad-Man’s "Neural-Scraped Sloganeering").

Noticing Rule: What this character specifically notices about the protagonist (e.g., "Sarge notices the protagonist's biometric errors").

Physical Anchor: (e.g., Glimmer’s "ozone tea and cushion height").

Implementation Instructions for the Programming Agent
"Generate a Python LangGraph implementation using StateGraph. Define nodes for dna_architect, scene_plotter, persona_drafter, and continuity_extractor. Use a SqliteSaver for persistent checkpointer memory so the 'Continuity Log' survives between different writing sessions. Ensure all system prompts for the nodes are modular and pulled from external .txt files in the Knowledge Base."

