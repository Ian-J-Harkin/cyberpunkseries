import os
from langgraph.checkpoint.sqlite import SqliteSaver
from graph import build_graph
from context import SessionLog

def run():
    builder  = build_graph()
    db_path  = os.path.join(os.path.dirname(__file__), "checkpoints.sqlite")

    # ── Session identity ───────────────────────────────────────────────────────
    # Change thread_id to start a fresh persistent session without deleting the DB.
    session_id = "warm_neon_session_1"
    config     = {"configurable": {"thread_id": session_id}}

    # ── Session event log (n8n Step 5 → database write equivalent) ────────────
    log_dir      = os.path.join(os.path.dirname(__file__), "logs")
    session_log  = SessionLog(session_id, log_dir=log_dir)

    with SqliteSaver.from_conn_string(db_path) as memory:
        graph = builder.compile(checkpointer=memory)

        # ── Initial State ──────────────────────────────────────────────────────
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

            "supporting_cast": [
                {
                    "name":               "Sarge",
                    "internal_frequency": "Cynical realism filtered through tactical habit",
                    "noticing_rule":      "Sarge notices the protagonist's biometric errors",
                    "physical_anchor":    "Scuffed cybernetic arm, always tapping",
                    "trust_level":        50
                },
                {
                    "name":               "Glimmer",
                    "internal_frequency": "Hyper-observant despite physical limitation",
                    "noticing_rule":      "Glimmer notices social power dynamics in the room",
                    "physical_anchor":    "Cushion-propped autoimmunity, ozone tea",
                    "trust_level":        40
                },
                {
                    "name":               "Ad-Man",
                    "internal_frequency": "Neural-Scraped Sloganeering",
                    "noticing_rule":      "Ad-Man notices what the protagonist is trying to sell",
                    "physical_anchor":    "Perpetually blinking ad-overlay visor",
                    "trust_level":        30
                },
                {
                    "name":               "Rook",
                    "internal_frequency": "Weaponizes his burns for intimidation",
                    "noticing_rule":      "Rook recognizes Dex's fear or weakness",
                    "physical_anchor":    "Permanently disfigured by electrocution",
                    "trust_level":        10
                },
                {
                    "name":               "Luce",
                    "internal_frequency": "The Reasonable Enforcer",
                    "noticing_rule":      "Luce notices missed payments and contract details",
                    "physical_anchor":    "Polite bureaucrat of the underworld",
                    "trust_level":        30
                }
            ],

            "infrastructure":    "High fraying — neon decay, acid rain, bureaucratic sludge",
            "inventory_log":     [],
            "lucidity_counts":   {"empathy": 0, "vault": 0, "schmuck": 0},
            "medical_loan_balance": 0.20,
            
            "scene_beats":       [],
            "current_beat_index": 0,
            
            "scene_brief": {
                "act_position": "Act 1, Chapter 1",
                "previous_scene_summary": "N/A (Opening Scene)",
                "scene_plot_function": "Establish the protagonist's normal world and introduce the inciting incident.",
                "new_state_goal": "Dex receives a job that requires engaging with the bureaucracy.",
                "character_knowledge": "Dex knows he is low on cash. Sarge knows something is brewing but hasn't shared it.",
                "character_emotional_states": "Dex: Baseline. Sarge: Baseline.",
                "physical_status": "No injuries",
                "health_flags": []
            },
            "rolling_state": "No scenes written yet. This is the start of the project.",
            
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
