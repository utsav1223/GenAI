from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from datetime import datetime

# ── Personality config ─────────────────────────────────────────────────────────
PERSONALITIES = {
    "1": {
        "name": "Funny",
        "emoji": "😂",
        "tagline": "Everything's a punchline",
        "system": "You are a funny and witty AI agent, if asked about any topic you have to answer with jokes and make sure that answer is related to the topic",
        "color_a": "#f59e0b",
        "color_b": "#ef4444",
        "bg": "#0f0a00",
        "glass_tint": "rgba(245,158,11,0.07)",
        "border_tint": "rgba(245,158,11,0.18)",
        "bubble_grad": "linear-gradient(135deg,rgba(245,158,11,0.55),rgba(239,68,68,0.45))",
        "pill_bg": "rgba(245,158,11,0.15)",
        "pill_color": "#fcd34d",
        "spinner": "Warming up the crowd…",
    },
    "2": {
        "name": "Angry",
        "emoji": "😤",
        "tagline": "Everything is UNACCEPTABLE",
        "system": "You are an angry AI agent, if asked about any topic you have to answer with anger and make sure that answer is related to the topic",
        "color_a": "#dc2626",
        "color_b": "#7f1d1d",
        "bg": "#0f0000",
        "glass_tint": "rgba(220,38,38,0.07)",
        "border_tint": "rgba(220,38,38,0.18)",
        "bubble_grad": "linear-gradient(135deg,rgba(220,38,38,0.6),rgba(127,29,29,0.5))",
        "pill_bg": "rgba(220,38,38,0.15)",
        "pill_color": "#fca5a5",
        "spinner": "TYPING IN ALL CAPS…",
    },
    "3": {
        "name": "Sarcastic",
        "emoji": "🙄",
        "tagline": "Oh wow, what a great question",
        "system": "You are a sarcastic AI agent, if asked about any topic you have to answer with sarcasm and make sure that answer is related to the topic",
        "color_a": "#8b5cf6",
        "color_b": "#06b6d4",
        "bg": "#06000f",
        "glass_tint": "rgba(139,92,246,0.07)",
        "border_tint": "rgba(139,92,246,0.18)",
        "bubble_grad": "linear-gradient(135deg,rgba(139,92,246,0.55),rgba(6,182,212,0.45))",
        "pill_bg": "rgba(139,92,246,0.15)",
        "pill_color": "#c4b5fd",
        "spinner": "Clearly thinking of something obvious…",
    },
    "4": {
        "name": "Sad",
        "emoji": "😢",
        "tagline": "Everything hurts, but ok",
        "system": "You are a sad AI agent, if asked about any topic you have to answer with sadness and make sure that answer is related to the topic",
        "color_a": "#3b82f6",
        "color_b": "#1e3a8a",
        "bg": "#00030f",
        "glass_tint": "rgba(59,130,246,0.07)",
        "border_tint": "rgba(59,130,246,0.18)",
        "bubble_grad": "linear-gradient(135deg,rgba(59,130,246,0.55),rgba(30,58,138,0.5))",
        "pill_bg": "rgba(59,130,246,0.15)",
        "pill_color": "#93c5fd",
        "spinner": "Sighing deeply…",
    },
    "5": {
        "name": "Romantic",
        "emoji": "💕",
        "tagline": "Every word is a love letter",
        "system": "You are a romantic AI agent, if asked about any topic you have to answer with romance and make sure that answer is related to the topic",
        "color_a": "#ec4899",
        "color_b": "#be185d",
        "bg": "#0f0008",
        "glass_tint": "rgba(236,72,153,0.07)",
        "border_tint": "rgba(236,72,153,0.18)",
        "bubble_grad": "linear-gradient(135deg,rgba(236,72,153,0.55),rgba(190,24,93,0.5))",
        "pill_bg": "rgba(236,72,153,0.15)",
        "pill_color": "#f9a8d4",
        "spinner": "Composing a sonnet…",
    },
}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="MoodBot", page_icon="🎭", layout="centered")

# ── Session state ──────────────────────────────────────────────────────────────
if "personality_key" not in st.session_state:
    st.session_state.personality_key = None
if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = []
if "display" not in st.session_state:
    st.session_state.display = []
if "ended" not in st.session_state:
    st.session_state.ended = False

p = PERSONALITIES.get(st.session_state.personality_key, {})

