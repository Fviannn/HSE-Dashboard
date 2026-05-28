import streamlit as st


def inject_css() -> None:
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ═══════════════════════════════════════════════════════════════════════ */
:root {
  --bg-base:      #080B10;
  --bg-panel:     #0E1318;
  --bg-card:      #141A22;
  --bg-hover:     #1A2230;
  --amber:        #F5A623;
  --amber-dim:    #7A5012;
  --cyan:         #00D4FF;
  --cyan-dim:     #004F61;
  --red:          #FF3B3B;
  --green:        #3DCC7E;
  --text-primary: #E8EDF2;
  --text-sec:     #7A8A99;
  --text-dim:     #3E4D5C;
  --border:       rgba(0,212,255,0.12);
  --border-amber: rgba(245,166,35,0.25);
  --glow-cyan:    0 0 20px rgba(0,212,255,0.25);
  --glow-amber:   0 0 20px rgba(245,166,35,0.35);
  --glow-red:     0 0 20px rgba(255,59,59,0.35);
  --glow-green:   0 0 20px rgba(61,204,126,0.35);
}

/* ═══════════════════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: 'Rajdhani', sans-serif !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stHeader"] {
  background: transparent !important;
}

/* Hide sidebar completely — not used in this layout */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
  display: none !important;
}

[data-testid="block-container"] {
  padding: 1.5rem 2rem 3rem !important;
  max-width: 100% !important;
}

/* Grid background */
[data-testid="stAppViewContainer"]::before {
  content: ''; position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px; pointer-events: none; z-index: 0;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--cyan-dim); border-radius: 2px; }

/* ═══════════════════════════════════════════════════════════════════════
   HEADER STATS BAR
   ═══════════════════════════════════════════════════════════════════════ */
.header-stats {
  display: flex; align-items: center; gap: 0;
  height: 100%; padding-top: .6rem;
}
.header-stat {
  display: flex; flex-direction: column; align-items: center;
  padding: 0 1.2rem;
}
.header-stat-label {
  font-size: .6rem; font-family: 'Fira Code', monospace;
  color: var(--text-dim); letter-spacing: .1em;
  text-transform: uppercase;
}
.header-stat-value {
  font-size: 1.1rem; font-weight: 700;
  font-family: 'Fira Code', monospace;
  line-height: 1.3;
}
.header-stat-sep {
  width: 1px; height: 28px;
  background: var(--border);
}

