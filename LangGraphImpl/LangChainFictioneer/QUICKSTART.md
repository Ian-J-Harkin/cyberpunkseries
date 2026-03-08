# Narrative Physics Engine — Quick Start

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
ANTHROPIC_API_KEY=your_key_here
```

---

## Step 1 — Setup (once per project)

```bash
python main.py setup
```

You will be prompted for:

- **Story premise** — 2-3 sentences describing your world and central conflict
- **Genre and tone** — e.g. *Hard sci-fi, bleak tone, The Expanse-style realism*
- **Characters** — one per line, format: `Name | brief description`
- **Relationship pairs** — one per line, format: `Name A | Name B`

This generates your Physics Document, Character State Machines, and Relationship Force Fields using Claude Opus, and saves everything to `narrative_engine.db`.

---

## Step 2 — Write a Scene (once per scene)

```bash
python main.py write
```

You will be prompted for the scene brief:

- Which characters are in the scene
- Act position (selected from a numbered list)
- What just happened (previous scene summary)
- What must happen in this scene
- What must change by the end
- What each character currently knows
- Current emotional states (e.g. `Kael: Mild Stress, Sova: Extreme Pressure`)

The pipeline assembles your physics doc, relevant character machines, and relationship force fields automatically, drafts the scene with Claude Sonnet, and generates a rolling state update. Repeat for every scene.

---

## Other Commands

```bash
# Print current project status and rolling state
python main.py status

# Export all scenes to scenes_output.md and engine_store_backup.json
python main.py export

# Delete the DB and start a fresh project
python main.py reset

# Use a different DB file (e.g. for a second project)
python main.py setup --db-path my_second_project.db
python main.py write --db-path my_second_project.db
```

---

## Notes

- The `narrative_engine.db` file is your entire project state — back it up alongside your manuscript
- Run `python main.py export` regularly to keep a human-readable Markdown copy of your scenes
- To enable LangSmith tracing for prompt debugging, add `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY=your_langsmith_key` to your `.env`
