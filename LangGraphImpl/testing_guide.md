# Warm Neon Engine Testing Guide

This document outlines how to test the two core Narrative Physics rule sets we just integrated into the `LangGraphImpl` engine: **The Vig Penalty** (Luce) and **The Lucidity Oracle** (Ad-Man).

---

## Prerequisites
Before running these tests, ensure:
1. Your terminal is open to `c:\Github\AI_Fiction\cyberpunkseries\LangGraphImpl`.
2. You have a valid `GEMINI_API_KEY` or `OPENROUTER_API_KEY` exported in your environment.
3. You run the engine via:
   ```bash
   python engine.py
   ```

After each test runs, you should open the session log located at `logs/warm_neon_session_1.jsonl` to verify the state changes.

---

## Test Scenario 1: "The Reasonable Collection" (The Vig Penalty)
**Goal:** Verify that refusing a job from Luce triggers a `vig_collection_event`, resulting in the loss of one random item from Dex's inventory and a `+0.05` increase in his medical loan balance.

**How to Setup (in `engine.py`):**
Replace the `scene_brief` and `inventory_log` in your `initial_state` with the following:

```python
            "inventory_log": ["Stun baton", "Burner phone", "Flask of cheap synthetic whiskey"],
            # ...
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
```

**Verification Details:**
1. Run the engine.
2. Read the final trailing output in the console. You should see a scene where Dex refuses the job and Luce demands compensation.
3. Open `logs/warm_neon_session_1.jsonl`. 
4. Look for the `VIG_COLLECTION_EVENT` key. You should see `"action": "Inventory item removed due to job refusal, debt increased by 5%"`.
5. Look for `INVENTORY_CHANGE` and verify that the `removed` array contains one of the three starting items.

---

## Test Scenario 2: "The Schmuck-Rage Trigger" (The Ad-Man Oracle)
**Goal:** Verify that the engine correctly parses Ad-Man's moments of lucidity and caps them mathematically so the model cannot "over-use" his insights.

**How to Setup (in `engine.py`):**
Replace the `scene_brief` and `lucidity_counts` in your `initial_state` with the following (note: we are setting `schmuck` to `1` initially to test the upper-bound cap):

```python
            "lucidity_counts":   {"empathy": 0, "vault": 0, "schmuck": 1}, # Starting near the cap
            # ...
            "scene_brief": {
                "act_position": "Act 2 — INVESTIGATION",
                "previous_scene_summary": "Dex just got a cryptic lead from a fixer.",
                "scene_plot_function": "Dex needs to decipher a Vault code from a scrap of data. He consults the glitched-out Ad-Man. A rival named Leon Schmuck walks by and taunts Ad-Man.",
                "new_state_goal": "Ad-Man experiences a moment of profound 'Schmuck-Rage' and temporarily drops his ad-slogans to provide the exact Vault code Dex needs in a moment of terrifying, unbroken clarity.",
                "character_knowledge": "Dex suspects Ad-Man knows the code but is waiting for a trigger.",
                "character_emotional_states": "Dex is frustrated. Ad-Man is lost in slogans until Leon Schmuck arrives.",
                "physical_status": "No injuries",
                "health_flags": []
            },
```

**Verification Details:**
1. Run the engine. 
   *(Note: because you already ran Test 1, change the `session_id` on line 12 of `engine.py` to `"warm_neon_session_2"` so the checkpointing starts fresh).*
2. Look for the `LUCIDITY_UPDATE` event type in `logs/warm_neon_session_2.jsonl`.
3. The event payload should show `"increments": {"empathy": 0, "vault": 0, "schmuck": 1}`. 
4. Check the very final state dump to verify that the `lucidity_counts` dictionary for `schmuck` stopped exactly at `2` (the mathematical cap enforced by `nodes.py`), even if the AI tried to increment it further.