/* ═══════════════════════════════════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════════════════════════════════ */
.hse-title {
  font-size: 26px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  background: linear-gradient(90deg, var(--cyan) 0%, #7EEEFF 60%, var(--text-primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
.hse-sub {
  font-size: 12px; font-family: 'Fira Code', monospace;
  color: var(--text-sec); letter-spacing: 0.06em; margin: 0;
}
.hse-clock {
  font-family: 'Fira Code', monospace; font-size: 22px;
  color: var(--amber); letter-spacing: 0.08em; font-weight: 500;
}
.hse-date {
  font-size: 12px; font-family: 'Fira Code', monospace; color: var(--text-sec);
}

/* Status pill (LIVE / DEMO) */
.status-pill {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: 'Fira Code', monospace; font-size: 10px; letter-spacing: 0.1em;
  padding: 3px 10px; border-radius: 2px; margin-top: 4px;
}
.status-live { background: rgba(61,204,126,0.12); border: 1px solid rgba(61,204,126,0.4); color: var(--green); }
.status-demo { background: rgba(245,166,35,0.12); border: 1px solid var(--border-amber); color: var(--amber); }
.status-dot  { width: 6px; height: 6px; border-radius: 50%; animation: blink 1.8s ease-in-out infinite; }
.status-live .status-dot { background: var(--green); }
.status-demo .status-dot { background: var(--amber); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ═══════════════════════════════════════════════════════════════════════
   NAV BUTTONS
   ═══════════════════════════════════════════════════════════════════════ */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--text-sec) !important;
  border-radius: 3px !important;
  font-family: 'Fira Code', monospace !important;
  font-size: .72rem !important;
  letter-spacing: .06em !important;
  text-transform: uppercase !important;
  padding: .35rem 1rem !important;
  transition: all 0.2s ease !important;
  min-height: 0 !important;
  height: auto !important;
}
.stButton > button:hover {
  color: var(--cyan) !important;
  border-color: var(--cyan) !important;
  background: rgba(0,212,255,0.05) !important;
}
.stButton > button[kind="primary"] {
  color: var(--cyan) !important;
  border-color: var(--cyan) !important;
  background: rgba(0,212,255,0.08) !important;
  box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: rgba(0,212,255,0.14) !important;
}

/* ═══════════════════════════════════════════════════════════════════════
   SECTION LABEL
   ═══════════════════════════════════════════════════════════════════════ */
.section-label {
  font-size: 11px; font-family: 'Fira Code', monospace; color: var(--cyan);
  letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 12px;
  display: flex; align-items: center; gap: 8px;
}
.section-label::before { content: '//'; color: var(--text-dim); }

/* ═══════════════════════════════════════════════════════════════════════
   KPI CARDS
   ═══════════════════════════════════════════════════════════════════════ */
.kpi-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 4px; padding: 18px 20px 16px;
  position: relative; overflow: hidden;
  transition: border-color 0.25s, transform 0.2s, box-shadow 0.25s;
}
.kpi-card:hover {
  border-color: rgba(0,212,255,0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.kpi-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.kpi-card.amber::before { background: var(--amber); box-shadow: var(--glow-amber); }
.kpi-card.cyan::before  { background: var(--cyan);  box-shadow: var(--glow-cyan);  }
.kpi-card.red::before   { background: var(--red);   box-shadow: var(--glow-red);   }
.kpi-card.green::before { background: var(--green); box-shadow: var(--glow-green); }
.kpi-label {
  font-size: 10px; font-family: 'Fira Code', monospace;
  color: var(--text-sec); letter-spacing: 0.12em;
  text-transform: uppercase; margin: 0 0 8px;
}
.kpi-value {
  font-size: 38px; font-weight: 700; line-height: 1;
  margin: 0 0 6px; letter-spacing: -0.01em;
}
.kpi-card.amber .kpi-value { color: var(--amber); }
.kpi-card.cyan  .kpi-value { color: var(--cyan);  }
.kpi-card.red   .kpi-value { color: var(--red);   }
.kpi-card.green .kpi-value { color: var(--green); }
.kpi-delta { font-size: 11px; font-family: 'Fira Code', monospace; color: var(--text-sec); }
.kpi-delta .up   { color: var(--green); }
.kpi-delta .down { color: var(--red); }
.kpi-icon  { position: absolute; top: 16px; right: 16px; font-size: 28px; opacity: 0.12; }

/* ═══════════════════════════════════════════════════════════════════════
   PANEL
   ═══════════════════════════════════════════════════════════════════════ */
.panel {
  background: var(--bg-panel); border: 1px solid var(--border);
  border-radius: 4px; padding: 20px 22px; margin-bottom: 4px;
}
.panel-title {
  font-size: 13px; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--text-primary); margin: 0 0 16px;
}
.panel-title span.accent { color: var(--cyan); }

/* ═══════════════════════════════════════════════════════════════════════
   LIVE FEED PANEL
   ═══════════════════════════════════════════════════════════════════════ */
.live-feed-container {
  position: relative; border-radius: 6px; overflow: hidden;
  border: 1px solid var(--border); background: var(--bg-card);
}
.live-feed-container img {
  width: 100%; display: block; border-radius: 5px;
}
.live-feed-container.is-live {
  border-color: rgba(61,204,126,0.4);
  animation: livePulse 3s ease-in-out infinite;
}
@keyframes livePulse {
  0%,100% { box-shadow: 0 0 0 rgba(61,204,126,0); }
  50%     { box-shadow: 0 0 20px rgba(61,204,126,0.15); }
}

/* Live badge overlay */
.live-badge {
  position: absolute; top: 10px; left: 10px; z-index: 10;
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(8,11,16,0.85); backdrop-filter: blur(8px);
  padding: 4px 10px; border-radius: 3px;
  font-family: 'Fira Code', monospace; font-size: 10px;
  letter-spacing: 0.1em; text-transform: uppercase;
}
.live-badge.on  { color: var(--green); border: 1px solid rgba(61,204,126,0.4); }
.live-badge.off { color: var(--text-dim); border: 1px solid var(--border); }
.live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  animation: blink 1.4s ease-in-out infinite;
}
.live-badge.on .live-dot  { background: var(--green); }
.live-badge.off .live-dot { background: var(--text-dim); animation: none; }

/* Scanline overlay */
.live-scanline {
  position: absolute; inset: 0; pointer-events: none; z-index: 5;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,212,255,0.015) 2px,
    rgba(0,212,255,0.015) 4px
  );
}

/* Camera offline placeholder */
.cam-offline {
  height: 280px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 12px;
  background: var(--bg-card); border-radius: 6px;
  border: 1px dashed var(--border);
}
.cam-offline-icon {
  font-size: 48px; opacity: 0.15;
  animation: camPulse 3s ease-in-out infinite;
}
@keyframes camPulse {
  0%,100% { opacity: 0.1; transform: scale(1); }
  50%     { opacity: 0.2; transform: scale(1.05); }
}
.cam-offline-text {
  font-family: 'Fira Code', monospace; font-size: 12px;
  color: var(--text-dim); letter-spacing: 0.06em;
}

/* ═══════════════════════════════════════════════════════════════════════
   DETECTION / VERIFICATION CARD
   ═══════════════════════════════════════════════════════════════════════ */
