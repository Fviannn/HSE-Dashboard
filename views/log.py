"""
views/log.py — Log Pelanggara
Tabel dengan filter status/shift/search + date range + pagination + export CSV.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import badge_html, apd_tags


ROWS_PER_PAGE = 15


def render(df_viol: pd.DataFrame, is_live: bool):

    st.markdown('<p class="section-label">Log Pelanggaran</p>', unsafe_allow_html=True)

    # ── Filter bar ────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([1, 1, 1, 1.5])

    with fc1:
        filter_status = st.selectbox(
            "Status", ["Semua", "unverified", "verified", "confirmed", "false_alarm"],
            label_visibility="collapsed", key="log_status",
        )
    with fc2:
        filter_shift = st.selectbox(
            "Shift", ["Semua Shift", "PAGI", "SIANG", "MALAM"],
            label_visibility="collapsed", key="log_shift",
        )
    with fc3:
        search_worker = st.text_input(
            "Cari", placeholder="Nama pekerja...",
            label_visibility="collapsed", key="log_search",
        )
    with fc4:
        today = datetime.now().date()
        date_range = st.date_input(
            "Rentang Tanggal",
            value=(today - timedelta(days=7), today),
            label_visibility="collapsed",
            key="log_date",
        )

    # ── Apply filters ─────────────────────────────────────────────────────
    df_show = df_viol.copy()
    if not df_show.empty:
        if filter_status != "Semua":
            df_show = df_show[df_show["status"] == filter_status]

        if filter_shift != "Semua Shift" and "shift" in df_show.columns:
            df_show = df_show[df_show["shift"] == filter_shift]

        if search_worker.strip() and "worker" in df_show.columns:
            df_show = df_show[
                df_show["worker"].str.contains(search_worker.strip(), case=False, na=False)
            ]

        # Date filter — parse "dd/mm HH:MM" format from time column
        if isinstance(date_range, tuple) and len(date_range) == 2 and "time" in df_show.columns:
            start_d, end_d = date_range
            try:
                # Parse dates from "dd/mm HH:MM" format
                current_year = datetime.now().year
                df_show = df_show[df_show["time"].apply(
                    lambda t: _date_in_range(t, start_d, end_d, current_year)
                )]
            except Exception:
                pass  # skip date filter if parsing fails

    # ── Pagination ────────────────────────────────────────────────────────
    total_rows  = len(df_show)
    total_pages = max((total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE, 1)

    if "log_page" not in st.session_state:
        st.session_state.log_page = 1
    # Reset page if filters changed
    if st.session_state.log_page > total_pages:
        st.session_state.log_page = 1

    current_page = st.session_state.log_page
    start_idx    = (current_page - 1) * ROWS_PER_PAGE
    end_idx      = start_idx + ROWS_PER_PAGE
    df_page      = df_show.iloc[start_idx:end_idx]

    # ── Table ─────────────────────────────────────────────────────────────
    rows_html = ""
    for _, row in df_page.iterrows():
        rows_html += f"""
        <tr>
          <td><span style="font-family:'Fira Code';font-size:11px;
                           color:var(--text-sec)">{row.get('time','—')}</span></td>
          <td><b>{row.get('worker','—')}</b></td>
          <td><span style="font-family:'Fira Code';font-size:11px;
                           color:#00D4FF">{row.get('shift','—')}</span></td>
          <td>{apd_tags(row.get('apd','—'))}</td>
          <td>{badge_html(row.get('status','unverified'))}</td>
        </tr>"""

    if not rows_html:
        rows_html = """<tr>
          <td colspan="5" style="text-align:center;color:var(--text-dim);padding:32px">
            Tidak ada data untuk filter yang dipilih
          </td></tr>"""

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

    # ── Pagination controls ──────────────────────────────────────────────
    if total_pages > 1:
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        with pc1:
            if st.button("◀  Sebelumnya", use_container_width=True, key="log_prev",
                         disabled=(current_page <= 1)):
                st.session_state.log_page = current_page - 1
                st.rerun()
        with pc2:
            st.markdown(
                f'<div class="page-info">Halaman {current_page} dari {total_pages}'
                f' · {total_rows} record</div>',
                unsafe_allow_html=True,
            )
        with pc3:
            if st.button("Selanjutnya  ▶", use_container_width=True, key="log_next",
                         disabled=(current_page >= total_pages)):
                st.session_state.log_page = current_page + 1
                st.rerun()

    # ── Export ────────────────────────────────────────────────────────────
    btn_col, info_col = st.columns([1, 5])
    with btn_col:
        export_cols = [c for c in ["time", "worker", "shift", "apd", "status"]
                       if c in df_show.columns]
        csv = df_show[export_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇  Export CSV", csv,
            file_name=f"log_apd_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv", use_container_width=True,
        )
    with info_col:
        st.caption(
            f"Menampilkan **{len(df_page)}** dari **{total_rows}** record "
            f"(total: **{len(df_viol)}**)"
        )


def _date_in_range(time_str: str, start_d, end_d, year: int) -> bool:
    """Check if a 'dd/mm HH:MM' string falls within date range."""
    try:
        parts = time_str.split(" ")[0].split("/")
        day, month = int(parts[0]), int(parts[1])
        d = datetime(year, month, day).date()
        return start_d <= d <= end_d
    except Exception:
        return True  # include if can't parse