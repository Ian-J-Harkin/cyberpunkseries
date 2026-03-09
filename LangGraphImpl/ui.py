import os
import sqlite3
import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver
from graph import build_graph
from context import SessionLog

# ── Streamlit Page Config ───────────────────────────────────────────────────
st.set_page_config(page_title="Warm Neon | Narrative Engine", layout="wide")

st.title("Warm Neon Narrative Engine")
st.markdown("Monitor the 5-node AI architecture generating the functional-failing cyberpunk narrative.")

# ── Ensure API Keys ────────────────────────────────────────────────────────
gemini_key = st.sidebar.text_input("GEMINI_API_KEY", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
router_key = st.sidebar.text_input("OPENROUTER_API_KEY", type="password", value=os.environ.get("OPENROUTER_API_KEY", ""))
anthropic_key = st.sidebar.text_input("ANTHROPIC_API_KEY", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))

if gemini_key:
    os.environ["GEMINI_API_KEY"] = gemini_key
if router_key:
    os.environ["OPENROUTER_API_KEY"] = router_key
if anthropic_key:
    os.environ["ANTHROPIC_API_KEY"] = anthropic_key

if not (gemini_key or router_key or anthropic_key):
    st.warning("Please enter an API key in the sidebar to run the engine.")
    st.stop()


# ── Initialization ──────────────────────────────────────────────────────────
@st.cache_resource
def get_graph():
    return build_graph()

builder = get_graph()
db_path = os.path.join(os.path.dirname(__file__), "checkpoints.sqlite")
session_id = st.sidebar.text_input("Session ID", value="warm_neon_session_1")
config = {"configurable": {"thread_id": session_id}}

log_dir = os.path.join(os.path.dirname(__file__), "logs")
session_log = SessionLog(session_id, log_dir=log_dir)

# Initialize blank layout placeholders
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Live Manuscript")
    manuscript_placeholder = st.empty()
    st.subheader("Latest Scene Beats")
    beats_placeholder = st.empty()

with col2:
    st.subheader("Graph Context")
    infra_placeholder = st.empty()
    gov_placeholder = st.empty()
    st.subheader("Inventory & Cast")
    metrics_placeholder = st.empty()
    st.subheader("Event Log")
    log_placeholder = st.empty()

# ── Function to render state to UI ──────────────────────────────────────────
def render_state(state):
    if state.get("manuscript"):
        manuscript_placeholder.markdown(state["manuscript"])
    else:
        manuscript_placeholder.info("Awaiting drafting...")

    if state.get("scene_beats"):
        beats = state["scene_beats"]
        idx = state.get("current_beat_index", 0)
        formatted_beats = ""
        for i, b in enumerate(beats):
            if i == idx:
                formatted_beats += f"- **👉 {b}**\n"
            elif i < idx:
                formatted_beats += f"- ~~{b}~~\n"
            else:
                formatted_beats += f"- {b}\n"
        beats_placeholder.markdown(formatted_beats)

    if state.get("infrastructure"):
        infra_placeholder.info(f"**Infrastructure:** {state['infrastructure']}")
    if state.get("governance"):
        gov_placeholder.caption(f"**North Star:** {state['governance']}")

    if state.get("inventory_log") is not None and state.get("supporting_cast") is not None:
        inv = ", ".join(state["inventory_log"]) if state["inventory_log"] else "Empty"
        cast_lines = []
        for c in state["supporting_cast"]:
            cast_lines.append(f"- {c['name']} (Trust: {c.get('trust_level', 50)})")
        cast_str = "\n".join(cast_lines)
        metrics_placeholder.markdown(f"**Inventory:** {inv}\n\n**Cast:**\n{cast_str}")

    logs = session_log.read_all()
    if logs:
        log_lines = []
        for log in reversed(logs[-10:]):  # Show last 10
            ts = log["timestamp"][11:19]
            log_lines.append(f"`[{ts}] {log['event_type']}`: {log['payload']}")
        log_placeholder.markdown("\n\n".join(log_lines))

# ── Run Engine Button ───────────────────────────────────────────────────────
if st.button("▶ Run Narrative Cycle"):
    with st.spinner("Engine is running..."):
        with SqliteSaver.from_conn_string(db_path) as memory:
            graph = builder.compile(checkpointer=memory)

            # Try to get existing state to resume, else provide initial state
            current_state = memory.get_tuple(config)
            
            if current_state is None:
                # Brand new session initialization
                state_to_use = {
                    "vault_access_level": 0,
                    "governance": "",
                    "boundaries": {},
                    "protagonist": {
                        "name": "Dex", "mbti": "ESTP", "enneagram": "7w8",
                        "arc_version": "Chapter 1 — Arrival", "physical_status": "No injuries",
                        "health_flags": []
                    },
                    "supporting_cast": [
                        {"name": "Sarge", "internal_frequency": "Cynical realism filtered through tactical habit", "noticing_rule": "Sarge notices the protagonist's biometric errors", "physical_anchor": "Scuffed cybernetic arm, always tapping", "trust_level": 50},
                        {"name": "Glimmer", "internal_frequency": "Hyper-observant despite physical limitation", "noticing_rule": "Glimmer notices social power dynamics in the room", "physical_anchor": "Cushion-propped autoimmunity, ozone tea", "trust_level": 40},
                        {"name": "Ad-Man", "internal_frequency": "Neural-Scraped Sloganeering", "noticing_rule": "Ad-Man notices what the protagonist is trying to sell", "physical_anchor": "Perpetually blinking ad-overlay visor", "trust_level": 30}
                    ],
                    "infrastructure": "High fraying — neon decay, acid rain, bureaucratic sludge",
                    "inventory_log": [],
                    "scene_beats": [],
                    "current_beat_index": 0,
                    "manuscript": "",
                    "_session_log": session_log
                }
            else:
                # Resume from last checkpoint, but we must inject the session log 
                # object since it's not serialized to sqlite
                state_to_use = None
                
            st.toast("Started graph stream...")
            
            # Stream events
            for event in graph.stream(state_to_use, config, stream_mode="updates"):
                for node, state_update in event.items():
                    # We can't render the partial state update perfectly if it only has deltas,
                    # so we fetch the full merged state from memory to render it cleanly.
                    merged = memory.get_tuple(config).checkpoint["channel_values"]
                    render_state(merged)
                    
            st.toast("Cycle Complete!", icon="✅")
            st.balloons()
            
else:
    # Render historical state on load if it exists
    with SqliteSaver.from_conn_string(db_path) as memory:
        current_state = memory.get_tuple(config)
        if current_state:
            render_state(current_state.checkpoint["channel_values"])
        else:
            st.info("No checkpoint found for this session ID. Click 'Run Narrative Cycle' to initialize.")
