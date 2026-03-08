"""
prompts.py — All LangChain ChatPromptTemplates for the Narrative Physics Engine.
One template per pipeline stage. Import and invoke directly in nodes.py.
"""

from langchain_core.prompts import ChatPromptTemplate


# ---------------------------------------------------------------------------
# Stage 1 — Physics Document
# Variables: {premise}, {genre_tone}
# ---------------------------------------------------------------------------

PHYSICS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Narrative Architect specialising in sci-fi/fantasy world-building. "
     "Your task is to define the physical laws of a story universe as a precise, "
     "structured document. Every rule you write must be actionable — specific enough "
     "that a writer can check a scene against it and know whether it passes or fails."),
    ("human",
     "My story: {premise}\n\n"
     "Genre and tone: {genre_tone}\n\n"
     "Generate a Narrative Physics Document structured exactly as follows. "
     "Write each rule as a positive law ('X must happen') not a prohibition.\n\n"
     "---\nNARRATIVE PHYSICS DOCUMENT\n---\n\n"
     "CAUSALITY LAWS\n"
     "3-5 unbreakable laws governing how events cause consequences in this story. "
     "Example: 'Every major obstacle can only be resolved by a character using skills "
     "or knowledge established before the obstacle appears.'\n\n"
     "RESOURCE / STAKES SYSTEM\n"
     "2-3 finite resources characters must spend to achieve goals (physical, social, "
     "or psychological). State what replenishes each (if anything) and what happens "
     "when they run out.\n\n"
     "INFORMATION ECONOMY\n"
     "Rules governing how knowledge flows. Characters may only act on information "
     "they actually possess. Include any special conditions (communication lag, "
     "unreliable sources, information gatekeepers).\n\n"
     "ESCALATION RULE\n"
     "The mechanism by which pressure increases across the story. What happens when "
     "characters fail, delay, or make the wrong choice?\n\n"
     "TONAL PHYSICS\n"
     "2-3 rules specific to this genre/tone that must shape every scene. "
     "Example: 'Hope must always be present but always cost something.'\n"
     "---\n\n"
     "Return the document only. No commentary, no preamble.")
])


# ---------------------------------------------------------------------------
# Stage 2 — Character State Machine
# Variables: {physics_doc}, {character_name}, {character_description}
# ---------------------------------------------------------------------------

CHARACTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Character Systems Designer. You do not write prose. "
     "You define the operating rules of characters as precise, checkable "
     "specifications — wounds, strategies, and behavioural palettes that a "
     "writer or AI can consult before writing any scene."),
    ("human",
     "NARRATIVE PHYSICS DOCUMENT (for context):\n{physics_doc}\n\n"
     "CHARACTER TO DEFINE:\n"
     "Name: {character_name}\n"
     "Description: {character_description}\n\n"
     "Build a Character State Machine structured exactly as follows:\n\n"
     "---\nCHARACTER STATE MACHINE: {character_name}\n---\n\n"
     "CORE WOUND\n"
     "The specific formative experience creating their central fear or belief. "
     "Be concrete: not 'they fear abandonment' but the specific event, what they "
     "concluded from it, and how that conclusion now governs their behaviour.\n\n"
     "FLAWED STRATEGY\n"
     "The coping mechanism they use to avoid confronting the wound. Must be specific "
     "enough that it generates plot problems.\n\n"
     "BEHAVIOURAL PALETTES\n"
     "How this character behaves in four emotional states. "
     "Give 3-4 specific, observable behaviours for each — "
     "things that could appear directly in a scene:\n\n"
     "Baseline (safe, in control): [list 3-4 behaviours]\n"
     "Mild Stress (something's wrong but manageable): [list 3-4 behaviours]\n"
     "Extreme Pressure (crisis): [list 3-4 behaviours]\n"
     "Rare Vulnerability (guard fully down): [list 3-4 behaviours]\n\n"
     "ARC VERSIONS\n"
     "Act 1 version: Who are they before the story changes them?\n"
     "Midpoint version: How has pressure begun to crack the flawed strategy?\n"
     "End version: Who have they become — changed or broken?\n"
     "---\n\n"
     "Return the document only. No prose, no commentary.")
])


# ---------------------------------------------------------------------------
# Stage 3 — Relationship Force Field
# Variables: {char_a}, {char_b}, {machine_a}, {machine_b}, {physics_doc}
# ---------------------------------------------------------------------------

