# frontend/app.py
import streamlit as st
import requests

# -------------------------
# SESSION STATE FOR CHAT
# -------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"q": "...", "a": "..."}

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="SparkAI | Electrical Intelligence",
    page_icon="S",
    layout="wide",
)

# -------------------------
# BACKEND HEALTH CHECK
# -------------------------
API_BASE = "https://sparkai-6g2p.onrender.com"





# -------------------------
# STYLE
# -------------------------
st.markdown(
    """
    <style>
        :root {
            --sparky-yellow: #f8d056;
            --sparky-slate: #0c1118;
            --sparky-graphite: #1a1f27;
            --sparky-line: rgba(248, 208, 86, 0.25);
            --sparky-text: #e5e7eb;
            --sparky-muted: #8b92a1;
            --sparky-panel: #12161d;
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top right, #1f2c3f, #090c11);
            color: var(--sparky-text);
            font-family: 'Inter', sans-serif;
        }

        [data-testid="stHeader"] {background: transparent;}

        .sparky-shell {
            border: 1px solid var(--sparky-line);
            background: linear-gradient(135deg, rgba(22,30,45,0.95), rgba(9,12,17,0.9));
            padding: 2.5rem;
            border-radius: 1.5rem;
            box-shadow: 0 25px 60px rgba(0,0,0,0.35);
        }

        .sparky-pill {
            letter-spacing: 0.3rem;
            font-size: 0.82rem;
            text-transform: uppercase;
            color: var(--sparky-yellow);
        }

        .spark-line {
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--sparky-yellow), transparent);
            margin: 1rem 0 1.5rem;
        }

        .grid-panel {
            border: 1px solid rgba(255,255,255,0.08);
            background: var(--sparky-panel);
            padding: 1.5rem;
            border-radius: 1rem;
            height: 100%;
        }

        .grid-panel h4 {
            margin-bottom: 0.5rem;
            color: var(--sparky-yellow);
        }

        textarea, input, .stTextArea textarea {
            background-color: #1f242d !important;
            color: var(--sparky-text) !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 0.8rem !important;
            padding: 0.9rem !important;
            font-size: 0.95rem !important;
        }

        textarea:focus, input:focus, .stTextArea textarea:focus {
            border: 1px solid var(--sparky-yellow) !important;
            outline: none !important;
            box-shadow: 0 0 0 1px var(--sparky-yellow);
        }

        div.stButton > button {
            background: var(--sparky-yellow);
            color: #111;
            border-radius: 0.7rem;
            font-weight: 600;
            border: none;
            height: 2.8rem;
            transition: all 0.2s ease;
        }

        div.stButton > button:hover {
            background: #ffd95c;
            transform: scale(1.02);
        }

        .answer-block {
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(12, 17, 25, 0.9);
            padding: 1.5rem;
            border-radius: 1rem;
            line-height: 1.6;
        }

        .chat-entry {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(20,25,35,0.7);
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 0.8rem;
        }

        .chat-question {
            color: var(--sparky-yellow);
            font-weight: 600;
        }

        .chat-answer {
            margin-top: 0.3rem;
        }

        .status-text {
            text-align: right;
            color: var(--sparky-muted);
            font-size: 0.9rem;
            margin-top: -2.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# HEADER
# -------------------------
st.markdown(
    """
    <div class="sparky-shell">
        <div class="sparky-pill">Precision Electrical Intelligence</div>
        <h1 style="margin-top:0.8rem; letter-spacing:-0.04em;">SparkAI</h1>
        <h3 style="font-weight:400; opacity:0.8;">
            Your instant guide to Australia’s core electrical standards
        </h3>
        <div class="spark-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)



st.write("")

# -------------------------
# CHAT HISTORY DISPLAY
# -------------------------
st.subheader("Conversation History")

if st.session_state.chat_history:
    for entry in reversed(st.session_state.chat_history):
        st.markdown(
            f"""
            <div class='chat-entry'>
                <div class='chat-question'>You:</div>
                <div>{entry["q"]}</div>
                <div class='chat-answer'><span class='chat-question'>SparkAI:</span> {entry["a"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.caption("No previous questions yet — start your session below.")

# Clear chat button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()

# -------------------------
# MAIN LAYOUT
# -------------------------
left, right = st.columns((1.4, 1))

with left:
    st.subheader("Console")
    question = st.text_area(
        "Input",
        placeholder="Describe the installation, compliance requirement, or clause you are validating.",
        label_visibility="collapsed",
        height=150,
    )
    send_col, info_col = st.columns([0.4, 0.6])
    with send_col:
        trigger = st.button("Initiate Analysis", use_container_width=True)
    with info_col:
        st.empty()

    response_container = st.container()

with right:
    st.subheader("Diagnostics")
    with st.container():
        st.markdown(
            """
            <div class="grid-panel">
                <h4>Standards Matrix</h4>
                <ul>
                    <li>AS/NZS 3000:2018 Wiring Rules</li>
                    <li>AS/NZS 3012:2010 Electrical installations - Construction & demolition sites</li>
                    <li>AS/NZS 3017:2007 Testing procedures</li>
                    <li>Supplementary project manuals - QLD Energy Connection Manual (Ergon Energy) and client specs</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------
# ASK BACKEND
# -------------------------
if trigger and question:
    with st.spinner("Thinking..."):
        try:
            resp = requests.post(
                f"{API_BASE}/ask",
                json={"question": question},
                timeout=90,
            )
            if resp.status_code == 200:
                payload = resp.json()
                answer = payload.get("answer", "No answer received.")
                confidence = payload.get("confidence")

                st.session_state.chat_history.append({"q": question, "a": answer})

                with response_container:
                    st.markdown("#### Advisory Output")
                    st.markdown(f'<div class="answer-block">{answer}</div>', unsafe_allow_html=True)
                    if confidence is not None:
                        pct = int(max(0.0, min(1.0, confidence)) * 100)
                        st.markdown(f"**Source alignment confidence:** {pct}%")
                        st.progress(pct)
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as exc:
            st.error(f"Connection error: {exc}")
elif trigger and not question:
    st.warning("Provide a detailed question so SparkAI can reference the correct clauses.")

# -------------------------
# FOOTER
# -------------------------
st.markdown(
    """
    ---
    **Disclaimer:** SparkAI references digitised Australian electrical standards, however all outputs must be independently validated against the latest published documents, project specifications, and regulatory requirements before implementation.
    
    Built by DocuFlex Safety · OpenAI-powered retrieval
    """
)
