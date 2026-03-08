import os
from langgraph.checkpoint.sqlite import SqliteSaver
from graph import build_graph
from context import SessionLog, load_prompt, parse_character_matrix

def run():
    builder  = build_graph()
    db_path  = os.path.join(os.path.dirname(__file__), "checkpoints.sqlite")

    # ── Session identity ───────────────────────────────────────────────────────
    session_id = "warm_neon_session_1"
    config     = {"configurable": {"thread_id": session_id}}

    # ── Session event log (n8n Step 5 → database write equivalent) ────────────
    log_dir      = os.path.join(os.path.dirname(__file__), "logs")
    session_log  = SessionLog(session_id, log_dir=log_dir)

    with SqliteSaver.from_conn_string(db_path) as memory:
        graph = builder.compile(checkpointer=memory)

        # ── Initial State ──────────────────────────────────────────────────────
        matrix_text = load_prompt("character_matrix.txt")
        parsed_cast = parse_character_matrix(matrix_text)
        
        initial_state = {
            "vault_access_level": 0,

            "governance":  "",
            "boundaries":  {},

            "protagonist": {
                "name":            "Dex",
                "mbti":            "ESTP",
                "enneagram":       "7w8",
                "arc_version":     "Chapter 1 — Arrival",
                "physical_status": "No injuries",
                "health_flags":    []
            },

            "supporting_cast": parsed_cast,

            "infrastructure":    "High fraying — neon decay, acid rain, bureaucratic sludge",
            "inventory_log":     ["Stun baton", "Burner phone", "Flask of cheap synthetic whiskey"],
            "lucidity_counts":   {"empathy": 0, "vault": 0, "schmuck": 0},
            "medical_loan_balance": 0.20,
            "character_modifiers": {"Rook": "Stage 1 - Pre-Accident"},
            
            "scene_beats":       [],
            "current_beat_index": 0,
            
            "scene_brief": {
                "act_position": "Act 2 — RISING PRESSURE",
                "previous_scene_summary": "N/A",
                "scene_plot_function": "Luce offers Dex a job to skip-trace a runner. Dex must refuse because it crosses his moral line. Luce must then politely demand a 'portion of the vig' (repayment of the medical loan).",
                "new_state_goal": "Reduce Dex's inventory_log by one item and increase his medical_debt percentage.",
                "character_knowledge": "Dex knows he is low on cash. Luce is here to collect.",
                "character_emotional_states": "Dex is in a 'Handkerchief Check' stress loop (unconfirmed anxiety). Luce is the 'Reasonable Enforcer'.",
                "physical_status": "No injuries",
                "health_flags": []
            },
            "rolling_state": "No scenes written yet. A sub-franchise of Vine's organization just tossed Dex's place looking for a lead. Now Luce has arrived to 'talk'.",
            
            "manuscript":        "",

            # Pass the session log object through state so continuity_extractor can write to it.
            # NarrativeState is a TypedDict — extra keys are ignored by LangGraph but accessible.
            "_session_log": session_log
        }

        print("═" * 60)
        print(f"  Warm Neon Engine  |  Session: {session_id}")
        print("═" * 60)

        try:
            for event in graph.stream(initial_state, config):
                for node, state_update in event.items():
                    print(f"\n▸ {node}")

                    if "governance" in state_update:
                        print(f"  Governance: {state_update['governance'][:80]}...")
                    if "infrastructure" in state_update:
                        print(f"  Infrastructure: {state_update['infrastructure']}")
                    if "scene_beats" in state_update:
                        beats = state_update["scene_beats"]
                        audited = sum(1 for b in beats if "[AUDITED]" in b)
                        print(f"  Beats: {len(beats)} total, {audited} audited by Friction Auditor")
                        for i, b in enumerate(beats[:3], 1):
                            print(f"    {i}. {b[:90]}")
                        if len(beats) > 3:
                            print(f"    ... and {len(beats) - 3} more.")
                    if "manuscript" in state_update:
                        excerpt = state_update["manuscript"][-400:]
                        print(f"  Manuscript (latest excerpt):\n    {excerpt[:300]}...")
                    if "inventory_log" in state_update:
                        print(f"  Inventory: {state_update['inventory_log']}")
                    if "supporting_cast" in state_update:
                        for c in state_update["supporting_cast"]:
                            print(f"  Cast — {c['name']}: trust={c['trust_level']}")

            print("\n" + "═" * 60)
            print("  Session Complete")
            print("═" * 60)
            print(session_log.summary())

        except Exception as e:
            print(f"\n✗ Execution failed: {e}")
            print("  Set OPENROUTER_API_KEY or GEMINI_API_KEY and try again.")

if __name__ == "__main__":
    run()
