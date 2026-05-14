import streamlit as st

def inject_css() -> None:
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

<style>
:root {
  --bg-base:      #080B10;
  --bg-panel:     #0E1318;
  --bg-card:      #141A22;
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
}
html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
[data-testid="block-container"] {
  padding: 1.5rem 2rem 3rem !important;
  max-width: 100% !important;
}
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

/* HEADER */
.hse-header {
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border);
  padding-bottom: 1.25rem; margin-bottom: 1.75rem; position: relative;
}
.hse-header::after {
  content: ''; position: absolute; bottom: -1px; left: 0;
  width: 220px; height: 1px;
  background: linear-gradient(90deg, var(--cyan), transparent);
}
.hse-title {
  font-size: 26px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  background: linear-gradient(90deg, var(--cyan) 0%, #7EEEFF 60%, var(--text-primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
}
.hse-sub  { font-size: 12px; font-family: 'Fira Code', monospace; color: var(--text-sec); letter-spacing: 0.06em; margin: 0; }
.hse-meta { text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.hse-clock { font-family: 'Fira Code', monospace; font-size: 22px; color: var(--amber); letter-spacing: 0.08em; font-weight: 500; }
.hse-date  { font-size: 12px; font-family: 'Fira Code', monospace; color: var(--text-sec); }
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

/* SECTION LABEL */
.section-label {
  font-size: 11px; font-family: 'Fira Code', monospace; color: var(--cyan);
  letter-spacing: 0.18em; text-transform: uppercase; margin: 0 0 12px;
  display: flex; align-items: center; gap: 8px;
}
.section-label::before { content: '//'; color: var(--text-dim); }

/* KPI CARDS */
.kpi-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 4px; padding: 18px 20px 16px;
  position: relative; overflow: hidden; transition: border-color 0.2s;
}
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-card.amber::before { background: var(--amber); box-shadow: var(--glow-amber); }
.kpi-card.cyan::before  { background: var(--cyan);  box-shadow: var(--glow-cyan);  }
.kpi-card.red::before   { background: var(--red);   box-shadow: var(--glow-red);   }
.kpi-card.green::before { background: var(--green); }
.kpi-card:hover { border-color: rgba(0,212,255,0.3); }
.kpi-label { font-size: 10px; font-family: 'Fira Code', monospace; color: var(--text-sec); letter-spacing: 0.12em; text-transform: uppercase; margin: 0 0 8px; }
.kpi-value { font-size: 38px; font-weight: 700; line-height: 1; margin: 0 0 6px; letter-spacing: -0.01em; }
.kpi-card.amber .kpi-value { color: var(--amber); }
.kpi-card.cyan  .kpi-value { color: var(--cyan);  }
.kpi-card.red   .kpi-value { color: var(--red);   }
.kpi-card.green .kpi-value { color: var(--green); }
.kpi-delta { font-size: 11px; font-family: 'Fira Code', monospace; color: var(--text-sec); }
.kpi-delta .up   { color: var(--green); }
.kpi-delta .down { color: var(--red); }
.kpi-icon  { position: absolute; top: 16px; right: 16px; font-size: 28px; opacity: 0.12; }

/* PANEL */
.panel { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 4px; padding: 20px 22px; margin-bottom: 4px; }
.panel-title { font-size: 13px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-primary); margin: 0 0 16px; }
.panel-title span.accent { color: var(--cyan); }

/* SHIFT BAR */
.shift-row { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.shift-name { font-family: 'Fira Code', monospace; font-size: 11px; color: var(--text-sec); width: 80px; flex-shrink: 0; }
.shift-sub  { font-size: 9px; font-family: 'Fira Code'; color: var(--text-dim); margin-top: 1px; }
.shift-bar-track { flex: 1; height: 8px; background: rgba(255,255,255,0.05); border-radius: 1px; overflow: hidden; }
.shift-bar-fill  { height: 100%; border-radius: 1px; }
.shift-pct { font-family: 'Fira Code', monospace; font-size: 14px; font-weight: 500; width: 50px; text-align: right; flex-shrink: 0; }
.good { background: var(--green); color: var(--green); }
.warn { background: var(--amber); color: var(--amber); }
.crit { background: var(--red);   color: var(--red);   }

/* APD ROW */
.apd-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.apd-row:last-child { border-bottom: none; }
.apd-name  { font-size: 13px; font-weight: 600; letter-spacing: 0.08em; }
.apd-count { font-family: 'Fira Code', monospace; font-size: 20px; font-weight: 500; }
.apd-lbl   { font-size: 10px; font-family: 'Fira Code', monospace; color: var(--text-sec); margin-top: 1px; }

/* VIOLATION TABLE */
.vtable { width: 100%; border-collapse: collapse; font-size: 12px; }
.vtable th { font-family: 'Fira Code', monospace; font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-sec); padding: 8px 12px; border-bottom: 1px solid var(--border); text-align: left; font-weight: 400; }
.vtable td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.03); color: var(--text-primary); font-size: 13px; }
.vtable tr:hover td { background: rgba(0,212,255,0.03); }
.badge-v          { display: inline-block; font-family: 'Fira Code', monospace; font-size: 9px; letter-spacing: 0.08em; padding: 2px 7px; border-radius: 2px; font-weight: 500; }
.badge-verified   { background: rgba(61,204,126,0.15);  color: var(--green);    border: 1px solid rgba(61,204,126,0.3); }
.badge-unverified { background: rgba(245,166,35,0.15);  color: var(--amber);    border: 1px solid rgba(245,166,35,0.3); }
.badge-false      { background: rgba(122,138,153,0.15); color: var(--text-sec); border: 1px solid rgba(122,138,153,0.3); }
.apd-tag { display: inline-block; font-family: 'Fira Code', monospace; font-size: 9px; padding: 2px 6px; border-radius: 2px; margin-right: 3px; background: rgba(255,59,59,0.12); color: var(--red); border: 1px solid rgba(255,59,59,0.25); }
.hse-divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)