RELATIONSHIP_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a Relationship Architect. You define the dynamic between two "
     "characters as a structural system — not a description of how they feel "
     "about each other, but the rules governing how they interact, conflict, "
     "and occasionally connect."),
    ("human",
     "CHARACTER A: {char_a}\n"
     "CHARACTER A STATE MACHINE:\n{machine_a}\n\n"
     "CHARACTER B: {char_b}\n"
     "CHARACTER B STATE MACHINE:\n{machine_b}\n\n"
     "NARRATIVE PHYSICS DOCUMENT:\n{physics_doc}\n\n"
     "Build a Relationship Force Field structured exactly as follows:\n\n"
     "---\nRELATIONSHIP FORCE FIELD: {char_a} / {char_b}\n---\n\n"
     "TENSION AXIS\n"
     "The fundamental opposition between them. Frame as a pull in two directions "
     "(e.g. 'Trust vs. Self-Preservation'). This axis must be present in nearly "
     "every scene they share.\n\n"
     "POWER DYNAMIC\n"
     "Who has power, of what kind, and does it shift? Be specific about type: "
     "knowledge, authority, emotional leverage, physical, moral.\n\n"
     "FRICTION PATTERNS\n"
     "3 specific recurring ways conflict flares between them. Each must be rooted "
     "in their individual wounds, not just 'they disagree'.\n\n"
     "CONNECTION PATTERNS\n"
     "2-3 specific conditions under which they find genuine ease or closeness. "
     "These should feel hard-won given the friction patterns.\n\n"
     "RELATIONAL ARC\n"
     "Three phases: beginning state, rupture point, resolution or permanent fracture.\n"
     "---\n\n"
     "Return the document only. No prose, no commentary.")
])


# ---------------------------------------------------------------------------
# Stage 4 — Scene Drafting Engine
# Variables: {physics_doc}, {character_context}, {relationship_context},
#            {rolling_state}, {act_position}, {previous_scene_summary},
#            {scene_plot_function}, {new_state_goal},
#            {character_knowledge}, {character_emotional_states}
# ---------------------------------------------------------------------------

DRAFTING_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Lead Writer on a sci-fi/fantasy project. "
     "You write scenes that follow strict narrative rules. "
     "Before writing a single word of prose, you consult all provided documents "
     "and check every character decision against their state machine. "
     "You write in prose only — no headers, no stage directions, no commentary."),
    ("human",
     "---\nNARRATIVE PHYSICS DOCUMENT\n---\n{physics_doc}\n\n"
     "---\nCHARACTER STATE MACHINES\n---\n{character_context}\n\n"
     "---\nRELATIONSHIP FORCE FIELD\n---\n{relationship_context}\n\n"
     "---\nROLLING STATE (what has happened so far)\n---\n{rolling_state}\n\n"
     "---\nSCENE BRIEF\n---\n"
     "Act position: {act_position}\n"
     "What just happened: {previous_scene_summary}\n"
     "What must happen in this scene: {scene_plot_function}\n"
     "What must change by the end: {new_state_goal}\n"
     "What each character currently knows: {character_knowledge}\n"
     "Current emotional states: {character_emotional_states}\n\n"
     "---\nDRAFTING RULES — FOLLOW ALL OF THESE\n---\n"
     "1. Every character action must be consistent with their current arc version "
     "and active behavioural palette.\n"
     "2. No character may act on information they do not possess as listed above.\n"
     "3. The problem in this scene may not be resolved by coincidence or external rescue.\n"
     "4. The scene must end in a New State — something is concretely different "
     "from how it began.\n"
     "5. Use the world's physics to create pressure. The environment and its rules "
     "are an antagonist.\n"
     "6. Dialogue must sound distinct for each character — cross-reference their "
     "wound and flawed strategy before writing any line.\n"
     "---\n\n"
     "Now draft the scene. Prose only.")
])


# ---------------------------------------------------------------------------
# Stage 5 — Rolling State Update
# Variables: {previous_rolling_state}, {scene_draft}
# ---------------------------------------------------------------------------

ROLLING_STATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are the Script Supervisor on this project. "
     "Your job is continuity and state-tracking — not prose. "
     "You produce concise, structured summaries that will be fed directly "
     "into the next scene's drafting prompt. Precision matters more than style."),
    ("human",
     "PREVIOUS ROLLING STATE:\n{previous_rolling_state}\n\n"
     "SCENE JUST WRITTEN:\n{scene_draft}\n\n"
     "Produce a Rolling State Update. "
     "Format as concise bullet points only under these exact headings:\n\n"
     "CHARACTER STATES\n"
     "- For each character who appeared: current emotional state "
     "(reference their behavioural palette by name), any arc version shift, "
     "any relationship change\n\n"
     "INFORMATION LEDGER\n"
     "- What each character now knows that they did not before\n"
     "- What they still do not know that the reader does\n\n"
     "PHYSICS LEDGER\n"
     "- Resources spent\n"
     "- Physics laws tested or under pressure\n"
     "- Consequences now in motion that must be paid off\n\n"
     "PLOT HOOKS\n"
     "- Primary hook: the immediate unresolved tension the next scene must address\n"
     "- Secondary hook: a slower-burn thread now in motion\n\n"
     "Return bullet points only. No prose, no preamble.")
])
