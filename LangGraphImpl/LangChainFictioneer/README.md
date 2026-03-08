# Narrative Physics Engine

An AI-assisted fiction writing pipeline built with LangChain and LangGraph.
Implements constraint system prompting — defining the rules of your story's universe
so the AI reasons within them rather than pattern-matching against generic fiction.

## Architecture

Two LangGraph pipelines share a single SQLite-backed state store:

**Setup Pipeline** (run once per project)
```
generate_physics → [fan-out] generate_character (×N) → collect_characters
                → [fan-out] generate_relationship (×M) → collect_relationships
                → build_engine_store
```

**Writing Loop** (run once per scene)
```
load_engine_store → assemble_context → draft_scene
                 → generate_rolling_state → update_engine_store
```

## Files

| File | Purpose |
|---|---|
| `state.py` | Pydantic models — EngineStore, input models, graph state dicts |
| `prompts.py` | All ChatPromptTemplates, one per pipeline stage |
| `persistence.py` | SQLite checkpointer config, load/save helpers, export utilities |
| `nodes.py` | All LangGraph node functions |
| `graphs.py` | Graph definitions and compiled graph factory |
| `main.py` | Typer CLI — setup, write, status, export, reset commands |

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
ANTHROPIC_API_KEY=your_key_here
```

## Usage

**1. Run setup once per project:**
```bash
python main.py setup
```
You'll be prompted for:
- Story premise (2-3 sentences)
- Genre and tone
- Characters (Name | description, one per line)
- Relationship pairs to map (Name A | Name B)

This runs the setup pipeline using **Claude Opus** and saves everything
to `narrative_engine.db`.

---

**2. Write a scene:**
```bash
python main.py write
```
You'll be prompted for the scene brief — characters, act position,
what must happen, what must change, what each character knows,
and their current emotional states.

The pipeline assembles your physics doc, relevant character state machines,
and relationship force fields automatically, then drafts the scene using
**Claude Sonnet** and generates a rolling state update.

---

**3. Check project status:**
```bash
python main.py status
```

**4. Export everything to Markdown and JSON:**
```bash
python main.py export
# Writes: scenes_output.md, engine_store_backup.json
```

**5. Start a new project:**
```bash
python main.py reset
# or use a different DB file:
python main.py setup --db-path my_new_project.db
```

## Model Routing

| Pipeline | Model | Reason |
|---|---|---|
| Setup (all stages) | `claude-opus-4-6` | Runs once; quality of physics/character docs matters |
| Scene drafting | `claude-sonnet-4-6` | Runs per scene; strong prose, lower cost |
| Rolling state update | `claude-sonnet-4-6` | Structured summary; doesn't need Opus |

To swap models, edit the `opus` and `sonnet` instances at the top of `nodes.py`.

## Switching to Postgres (Production)

In `persistence.py`, replace:
```python
from langgraph.checkpoint.sqlite import SqliteSaver
return SqliteSaver.from_conn_string(db_path)
```
with:
```python
from langgraph.checkpoint.postgres import PostgresSaver
return PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])
```

## LangSmith Tracing (Optional)

Add to your `.env`:
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=narrative-physics-engine
```

All LLM calls will appear in your LangSmith dashboard for prompt debugging.
