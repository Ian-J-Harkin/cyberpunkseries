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
Role: Initializes the session by injecting the North Star and World Compass into the state.

Prompt Logic: "Ensure the environment is defined by low-grade friction and bureaucratic hurdles. Set the 'Fraying Level' for the current location."

Node B: The Structural Scene Plotter
Role: Generates 10-15 granular beats for the chapter.

Prompt Logic: "Follow the Protagonist's MBTI (ESTP) and Enneagram (7w8). Every three beats, an external 'Friction Event' (broken tech or paperwork) must obstruct progress. No internal brooding; keep the character in motion."

Node C: The Persona-Driven Drafter
Role: The primary prose engine.

Prompt Logic: "Convert the current beat into prose. Apply the Voice Anchor (Elmore Leonard/Will Smith). Enforce Vocabulary Quarantines (e.g., no 'shimmering', 'hacker', or 'chrome'). Describe Glimmer's physical limitations (cushion-propped autoimmunity) through the protagonist's unimpressed-but-curious lens."

Node D: The Continuity Extractor
Role: Updates the State after each scene.

Prompt Logic: "Analyze the new draft. Did the protagonist lose/gain an item? Did an NPC's trust level change? Did a piece of infrastructure break? Update the inventory_log and cast_matrix accordingly."

3. Edge Logic (Information Gating)
To manage The Vault (The Lunar Secrets), the system uses a Conditional Edge. This ensures the "Drafter" node is physically incapable of "leaking" the secret until the "Plotter" node triggers the discovery.

Rule: If vault_access_level < 1, the Drafter receives a masked version of the World_Compass where the Moon's true nature (Computational Drift/Mineral Euphoria) is replaced with "Industrial Rumors."

4. The "Character Matrix" Logic (Supporting Cast)
To prevent secondary characters from becoming "generic," each entry in the supporting_cast list must include:

Internal Frequency: (e.g., Ad-Man’s "Neural-Scraped Sloganeering").

Noticing Rule: What this character specifically notices about the protagonist (e.g., "Sarge notices the protagonist's biometric errors").

Physical Anchor: (e.g., Glimmer’s "ozone tea and cushion height").

Implementation Instructions for the Programming Agent
"Generate a Python LangGraph implementation using StateGraph. Define nodes for dna_architect, scene_plotter, persona_drafter, and continuity_extractor. Use a SqliteSaver for persistent checkpointer memory so the 'Continuity Log' survives between different writing sessions. Ensure all system prompts for the nodes are modular and pulled from external .txt files in the Knowledge Base."

