# Warm Neon Narrative Engine

A 5-node AI architecture built with LangGraph in Python. It simulates a low-grade, "frictional" cyberpunk environment where bureaucracy, failing infrastructure, and character-driven interactions guide the narrative. 

This engine is stateful, maintaining a persistent "Continuity Log" in a local SQLite database that stores inventory, NPC trust levels, environmental framing, and the ongoing manuscript. 

## Table of Contents
- [Quickstart: How to Run](#quickstart-how-to-run)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)

---

## Quickstart: How to Run

### Option 1: The Streamlit Dashboard (Recommended)

This provides a real-time, interactive visual interface where you can watch the AI agents generate scene beats, perform audits, draft the manuscript, and extract continuity updates (inventory/trust).

```powershell
pip install -r requirements.txt
streamlit run ui.py
```

*Note: You do not need to set API keys as environment variables beforehand. You can paste your **Gemini API Key** or **OpenRouter Key** directly into the sidebar of the web app.*

### Option 2: The Terminal Engine

If you prefer to run the raw python script in your terminal, you must first declare your LLM key as an environment variable. The engine prioritizes Gemini if both are present.

**For Gemini `gemini-1.5-pro` (Recommended):**
```powershell
$env:GEMINI_API_KEY="your-gemini-key"
```

**For OpenRouter (e.g. `openai/gpt-4o`):**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-your-key"
```

Then execute:
```powershell
python engine.py
```

---

## Architecture Overview

The pipeline executes a 5-step "Chain of Thought" loop.

1. **DNA Architect:** Initializes the session by pulling the global `series_bible.txt` and defining the current infrastructure / systemic friction of the world.
2. **Scene Plotter:** Proposes 10-15 granular narrative beats tailored to the protagonist's established MBTI/Enneagram traits. 
3. **Friction Auditor:** A specialized critic node. It reviews the immediate beats and enforces the "80/20 Rule" (must contain a physical friction event every 3 beats) and deletes any beats requiring "internal brooding."
4. **Persona Drafter:** The prose engine. It translates the *audited* beats into creative manuscript prose in the designated "Voice Anchor." It operates behind a **Vault Access Wall** — it is physically prevented from seeing classified world geography if the session's vault access level is zero.
5. **Continuity Extractor:** Analyzes the newly generated prose and executes a structured Pydantic tool call to extract exact `inventory_additions`, `inventory_removals`, and NPC `trust_updates` (-10 to +10). It logs these distinct state-changes to a JSONL file in the `logs/` directory for pure queryable history.

*The nodes then loop back to the Persona Drafter for the next beat until the scene concludes.*

---

## Project Structure

- `ui.py` — The Streamlit frontend dashboard.
- `engine.py` — The standalone terminal script and entry point.
- `graph.py` — LangGraph definitions, edge logic, and Vault-masking wrappers.
- `nodes.py` — The Python logic for the 5 agents + Pydantic schema upgrades.
- `state.py` — Typed dictionaries defining the "Continuity Log."
- `context.py` — Global Context injectors (Digital Library pattern) and the JSON Session Logging mechanism.
- `prompts/` — The true "Knowledge Base" holding all human-readable instructions and World Bibles.
- `logs/` — Distinct session history files generated during runs (`<session_id>.jsonl`).
- `checkpoints.sqlite` — Auto-generated persistent LangGraph database saving all historical state.
