"""
views/analytics.py — Analytics / KPI Dashboard
KPI cards + trend chart + shift compliance + donut APD + bar 7 hari.
"""

import streamlit as st
from config import SHIFT_DISPLAY
from components.charts import chart_trend, chart_apd_donut, chart_daily_violations
from utils.helpers import color_class


def render(summary: dict, shift_compliance: dict, df_trend, is_live: bool):

    # ── KPI Cards ────────────────────────────────────────────────────────
    st.markdown('<p class="section-label">KPI Utama</p>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    compliance = summary["overall_compliance"]
    comp_color = "green" if compliance >= 87 else "amber" if compliance >= 75 else "red"
    total_v    = summary["total_violations"]

    with c1:
        st.markdown(f"""
        <div class="kpi-card {comp_color}">
          <span class="kpi-icon">&#x2B21;</span>
          <p class="kpi-label">Kepatuhan Keseluruhan</p>
          <p class="kpi-value">{compliance}%</p>
          <p class="kpi-delta">dari foto yang diproses</p>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card red">
          <span class="kpi-icon">&#x26A0;</span>
          <p class="kpi-label">Total Pelanggaran</p>
          <p class="kpi-value">{total_v}</p>
          <p class="kpi-delta">keseluruhan tercatat</p>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card amber">
          <span class="kpi-icon">&#x25CE;</span>
          <p class="kpi-label">Perlu Diverifikasi</p>
          <p class="kpi-value">{summary['unverified']}</p>
          <p class="kpi-delta">dari {total_v} total</p>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card cyan">
          <span class="kpi-icon">&#x2713;</span>
          <p class="kpi-label">Sudah Diverifikasi</p>
          <p class="kpi-value">{summary['verified']}</p>
          <p class="kpi-delta"><span class="up">{summary['false_alarms']}</span> false alarm</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Trend + Shift ────────────────────────────────────────────────────
    col_t, col_s = st.columns([3, 1])

    with col_t:
        st.markdown(
            '<div class="panel">'
            '<p class="panel-title">Trend Kepatuhan '
            '<span class="accent">30 Hari</span></p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_trend(df_trend), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s:
        st.markdown(
            '<div class="panel">'
            '<p class="panel-title">Per <span class="accent">Shift</span></p>',
            unsafe_allow_html=True,
        )
        for name, time_range in SHIFT_DISPLAY.items():
            rate = shift_compliance.get(name, 0.0)
            cls  = color_class(rate)
            st.markdown(f"""
            <div class="shift-row">
              <div>
                <div class="shift-name">{name}</div>
                <div class="shift-sub">{time_range}</div>
              </div>
              <div class="shift-bar-track">
                <div class="shift-bar-fill {cls}" style="width:{rate}%"></div>
              </div>
              <div class="shift-pct {cls}">{rate}%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Donut APD + Bar 7 Hari ───────────────────────────────────────────
    col_d, col_b = st.columns([1.2, 1.4])

    with col_d:
        st.markdown(
            '<div class="panel">'
            '<p class="panel-title">Jenis <span class="accent">APD</span></p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_apd_donut(summary), use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown(
            '<div class="panel">'
            '<p class="panel-title">Pelanggaran <span class="accent">7 Hari</span></p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(chart_daily_violations(df_trend), use_container_width=True,
                        config={"displayModeBar": False})

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
              <div>
                <div class="apd-name" style="color:{color}">{apd}</div>
                <div class="apd-lbl">{pct}% dari total</div>
              </div>
              <div class="apd-count" style="color:{color}">{count}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