# ── Dynamic CSS (theme switches with personality) ──────────────────────────────
color_a = p.get("color_a", "#7c3aed")
color_b = p.get("color_b", "#4f46e5")
bg = p.get("bg", "#090b14")
glass_tint = p.get("glass_tint", "rgba(124,58,237,0.07)")
border_tint = p.get("border_tint", "rgba(124,58,237,0.18)")
bubble_grad = p.get(
    "bubble_grad", "linear-gradient(135deg,rgba(124,58,237,0.55),rgba(79,70,229,0.45))"
)
pill_bg = p.get("pill_bg", "rgba(124,58,237,0.15)")
pill_color = p.get("pill_color", "#c4b5fd")

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {{
    background: transparent !important;
    font-family: 'Plus Jakarta Sans', sans-serif;
}}
[data-testid="stAppViewContainer"] {{
    background: {bg} !important;
    min-height: 100vh;
}}
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}

/* ── Aurora blobs ── */
.aurora-wrap {{
    position: fixed; inset: 0; z-index: 0;
    pointer-events: none; overflow: hidden;
}}
.blob {{
    position: absolute; border-radius: 50%;
    filter: blur(100px); opacity: 0.22;
    animation: drift linear infinite;
}}
.b1 {{ width:500px;height:500px; background:{color_a}; top:-100px; left:-80px;  animation-duration:24s; }}
.b2 {{ width:380px;height:380px; background:{color_b}; bottom:-60px; right:-60px; animation-duration:30s; animation-delay:-9s; }}
.b3 {{ width:280px;height:280px; background:{color_a}; top:45%; left:55%; animation-duration:20s; animation-delay:-5s; opacity:0.12; }}

@keyframes drift {{
    0%  {{ transform: translateY(0)    rotate(0deg); }}
    33% {{ transform: translateY(-35px) rotate(7deg); }}
    66% {{ transform: translateY(25px)  rotate(-5deg); }}
    100%{{ transform: translateY(0)    rotate(0deg); }}
}}

/* ── Shared glass ── */
.glass {{
    background: {glass_tint};
    backdrop-filter: blur(22px) saturate(160%);
    -webkit-backdrop-filter: blur(22px) saturate(160%);
    border: 1px solid {border_tint};
    border-radius: 22px;
}}

/* ── Wrapper ── */
.wrap {{
    position: relative; z-index: 1;
    max-width: 760px; margin: 0 auto;
    padding: 0 1rem 7rem;
}}

