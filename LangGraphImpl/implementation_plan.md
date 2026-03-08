# Refactoring to Prompt-Driven Engine

**Refactoring Logic: The "Skeleton & Muscle" Philosophy**
*Thinking Model:* "The Python code is the Skeleton (data structures and flow). The Text Prompts are the Muscle (decisions and values). The Skeleton must never decide how a bone moves; it only provides the joint. All 'How' and 'Why' logic must be evicted from `.py` files and relocated to `.txt` files."

## Phase 1: Dynamic Initialization (Evicting Static Data)
**Goal:** Remove hard-coded character definitions and world constants from `engine.py`.
**Logic Change:** Replace the static `supporting_cast` list in `initial_state` with a call to a new parser.

*   **Create `parse_character_matrix(file_content)` utility in `context.py`.**
    *   This utility must use regex or string splitting to find character names (e.g., "LUCE", "ROOK") and map the subsequent bullet points into the `SupportingCast` TypedDict format.
*   **Update `initial_state`:** Set the `supporting_cast` field to the output of the new parsing function so that adding a character only requires a text edit.

## Phase 2: Instruction-Driven Continuity (Evicting Math)
**Goal:** Remove the "Vig" math (random item loss, 5% increase) and Lucidity caps from `nodes.py`.
*Thinking Model:* "The LLM is the judge. If the LLM says a 'Vig event' happened and specifies 'Stun baton' is lost, the Python simply deletes 'Stun baton'. It does not choose the item itself."

*   **Modify `ContinuityUpdates` Pydantic schema** to include `specific_item_to_remove: Optional[str]` and `lucidity_type: Optional[str]`.
*   **Refactor `nodes.py`:** Remove `import random` and the `min(2, ...)` logic from `continuity_extractor`.
*   **Update `continuity_extractor.txt`:** Add explicit instructions:
    *   "If the prose indicates a job refusal, identify one specific item from the current inventory to be lost as 'the vig'."
    *   "If Ad-Man achieves lucidity, categorize it as empathy, vault, or schmuck-rage."

## Phase 3: Externalizing Physics (Evicting Constants)
**Goal:** Remove the "Industrial Rumors" mask and world-limit constants from the code.
*Thinking Model:* "If a rule exists in Python (like a cap of 2 lucidity moments), move that sentence into the `physics_doc.txt` as a 'Law'. It is now the LLM’s job to count and respect that law."

*   **Externalize Vault Masking:** Add a `[VAULT_MASK]` section to `physics_doc.txt` containing the "Industrial Rumors" text. Update `_masked_drafter` in `graph.py` to call `load_prompt("physics_doc.txt")` and extract the mask string dynamically.
*   **Global Constants:** Move the "2x Lucidity Limit" into `physics_doc.txt` as a "Systemic Law" that the `continuity_extractor` must respect.

## Phase 4: Verification & Logging
*   **Update SessionLog:** Ensure the `continuity_extractor` still records these events in the JSONL log, but labels them as "LLM-Triggered Continuity Events" to distinguish them from manual state changes.
*   **Audit Run:** Run a test session using the scene brief in `engine.py` to confirm the LLM successfully triggers a Vig collection based solely on the text instructions.
