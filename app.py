import time
import streamlit as st
from datetime import datetime

from config import REFRESH_INTERVAL, SHIFT_DISPLAY
from components.styles import inject_css
from components.charts import (
    chart_trend,
    chart_apd_donut, chart_daily_violations,
)
from utils.data import fetch_data
from utils.helpers import color_class, badge_html, apd_tags

# PAGE CONFIG
st.set_page_config(
    page_title="APD Monitor — HSE Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# AUTO-REFRESH
def init_refresh():
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()

# MAIN
def main():
    inject_css()
    init_refresh()

    summary, shift_compliance, df_trend, df_viol, is_live = fetch_data()
    now = datetime.now()

    # ── HEADER ──
    sc = "status-live" if is_live else "status-demo"
    sl = "LIVE · BACKEND" if is_live else "DEMO · BACKEND OFFLINE"
    st.markdown(f"""
    <div class="hse-header">
      <div>
        <p class="hse-title">APD Monitor</p>
        <p class="hse-sub">HSE KPI Dashboard</p>
      </div>
      <div class="hse-meta">
        <div class="hse-date">{now.strftime('%A, %d %B %Y')}</div>
        <div class="{sc} status-pill"><div class="status-dot"></div>{sl}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Jam diupdate oleh while True di bawah
    clock_placeholder = st.empty()

    # KPI Cards 
    st.markdown('<p class="section-label">KPI Utama</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    compliance = summary["overall_compliance"]
    comp_color = "green" if compliance >= 87 else "amber" if compliance >= 75 else "red"
    total_v    = summary["total_violations"]

    with c1:
        st.markdown(f"""
        <div class="kpi-card {comp_color}">
          <span class="kpi-icon">⬡</span>
          <p class="kpi-label">Kepatuhan Keseluruhan</p>
          <p class="kpi-value">{compliance}%</p>
          <p class="kpi-delta">dari foto yang diproses</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card red">
          <span class="kpi-icon">⚠</span>
          <p class="kpi-label">Total Pelanggaran</p>
          <p class="kpi-value">{total_v}</p>
          <p class="kpi-delta">keseluruhan tercatat</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card amber">
          <span class="kpi-icon">◎</span>
          <p class="kpi-label">Perlu Diverifikasi</p>
          <p class="kpi-value">{summary['unverified']}</p>
          <p class="kpi-delta">dari {total_v} total</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <span class="kpi-icon">✓</span>
          <p class="kpi-label">Sudah Diverifikasi</p>
          <p class="kpi-value">{summary['verified']}</p>
          <p class="kpi-delta"><span class="up">{summary['false_alarms']}</span> false alarm</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Trend & Shift
    col_t, col_s = st.columns([3, 1])
    with col_t:
        st.markdown('<div class="panel"><p class="panel-title">Trend Kepatuhan <span class="accent">30 Hari</span></p>', unsafe_allow_html=True)
        st.plotly_chart(chart_trend(df_trend), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col_s:
        st.markdown('<div class="panel"><p class="panel-title">Per <span class="accent">Shift</span></p>', unsafe_allow_html=True)
        for name, time_range in SHIFT_DISPLAY.items():
            rate = shift_compliance.get(name, 0.0)
            cls  = color_class(rate)
            st.markdown(f"""
            <div class="shift-row">
              <div><div class="shift-name">{name}</div><div class="shift-sub">{time_range}</div></div>
              <div class="shift-bar-track"><div class="shift-bar-fill {cls}" style="width:{rate}%"></div></div>
              <div class="shift-pct {cls}">{rate}%</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Heatmap + Donut + Bar
    col_d, col_b = st.columns([1.2, 1.4])
    with col_d:
        st.markdown('<div class="panel"><p class="panel-title">Jenis <span class="accent">APD</span></p>', unsafe_allow_html=True)
        st.plotly_chart(chart_apd_donut(summary), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="panel"><p class="panel-title">Pelanggaran <span class="accent">7 Hari</span></p>', unsafe_allow_html=True)
        st.plotly_chart(chart_daily_violations(df_trend), use_container_width=True, config={"displayModeBar": False})
        total_apd = (summary["missing_helmet_count"] +
                     summary["missing_vest_count"] +
                     summary["missing_mask_count"])
        for apd, key, color in [
            ("HELM",   "missing_helmet_count", "#FF3B3B"),
            ("ROMPI",  "missing_vest_count",   "#F5A623"),
            ("MASKER", "missing_mask_count",   "#00D4FF"),
        ]:
            count = summary[key]
            pct   = round(count / total_apd * 100) if total_apd else 0
            st.markdown(f"""
            <div class="apd-row">
              <div><div class="apd-name" style="color:{color}">{apd}</div><div class="apd-lbl">{pct}% dari total</div></div>
              <div class="apd-count" style="color:{color}">{count}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Tabel Violation
    st.markdown('<p class="section-label">Pelanggaran Terbaru</p>', unsafe_allow_html=True)
    fc1, fc2, _ = st.columns([1, 1, 4])
    with fc1:
        filter_status = st.selectbox("Status", ["Semua","unverified","verified","false_alarm"],
                                     label_visibility="collapsed")
    with fc2:
        filter_shift = st.selectbox("Shift", ["Semua Shift","PAGI","SIANG","MALAM"],
                                    label_visibility="collapsed")

    df_show = df_viol.copy()
    if not df_show.empty:
        if filter_status != "Semua":
            df_show = df_show[df_show["status"] == filter_status]
        if filter_shift != "Semua Shift":
            df_show = df_show[df_show["shift"] == filter_shift]

    rows_html = ""
    for _, row in df_show.head(12).iterrows():
        rows_html += f"""
        <tr>
          <td><span style="font-family:'Fira Code';font-size:11px;color:var(--text-sec)">{row['time']}</span></td>
          <td><b>{row['worker']}</b></td>
          <td><span style="font-family:'Fira Code';font-size:11px;color:#00D4FF">{row['shift']}</span></td>
          <td>{apd_tags(row['apd'])}</td>
          <td>{badge_html(row['status'])}</td>
        </tr>"""
    if not rows_html:
        rows_html = '<tr><td colspan="6" style="text-align:center;color:var(--text-dim);padding:24px">Tidak ada data</td></tr>'

    st.markdown(f"""
    <div class="panel">
      <table class="vtable">
        <thead><tr>
          <th>Waktu</th><th>Pekerja</th>
          <th>Shift</th><th>APD Dilanggar</th><th>Status</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)

    # FOOTER 
    st.markdown(f"""
    <hr class="hse-divider">
    <div style="display:flex;justify-content:space-between">
      <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
        APD MONITOR v1.1 · HSE EPSON MFG · {'LIVE DATA' if is_live else 'DEMO MODE'}
      </span>
      <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
        Shift dihitung dari timestamp · Area dari camera_location
      </span>
    </div>""", unsafe_allow_html=True)

    # LIVE CLOCK + AUTO REFRESH 
    while True:
        clock_placeholder.markdown(
            f'<div class="hse-clock">{datetime.now().strftime("%H:%M:%S")}</div>',
            unsafe_allow_html=True,
        )
        elapsed = time.time() - st.session_state.last_refresh
        if elapsed >= REFRESH_INTERVAL:
            st.session_state.last_refresh = time.time()
            fetch_data.clear()
            st.rerun()
        time.sleep(1)


if __name__ == "__main__":
    main()