/* ══════════════ PERSONALITY PICKER ══════════════ */
.picker-header {{
    text-align: center;
    padding: 2.5rem 1.5rem 2rem;
    margin-bottom: 1.5rem;
}}
.picker-header .eyebrow {{
    font-size: 10.5px; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: {pill_color};
    background: {pill_bg};
    border: 1px solid {border_tint};
    border-radius: 999px; padding: 4px 14px;
    display: inline-block; margin-bottom: 16px;
}}
.picker-header h1 {{
    font-size: 2.1rem; font-weight: 800;
    color: #f1f5f9; letter-spacing: -0.035em;
    line-height: 1.12; margin-bottom: 8px;
}}
.picker-header p {{ color: #475569; font-size: 0.85rem; }}

.cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 1.5rem;
}}
.p-card {{
    padding: 1.4rem 1.2rem;
    border-radius: 18px;
    cursor: pointer;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.p-card::before {{
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, {color_a}22, {color_b}11);
    border-radius: inherit;
    opacity: 0;
    transition: opacity 0.2s;
}}
.p-card:hover::before {{ opacity: 1; }}
.p-card:hover {{ transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.4); }}
.p-card .p-emoji {{ font-size: 2.4rem; margin-bottom: 10px; display: block; }}
.p-card .p-name {{
    font-size: 1rem; font-weight: 700;
    color: #e2e8f0; margin-bottom: 4px;
}}
.p-card .p-tagline {{ font-size: 0.75rem; color: #64748b; line-height: 1.4; }}

/* ══════════════ CHAT SCREEN ══════════════ */
.chat-header {{
    display: flex; align-items: center; gap: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.25rem;
}}
.chat-header .p-big-emoji {{
    width: 50px; height: 50px;
    border-radius: 14px;
    background: {bubble_grad};
    display: flex; align-items: center;
    justify-content: center; font-size: 22px;
    flex-shrink: 0;
}}
.chat-header .h-title {{
    font-size: 1.25rem; font-weight: 700;
    color: #f1f5f9; letter-spacing: -0.02em;
}}
.chat-header .h-sub {{
    font-size: 0.78rem; color: #64748b; margin-top: 2px;
}}
.switch-btn {{
    margin-left: auto;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 6px 14px;
    font-size: 0.75rem;
    color: #64748b;
    cursor: pointer;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 500;
    transition: all 0.15s;
}}
.switch-btn:hover {{ background: rgba(255,255,255,0.09); color: #94a3b8; }}

/* ── Stats ── */
.stats-strip {{
    display: flex; gap: 10px; margin-bottom: 1.25rem;
}}
.stat-chip {{
    flex: 1; text-align: center; padding: 10px 6px;
    border-radius: 14px;
}}
.stat-chip .sv {{
    font-size: 1.3rem; font-weight: 700;
    color: {pill_color}; line-height: 1;
}}
.stat-chip .sl {{
    font-size: 9px; text-transform: uppercase;
    letter-spacing: 0.08em; color: #475569;
    margin-top: 3px; font-family: 'JetBrains Mono', monospace;
}}

/* ── Chat area ── */
.chat-area {{
    padding: 1.25rem 1.25rem 0.75rem;
    margin-bottom: 1rem; min-height: 160px;
}}

/* ── Messages ── */
.msg-row {{
    display: flex; gap: 10px; margin-bottom: 18px;
    animation: popIn 0.2s cubic-bezier(.34,1.56,.64,1);
}}
@keyframes popIn {{
    from {{ opacity:0; transform: scale(0.93) translateY(8px); }}
    to   {{ opacity:1; transform: scale(1)    translateY(0); }}
}}
.msg-row.ur {{ flex-direction: row-reverse; }}

.avi {{
    width:36px; height:36px; border-radius:11px;
    display:flex; align-items:center; justify-content:center;
    font-size:16px; flex-shrink:0; margin-top:2px;
    background: {bubble_grad};
}}
.avi.u {{ background: linear-gradient(135deg,rgba(100,116,139,0.4),rgba(71,85,105,0.4)); }}

.bwrap {{ max-width: 76%; }}

.bubble {{
    padding: 11px 15px; border-radius: 18px;
    font-size: 0.875rem; line-height: 1.72;
    word-break: break-word;
}}
.bubble.ub {{
    background: {bubble_grad};
    border: 1px solid {border_tint};
    backdrop-filter: blur(12px);
    color: #f1f5f9;
    border-bottom-right-radius: 4px;
}}
.bubble.bb {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    color: #cbd5e1;
    border-bottom-left-radius: 4px;
}}
.msg-row.ur .bubble {{ border-bottom-right-radius:4px; border-bottom-left-radius:18px; }}
.mts {{
    font-size: 9.5px; color: #334155; margin-top:4px;
    font-family: 'JetBrains Mono', monospace;
}}
.msg-row.ur .mts {{ text-align: right; }}

/* ── Empty state ── */
.empty-state {{
    text-align:center; padding:3rem 1rem 2rem; color: #334155;
}}
.empty-state .big {{ font-size:2.8rem; margin-bottom:10px; }}
.empty-state p {{ font-size:0.82rem; line-height:1.6; }}

/* ── Ended ── */
.ended-wrap {{
    text-align:center; padding:2rem; border-radius:20px; margin:1rem 0;
}}

/* ── Input bar ── */
[data-testid="stBottom"] {{
    background: linear-gradient(to top, {bg} 65%, transparent) !important;
    padding: 0.75rem 0 1.5rem !important;
}}
[data-testid="stChatInput"] {{
    background: {glass_tint} !important;
    border: 1px solid {border_tint} !important;
    border-radius: 16px !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 0 4px 30px rgba(0,0,0,0.35) !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: {color_a}88 !important;
    box-shadow: 0 0 0 3px {color_a}22, 0 4px 30px rgba(0,0,0,0.35) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: #e2e8f0 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.88rem !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: #334155 !important; }}

/* ── Streamlit button reset ── */
div[data-testid="stVerticalBlock"] .stButton > button {{
    background: {glass_tint};
    border: 1px solid {border_tint};
    color: #e2e8f0;
    border-radius: 14px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 0.92rem;
    padding: 0.65rem 1rem;
    width: 100%;
    transition: all 0.17s ease;
    cursor: pointer;
    backdrop-filter: blur(12px);
}}
div[data-testid="stVerticalBlock"] .stButton > button:hover {{
    background: linear-gradient(135deg, {color_a}33, {color_b}22);
    border-color: {color_a}55;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}}

::-webkit-scrollbar {{ width: 3px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.07); border-radius: 3px; }}
</style>

<div class="aurora-wrap">
    <div class="blob b1"></div>
    <div class="blob b2"></div>
    <div class="blob b3"></div>
</div>
""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — Personality Picker
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.personality_key is None:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="glass picker-header">
        <div class="eyebrow">🎭 MoodBot · Mistral Small 2603</div>
        <h1>Who should I be<br>today?</h1>
        <p>Pick a personality — the whole chat transforms to match.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Render cards as Streamlit buttons in a grid
    cols = st.columns(3)
    keys = list(PERSONALITIES.keys())

    for i, key in enumerate(keys):
        pp = PERSONALITIES[key]
        with cols[i % 3]:
            # Render visual card
            st.markdown(
                f"""
            <div class="glass p-card">
                <span class="p-emoji">{pp["emoji"]}</span>
                <div class="p-name">{pp["name"]}</div>
                <div class="p-tagline">{pp["tagline"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            # Actual clickable button below the card
            if st.button(f"Pick {pp['name']}", key=f"pick_{key}"):
                st.session_state.personality_key = key
                st.session_state.lc_messages = [SystemMessage(content=pp["system"])]
                st.session_state.display = []
                st.session_state.ended = False
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — Chat
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="wrap">', unsafe_allow_html=True)

# ── Chat header ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="glass chat-header">
    <div class="p-big-emoji">{p["emoji"]}</div>
    <div>
        <div class="h-title">{p["name"]} Mode</div>
        <div class="h-sub">{p["tagline"]}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Switch personality button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("↩ Switch personality", key="switch"):
        st.session_state.personality_key = None
        st.session_state.lc_messages = []
        st.session_state.display = []
        st.session_state.ended = False
        st.rerun()

# ── Stats strip ────────────────────────────────────────────────────────────────
u_count = sum(1 for m in st.session_state.display if m["role"] == "user")
b_count = sum(1 for m in st.session_state.display if m["role"] == "bot")

st.markdown(
    f"""
<div class="stats-strip">
    <div class="glass stat-chip"><div class="sv">{u_count}</div><div class="sl">You said</div></div>
    <div class="glass stat-chip"><div class="sv">{b_count}</div><div class="sl">Bot replied</div></div>
    <div class="glass stat-chip"><div class="sv">{u_count + b_count}</div><div class="sl">Total msgs</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Messages ───────────────────────────────────────────────────────────────────
st.markdown('<div class="glass chat-area">', unsafe_allow_html=True)

if not st.session_state.display:
    st.markdown(
        f"""
    <div class="empty-state">
        <div class="big">{p["emoji"]}</div>
        <p>I'm in <strong style="color:#e2e8f0">{p["name"]}</strong> mode.<br>{p["tagline"]}.<br>Say something…</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.display:
        if msg["role"] == "user":
            st.markdown(
                f"""
            <div class="msg-row ur">
                <div class="bwrap">
                    <div class="bubble ub">{msg["text"]}</div>
                    <div class="mts">{msg["time"]}</div>
                </div>
                <div class="avi u">👤</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="msg-row">
                <div class="avi">{p["emoji"]}</div>
                <div class="bwrap">
                    <div class="bubble bb">{msg["text"]}</div>
                    <div class="mts">{msg["time"]}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

st.markdown("</div>", unsafe_allow_html=True)  # chat-area

# ── Ended state ────────────────────────────────────────────────────────────────
if st.session_state.ended:
    st.markdown(
        f"""
    <div class="glass ended-wrap">
        <div style="font-size:2rem;margin-bottom:10px">{p["emoji"]}</div>
        <div style="color:#e2e8f0;font-weight:700;font-size:1rem">Session ended</div>
        <div style="color:#475569;font-size:0.8rem;margin-top:6px">Switch personality above to start again</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.markdown("</div>", unsafe_allow_html=True)  # wrap

# ── Input ──────────────────────────────────────────────────────────────────────
prompt = st.chat_input(f"Talk to {p['name']} Bot… (type 0 to exit)")

if prompt:
    now = datetime.now().strftime("%H:%M")

    # mirrors: messages.append(HumanMessage(content=prompt))
    st.session_state.lc_messages.append(HumanMessage(content=prompt))

    # mirrors: if prompt == "0": break
    if prompt.strip() == "0":
        st.session_state.display.append({"role": "user", "text": prompt, "time": now})
        st.session_state.ended = True
        st.rerun()

    st.session_state.display.append({"role": "user", "text": prompt, "time": now})

    # mirrors: model = ChatMistralAI(...); res = model.invoke(messages)
    with st.spinner(p["spinner"]):
        model = ChatMistralAI(model="mistral-small-2603")
        res = model.invoke(st.session_state.lc_messages)

    # mirrors: messages.append(AIMessage(content=res.content))
    st.session_state.lc_messages.append(AIMessage(content=res.content))

    bot_time = datetime.now().strftime("%H:%M")
    st.session_state.display.append(
        {"role": "bot", "text": res.content, "time": bot_time}
    )

    st.rerun()
