# Warm Neon Narrative Engine - Implementation Walkthrough

The LangGraph architecture for the Warm Neon narrative engine is now fully implemented. This document details the completed components, how they interact, and instructions for running the pipeline locally.

## 1. Directory Structure & Knowledge Base

The repository is structured neatly at `c:\Github\AI_Fiction\cyberpunkseries\LangGraphImpl`:

- `prompts/`: Contains the modular text prompts for each agent.
  - `series_bible.txt` (Narrative Physics Document — Causality Laws, Tonal Physics)
  - `character_matrix.txt` (Character State Machines — Wounds, Strategies, 4-state Palettes)
  - `relationship_matrix.txt` (Relationship Force Fields — Tension Axes, Friction Patterns)
  - `dna_architect.txt`, `scene_plotter.txt`, `friction_auditor.txt`, `persona_drafter.txt`, `continuity_extractor.txt`
- `state.py`: Defines the `NarrativeState` typed dictionary and sub-schemas, including `SceneBrief`.
- `context.py`: Handles global prompt injection (Physics Doc + State Machines + Force Fields) and manages the structured `SessionLog`.
- `nodes.py`: Houses the LangGraph nodes. The architect and plotter now use Pydantic `with_structured_output`, and the extractor guarantees strict JSON continuity updates. No "how" or "why" logic exists in the Python file.
- `graph.py`: Constructs the `StateGraph` and defines the execution flow.
- `engine.py`: The terminal-based entry point script. It uses `parse_character_matrix` to dynamically load character text blocks so Python doesn't hardcode them.
- `ui.py`: The **Streamlit Frontend** that provides a real-time visual dashboard of the graph's execution.

## 2. Global Context & Friction Auditing

The architecture features a 5-node chain of thought:
1. **DNA Architect**
2. **Scene Plotter**
3. **Friction Auditor** (Enforces friction quota, motion checks, and vocabulary quarantine before prose is drafted)
4. **Persona Drafter** (Enforces 6 Formal Drafting Rules: arc versions, information economy, causal resolution)
5. **Continuity Extractor** (Produces both a JSON Continuity Delta and a narrative Rolling State Update)

Every node receives the `series_bible.txt`, `character_matrix.txt`, and `relationship_matrix.txt` automatically injected into its system prompt by `context.py`. This ensures universal world consistency: characters operate within their defined State Machines, and the world obeys the overarching Narrative Physics.

## 3. The Conditional Logic (The Vault)

In `graph.py`, a graph-level wrapper (`_masked_drafter`) enforces the "Vault Access" rules. If `vault_access_level < 1`, the literal boundaries dictionary is replaced with an "Industrial Rumors" mask *before* the drafting node sees the state, creating a hard firewall.

## 4. Persistent Memory & Session Logs

The engine uses three layers of state permanence:
1. `langgraph-checkpoint-sqlite`: Saves the raw entire graph state between runs.
2. **Session Event Logs**: The Continuity Extractor writes discrete state-changes (Inventory gains/losses, Trust deltas, Lucidity updates, and Medical Debt increases) into a human-readable, queryable JSONL file at `logs/warm_neon_session_1.jsonl`.
3. **Rolling State**: A human-readable text ledger updated every scene (Character States, Information Ledger, Physics Ledger) that feeds forward into the *next* scene's drafting prompt.

## 5. Specific Character Mechanics & Prompt-Driven "De-coding"
The engine has been fully "de-coded"—meaning that logic governing *how* characters behave, *how many* beats are generated, and *what* the physical boundaries are, is no longer written in Python.

- **Dynamic Characters**: Characters are parsed seamlessly via text-blocks from `character_matrix.txt` on boot.
- **The Vig (`medical_loan_balance`)**: The LLM autonomously determines the narrative fit for which item to confiscate based strictly on instructions in `continuity_extractor.txt`, removing `import random` bounds from python.
- **The Lucidity Oracle`: Caps on Ad-Man's clarity (Empathy, Vault-Knowledge, Schmuck-Rage) and the `[VAULT_MASK]` are read textually from the `physics_doc.txt` as a "Systemic Law."
- **Governance & Geography**: The DNA architect reads the state and populates the world geometry mapping without Python fallbacks.

## 6. How to Run

You have two options to run the narrative engine:

### Option A: The Streamlit Dashboard (Recommended)
This provides a live visual interface to watch the graph execute, see the state updates, and monitor the event log. You do *not* need to set API keys in the terminal; you can enter them directly into the UI sidebar.

```powershell
cd c:\Github\AI_Fiction\cyberpunkseries\LangGraphImpl
streamlit run ui.py
```

### Option B: The Terminal Engine
If you prefer standard out, you must configure an LLM provider by setting the environment variable in your terminal first. 

**Termimal (Gemini):**
```powershell
$env:GEMINI_API_KEY="your-gemini-key"
```

**Terminal (OpenRouter):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-api-key"
```

Then execute the engine script:

```powershell
cd c:\Github\AI_Fiction\cyberpunkseries\LangGraphImpl
python engine.py
```

You will see output streamed from the StateGraph as each node iteratively generates the north star, scene beats, and prose drafts.