.det-card {
  background: var(--bg-card); border-radius: 6px;
  padding: .75rem 1rem; margin: .5rem 0;
  border: 1px solid var(--border);
  transition: border-color 0.2s;
}
.det-card:hover { border-color: rgba(0,212,255,0.25); }
.det-card-header {
  font-size: .68rem; font-family: 'Fira Code', monospace;
  color: var(--text-sec); margin-bottom: .5rem;
  letter-spacing: .08em; text-transform: uppercase;
}
.det-grid {
  display: flex; gap: 2.5rem; flex-wrap: wrap;
}
.det-field-label {
  font-size: .65rem; color: var(--text-dim);
  font-family: 'Fira Code', monospace;
}
.det-field-value {
  font-weight: 700; font-size: .95rem; margin-top: 2px;
}

/* ═══════════════════════════════════════════════════════════════════════
   SHIFT BAR
   ═══════════════════════════════════════════════════════════════════════ */
.shift-row {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px;
}
.shift-name {
  font-family: 'Fira Code', monospace; font-size: 11px;
  color: var(--text-sec); width: 80px; flex-shrink: 0;
}
.shift-sub {
  font-size: 9px; font-family: 'Fira Code', monospace;
  color: var(--text-dim); margin-top: 1px;
}
.shift-bar-track {
  flex: 1; height: 8px; background: rgba(255,255,255,0.05);
  border-radius: 1px; overflow: hidden;
}
.shift-bar-fill {
  height: 100%; border-radius: 1px;
  transition: width 0.6s ease;
}
.shift-pct {
  font-family: 'Fira Code', monospace; font-size: 14px;
  font-weight: 500; width: 50px; text-align: right; flex-shrink: 0;
}
.good { background: var(--green); color: var(--green); }
.warn { background: var(--amber); color: var(--amber); }
.crit { background: var(--red);   color: var(--red);   }

/* ═══════════════════════════════════════════════════════════════════════
   APD ROW (sidebar donut detail)
   ═══════════════════════════════════════════════════════════════════════ */
.apd-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.apd-row:last-child { border-bottom: none; }
.apd-name  { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; }
.apd-count { font-family: 'Fira Code', monospace; font-size: 20px; font-weight: 500; }
.apd-lbl   { font-size: 10px; font-family: 'Fira Code', monospace; color: var(--text-sec); margin-top: 1px; }

/* ═══════════════════════════════════════════════════════════════════════
   VIOLATION TABLE
   ═══════════════════════════════════════════════════════════════════════ */
.vtable { width: 100%; border-collapse: collapse; font-size: 12px; }
.vtable th {
  font-family: 'Fira Code', monospace; font-size: 10px;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--text-sec); padding: 8px 12px;
  border-bottom: 1px solid var(--border); text-align: left; font-weight: 400;
}
.vtable td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  color: var(--text-primary); font-size: 13px;
  transition: background 0.15s;
}
.vtable tr:nth-child(even) td { background: rgba(0,212,255,0.015); }
.vtable tr:hover td { background: rgba(0,212,255,0.05); }

/* Badges */
.badge-v {
  display: inline-block; font-family: 'Fira Code', monospace;
  font-size: 9px; letter-spacing: 0.08em; padding: 2px 7px;
  border-radius: 2px; font-weight: 500;
}
.badge-verified   { background: rgba(61,204,126,0.15);  color: var(--green);    border: 1px solid rgba(61,204,126,0.3); }
.badge-unverified { background: rgba(245,166,35,0.15);  color: var(--amber);    border: 1px solid rgba(245,166,35,0.3); }
.badge-false      { background: rgba(122,138,153,0.15); color: var(--text-sec); border: 1px solid rgba(122,138,153,0.3); }
.apd-tag {
  display: inline-block; font-family: 'Fira Code', monospace;
  font-size: 9px; padding: 2px 6px; border-radius: 2px; margin-right: 3px;
  background: rgba(255,59,59,0.12); color: var(--red); border: 1px solid rgba(255,59,59,0.25);
}

/* ═══════════════════════════════════════════════════════════════════════
   PAGINATION
   ═══════════════════════════════════════════════════════════════════════ */
.page-info {
  font-family: 'Fira Code', monospace; font-size: 11px;
  color: var(--text-sec); text-align: center; padding: 8px 0;
}

/* ═══════════════════════════════════════════════════════════════════════
   MISC
   ═══════════════════════════════════════════════════════════════════════ */
.hse-divider {
  border: none; border-top: 1px solid var(--border); margin: 1.5rem 0;
}

/* Streamlit input styling */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  font-family: 'Rajdhani', sans-serif !important;
  border-radius: 4px !important;
  transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 1px rgba(0,212,255,0.2) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
  background: var(--bg-card) !important;
  border-color: var(--border) !important;
}

/* Date input */
[data-testid="stDateInput"] input {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
}

/* Success/error messages */
[data-testid="stAlert"] {
  border-radius: 4px !important;
  font-family: 'Rajdhani', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)
