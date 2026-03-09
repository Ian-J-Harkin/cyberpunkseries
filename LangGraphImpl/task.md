# The "Warm Neon" Narrative Engine Implementation

- [x] Planning
  - [x] Create implementation plan
  - [x] Get user approval
- [ ] Execution
  - [x] Setup Knowledge Base (Prompt text files)
  - [x] Implement State Schema (`Continuity Log` and `Character Matrix`)
  - [x] Implement Nodes (`dna_architect`, `scene_plotter`, `persona_drafter`, `continuity_extractor`)
  - [x] Implement Edge Logic / Vault Access condition
  - [x] Setup LangGraph `StateGraph` and `SqliteSaver`
  - [x] Create main execution script
- [x] Verification
  - [x] Test the pipeline
  - [x] Create walkthrough.md
- [x] n8n Enhancements
  - [x] Add `series_bible.txt` and `character_matrix.txt` global context files
  - [x] Create `load_global_context()` utility injected into all nodes
  - [x] Add `friction_auditor` node between `scene_plotter` and `persona_drafter`
  - [x] Add structured JSON session event log
  - [x] Wire `friction_auditor` into `graph.py`
  - [x] Update `engine.py` to initialize the session log

## Phase 2: UI & Tool Integration
- [x] Execution
  - [x] Add `streamlit` to `requirements.txt`
  - [x] Update `continuity_extractor` in `nodes.py` to use structured JSON output/tools
  - [x] Create `ui.py` Streamlit frontend
- [x] Verification
  - [x] Install updated requirements
  - [x] Run `streamlit run ui.py` to verify UI and graph execution
  - [x] Update `walkthrough.md` with Phase 2 details

## Phase 3A: LangChainFictioneer Logic Injection
- [x] Execution
  - [x] Rewrite `prompts/series_bible.txt` as Narrative Physics Document
  - [x] Rewrite `prompts/character_matrix.txt` with State Machine format
  - [x] Create `prompts/relationship_matrix.txt` with Relationship Force Fields
  - [x] Upgrade `prompts/persona_drafter.txt` with 6 Formal Drafting Rules
  - [x] Upgrade `prompts/continuity_extractor.txt` to produce Rolling State
  - [x] Add `SceneBrief` TypedDict and `rolling_state` field to `state.py`
  - [x] Update `context.py` to load `relationship_matrix.txt`
  - [x] Update `nodes.py` (drafter uses SceneBrief, extractor produces Rolling State)
  - [x] Update `engine.py` with initial SceneBrief and rolling_state seed
- [x] Verification
  - [x] Syntax check
  - [x] Update `walkthrough.md`

## Phase 3C: Character Matrix & Variable Tracking
- [x] Overwrite `prompts/character_matrix.txt` with Warm Neon details
- [x] Add `lucidity_counts` and `medical_debt` to `NarrativeState` (`state.py`)
- [x] Initialize fields in `engine.py`
- [x] Update `continuity_extractor.txt` and `nodes.py` to handle `lucidity_increments` and `medical_debt_increase`

## Phase 3D: Writing Loop & Persistent Logic
- [x] Create `prompts/writing_loop.txt`
- [x] Change `medical_debt` to `medical_debt_percent` in `NarrativeState` (Now `medical_loan_balance`)
- [x] Update `continuity_extractor` node logic to parse Vig and Ad-Man triggers

## Phase 3E: Enhanced Character Matrix & Physics Logic
- [x] Overwrite `prompts/character_matrix.txt` with latest Behavioral Anchors
- [x] Overwrite `prompts/physics_doc.txt` with Causality Laws & World Compass
- [x] Update `nodes.py` to extract `vig_collection_event` and remove an inventory item instead of increasing debt percent
- [x] Update `engine.py` and `state.py` to initialize `medical_loan_balance: 0.20`

## Phase 3F: Final Logic Gaps
- [x] Update `engine.py` to add Rook and Luce to `initial_state`
- [x] Update `nodes.py` to enforce max 2 instances for Ad-Man's Lucidity properties
- [x] Update `nodes.py` `persona_drafter` context injection to explicitly pass Lucidity and Vig status to the LLM
- [x] Confirm `context.py` automatically injects `physics_doc.txt` to all nodes (Tonal Gap logic satisfied)
- [x] Update `engine.py` with "The Reasonable Collection" test brief and initial inventory, and enforce the 5% debt penalty on Vig collection in `nodes.py`

## Phase 3G: Revised Enforcer Matrix (Rook & Luce)
- [x] Overwrite `character_matrix.txt` Enforcers section with detailed Stage 1/Stage 2 logic for Rook and Mercenary logic for Luce.
- [x] Add `character_modifiers` to `NarrativeState` in `state.py`
- [x] Initialize `character_modifiers` with Rook's Stage 1 status in `engine.py`
- [x] Add extraction and logging logic for `character_modifiers_update` to `nodes.py`

## Phase 3H: The Mercenary Pivot
- [x] Verify `character_matrix.txt` contains Luce's Mercenary Pivot and anchors
- [x] Add the 20% "Mercenary Friction" rule to Causality Laws in `physics_doc.txt`

## Phase 1: Dynamic Character Initialization
- [x] Implement `parse_character_matrix(file_content)` utility in `context.py`
- [x] Refactor `engine.py` to remove static `supporting_cast` list and use the parser
- [x] Update `initial_state` to use the dynamically parsed cast

## Phase 2: Instruction-Driven Continuity
- [x] Modify `ContinuityUpdates` in `nodes.py` to remove random choices and strict math bounds
- [x] Add explicit instructions to `continuity_extractor.txt` for handling Vig and Lucidity types
- [x] Update `continuity_extractor` logic to apply LLM-chosen actions

## Phase 3: Moving Physics to the Physics Doc
- [x] Add `[VAULT_MASK]` section to `physics_doc.txt`
- [x] Update `_masked_drafter` in `graph.py` to pull the mask directly from `physics_doc.txt`
- [x] Move the "2x Lucidity Limit" into `physics_doc.txt` as a Systemic Law

## Phase 4: Verification & Logging
- [x] Update `SessionLog` in `nodes.py` to label "LLM-Triggered Continuity Events"
- [x] Run an audit session with "The Reasonable Collection" brief to verify LLM execution

## Phase 5: Dynamic Scene Architecture
- [x] Create Pydantic `BeatList` schema in `nodes.py`
- [x] Update `scene_plotter` to use structured output, removing the "10-15 beats" hard-coded prompt

## Phase 6: Externalizing the World Compass
- [x] Remove boundaries initialization from `nodes.py`
- [x] Update `dna_architect.txt` to extract boundaries from `PHYSICS_LAWS`

## Phase 7: The Governance Refactor
- [x] Empty `infrastructure` in `engine.py` initial state
- [x] Update `dna_architect` to use structured output without truncating `governance`
- [x] Instruct `dna_architect` to define Governance based on arc theme from state

## Deferred Phase
- Option B: Setup Graph with LangGraph Send API fan-out
- [x] Anthropic API key support for Claude Opus/Sonnet
