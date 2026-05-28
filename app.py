"""
app.py — APD Monitoring Dashboard v3.1
Jalankan: streamlit run app.py

v3.1:
  - Sidebar dihapus (fix bug toggle tidak bisa dibuka)
  - Quick stats dipindah ke header bar
  - Page switch lebih cepat (backend check di-cache)
"""

import time
import streamlit as st
from datetime import datetime

from config import REFRESH_INTERVAL
from components.styles import inject_css
from utils.data import fetch_data
from views import monitor, analytics, log


# ── Fragment: live clock ───────────────────────────────────────────────────
@st.fragment(run_every="1s")
def live_clock():
    """Update jam tiap detik tanpa re-render seluruh halaman."""
    now     = datetime.now()
    is_live = st.session_state.get("_is_live", False)
    sc      = "status-live" if is_live else "status-demo"
    sl      = "LIVE · BACKEND" if is_live else "DEMO · OFFLINE"

    st.markdown(f"""
    <div class="hse-clock">{now.strftime('%H:%M:%S')}</div>
    <div class="hse-date">{now.strftime('%A, %d %B %Y')}</div>
    <div class="{sc} status-pill">
      <div class="status-dot"></div>{sl}
    </div>""", unsafe_allow_html=True)

    # Auto-refresh data
    elapsed = time.time() - st.session_state.get("last_refresh", time.time())
    if elapsed >= REFRESH_INTERVAL:
        st.session_state.last_refresh = time.time()
        fetch_data.clear()
        st.rerun()


# ── State init ─────────────────────────────────────────────────────────────
def init_state():
    if "page"         not in st.session_state: st.session_state.page         = "monitor"
    if "last_refresh" not in st.session_state: st.session_state.last_refresh = time.time()
    if "_is_live"     not in st.session_state: st.session_state._is_live     = False


# ── Header ─────────────────────────────────────────────────────────────────
def render_header(is_live: bool, summary: dict):
    # Top bar: title + quick stats + clock
    col_title, col_stats, col_clock = st.columns([2.5, 4.5, 1.5])

    with col_title:
        st.markdown("""
        <div>
          <p class="hse-title">APD Monitor</p>
          <p class="hse-sub">HSE KPI Dashboard · PT Indonesia Epson Industry</p>
        </div>""", unsafe_allow_html=True)

    with col_stats:
        comp  = summary.get("overall_compliance", 0)
        unver = summary.get("unverified", 0)
        total = summary.get("total_violations", 0)
        comp_c = "#3DCC7E" if comp >= 87 else "#F5A623" if comp >= 75 else "#FF3B3B"
        conn_c = "#3DCC7E" if is_live else "#F5A623"
        conn_l = "LIVE" if is_live else "OFFLINE"

        st.markdown(f"""
        <div class="header-stats">
          <div class="header-stat">
            <span class="header-stat-label">Kepatuhan</span>
            <span class="header-stat-value" style="color:{comp_c}">{comp}%</span>
          </div>
          <div class="header-stat-sep"></div>
          <div class="header-stat">
            <span class="header-stat-label">Pelanggaran</span>
            <span class="header-stat-value" style="color:#FF3B3B">{total}</span>
          </div>
          <div class="header-stat-sep"></div>
          <div class="header-stat">
            <span class="header-stat-label">Verifikasi</span>
            <span class="header-stat-value" style="color:#F5A623">{unver}</span>
          </div>
          <div class="header-stat-sep"></div>
          <div class="header-stat">
            <span class="header-stat-label">Backend</span>
            <span class="header-stat-value" style="color:{conn_c}">{conn_l}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with col_clock:
        live_clock()

    # Divider line with cyan gradient
    st.markdown("""
    <div style="position:relative;border-bottom:1px solid var(--border);
                margin-bottom:.75rem;padding-top:.2rem">
      <div style="position:absolute;bottom:-1px;left:0;width:220px;height:1px;
                  background:linear-gradient(90deg,var(--cyan),transparent)"></div>
    </div>""", unsafe_allow_html=True)


# ── Nav buttons ────────────────────────────────────────────────────────────
def render_nav():
    cur = st.session_state.page
    n1, n2, n3, _ = st.columns([1.6, 1, 1.4, 6])
    with n1:
        if st.button("Monitor & Verifikasi", use_container_width=True,
                     type="primary" if cur == "monitor"   else "secondary",
                     key="nav_monitor"):
            st.session_state.page = "monitor"
            st.rerun()
    with n2:
        if st.button("Analytics", use_container_width=True,
                     type="primary" if cur == "analytics" else "secondary",
                     key="nav_analytics"):
            st.session_state.page = "analytics"
            st.rerun()
    with n3:
        if st.button("Log Pelanggaran", use_container_width=True,
                     type="primary" if cur == "log"       else "secondary",
                     key="nav_log"):
            st.session_state.page = "log"
            st.rerun()
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    inject_css()
    init_state()

    summary, shift_compliance, df_trend, df_viol, is_live = fetch_data()

    st.session_state._is_live = is_live

    render_header(is_live, summary)
    render_nav()

    # Render halaman aktif
    page = st.session_state.page
    if page == "monitor":
        monitor.render()
    elif page == "analytics":
        analytics.render(summary, shift_compliance, df_trend, is_live)
    elif page == "log":
        log.render(df_viol, is_live)

    # Footer
    sync_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <hr class="hse-divider">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem">
      <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
        APD MONITOR v3.1 · HSE EPSON MFG · {'LIVE DATA' if is_live else 'DEMO MODE'}
      </span>
      <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
        Capstone FILKOM UB 2026 · Kelompok 3 · Epson A.2
      </span>
      <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
        Sync: {sync_time} · Refresh tiap {REFRESH_INTERVAL}s
      </span>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    st.set_page_config(
        page_title="APD Monitor — HSE Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    main()
