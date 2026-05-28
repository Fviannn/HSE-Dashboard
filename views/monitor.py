"""
views/monitor.py — Monitor & Verifikasi
Panel kiri: Live camera feed (MJPEG stream atau polling capture)
Panel kanan: Antrian verifikasi pengawas K3
"""

import streamlit as st
import requests
from datetime import datetime

from config import BACKEND_URL, STREAM_URL
from utils.data import (
    fetch_detections_unverified,
    fetch_latest_capture,
    check_stream_available,
    verify_detection,
    _is_backend_alive,
)


def _apd_missing_label(det: dict) -> str:
    parts = []
    if not det.get("has_helmet"): parts.append("Helm")
    if not det.get("has_vest"):   parts.append("Rompi")
    if not det.get("has_mask"):   parts.append("Masker")
    return ", ".join(parts) if parts else "—"


def _img_url(capture_id: int, enhanced: bool = True) -> str:
    ep = "enhanced" if enhanced else "image"
    return f"{BACKEND_URL}/api/captures/{capture_id}/{ep}"


def _fetch_image(capture_id: int):
    """Coba ambil foto enhanced dulu, fallback ke original. Return bytes atau None."""
    for enhanced in [True, False]:
        try:
            resp = requests.get(_img_url(capture_id, enhanced), timeout=3)
            if resp.ok and "image" in resp.headers.get("content-type", ""):
                return resp.content
        except Exception:
            continue
    return None


# ══════════════════════════════════════════════════════════════════════════════
# LIVE CAMERA PANEL
# ══════════════════════════════════════════════════════════════════════════════
def _render_live_feed():
    """Render panel live camera feed."""
    st.markdown(
        '<p class="panel-title">Live <span class="accent">Camera</span></p>',
        unsafe_allow_html=True,
    )

    # Quick check — kalau backend mati, langsung tampilkan offline placeholder
    if not _is_backend_alive():
        st.markdown("""
        <div class="cam-offline">
          <div class="cam-offline-icon">&#x1F4F9;</div>
          <div class="cam-offline-text">
            Kamera tidak tersedia<br>
            <span style="font-size:10px;color:var(--text-dim)">
              Backend offline — stream endpoint belum aktif
            </span>
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("⟳  Refresh", use_container_width=True, key="btn_refresh_feed"):
            _is_backend_alive.clear()
            st.cache_data.clear()
            st.rerun()
        return

    stream_ok = check_stream_available()

    if stream_ok:
        # ── MJPEG Stream tersedia → embed langsung ──
        st.markdown(f"""
        <div class="live-feed-container is-live">
          <div class="live-badge on">
            <div class="live-dot"></div>LIVE STREAM
          </div>
          <div class="live-scanline"></div>
          <img src="{STREAM_URL}" alt="Live Camera Feed">
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;gap:1rem;margin-top:.6rem;flex-wrap:wrap;
                    align-items:center">
          <span style="font-family:'Fira Code';font-size:10px;color:var(--text-sec)">
            Stream: <b style="color:var(--green)">CONNECTED</b>
          </span>
          <span style="font-family:'Fira Code';font-size:10px;color:var(--text-dim)">
            {STREAM_URL}
          </span>
        </div>""", unsafe_allow_html=True)

    else:
        # ── Stream belum ada → fallback polling capture terbaru ──
        capture, cap_live = fetch_latest_capture()

        if capture:
            cap_id = capture.get("id")
            status = capture.get("status", "—")
            ts_raw = capture.get("captured_at", "")
            try:
                ts_str = datetime.fromisoformat(
                    ts_raw.split("+")[0].split("Z")[0]
                ).strftime("%d/%m/%Y %H:%M:%S")
            except Exception:
                ts_str = ts_raw[:19].replace("T", " ")

            img_bytes = _fetch_image(cap_id)

            badge_cls = "on" if cap_live else "off"
            badge_txt = "LATEST CAPTURE" if cap_live else "OFFLINE"

            if img_bytes:
                st.markdown(f"""
                <div class="live-feed-container {'is-live' if cap_live else ''}">
                  <div class="live-badge {badge_cls}">
                    <div class="live-dot"></div>{badge_txt}
                  </div>
                  <div class="live-scanline"></div>
                </div>""", unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
            else:
                st.markdown("""
                <div class="cam-offline">
                  <div class="cam-offline-icon">&#x1F4F7;</div>
                  <div class="cam-offline-text">Foto tidak tersedia</div>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;gap:1.2rem;margin-top:.6rem;flex-wrap:wrap">
              <span style="font-family:'Fira Code';font-size:11px;color:var(--text-sec)">
                ID: <b style="color:var(--cyan)">{cap_id}</b>
              </span>
              <span style="font-family:'Fira Code';font-size:11px;color:var(--text-sec)">
                Status: <b style="color:var(--amber)">{status.upper()}</b>
              </span>
              <span style="font-family:'Fira Code';font-size:11px;color:var(--text-sec)">
                {ts_str}
              </span>
            </div>""", unsafe_allow_html=True)

        else:
            # Backend offline total
            st.markdown("""
            <div class="cam-offline">
              <div class="cam-offline-icon">&#x1F4F9;</div>
              <div class="cam-offline-text">
                Kamera tidak tersedia<br>
                <span style="font-size:10px;color:var(--text-dim)">
                  Backend offline — stream endpoint belum aktif
                </span>
              </div>
            </div>""", unsafe_allow_html=True)

    if st.button("⟳  Refresh", use_container_width=True, key="btn_refresh_feed"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# VERIFICATION PANEL
# ══════════════════════════════════════════════════════════════════════════════
def _render_verification():
    """Render panel antrian verifikasi pengawas K3."""
    st.markdown(
        '<p class="panel-title">Antrian <span class="accent">Verifikasi</span></p>',
        unsafe_allow_html=True,
    )

    detections, det_live = fetch_detections_unverified()

    if not det_live:
        st.markdown("""
        <div style="font-family:'Fira Code';font-size:10px;color:var(--amber);
                    margin-bottom:.8rem;padding:.3rem .6rem;
                    background:rgba(245,166,35,0.08);border-radius:3px;
                    border:1px solid rgba(245,166,35,0.2)">
          DEMO MODE — data simulasi, belum terhubung ke backend
        </div>""", unsafe_allow_html=True)

    if not detections:
        st.markdown("""
        <div style="padding:2.5rem;text-align:center;
                    color:var(--green);font-family:'Fira Code';font-size:13px">
          &#x2713; Semua deteksi sudah diverifikasi
        </div>""", unsafe_allow_html=True)
        return

    # Counter
    st.markdown(f"""
    <div style="font-family:'Fira Code';font-size:11px;color:var(--amber);
                margin-bottom:.5rem">
      {len(detections)} deteksi menunggu verifikasi
    </div>""", unsafe_allow_html=True)

    # Dropdown pilih deteksi
    def _det_label(d):
        t = d.get("_time_str") or d.get("detected_at", "")[:16].replace("T", " ")
        missing = []
        if not d.get("has_helmet"): missing.append("Helm")
        if not d.get("has_vest"):   missing.append("Rompi")
        if not d.get("has_mask"):   missing.append("Masker")
        apd_str = "+".join(missing) if missing else "—"
        return f"#{d['id']} · {t} · {apd_str}"

    options = {_det_label(d): d for d in detections}
    selected_label = st.selectbox(
        "Pilih deteksi",
        list(options.keys()),
        label_visibility="collapsed",
        key="sel_detection",
    )
    det = options[selected_label]

    # Foto bukti
    cap_id = det.get("capture_id")
    if cap_id:
        img_bytes = _fetch_image(cap_id)
        if img_bytes:
            st.image(img_bytes, use_container_width=True,
                     caption=f"Bukti · Capture #{cap_id}")
        else:
            st.markdown("""
            <div style="height:140px;display:flex;align-items:center;
                        justify-content:center;background:var(--bg-card);
                        border-radius:6px;color:var(--text-dim);
                        font-family:'Fira Code';font-size:11px;
                        border:1px dashed var(--border)">
                Foto bukti tidak tersedia
            </div>""", unsafe_allow_html=True)

    # Info dari AI
    apd_label = _apd_missing_label(det)
    conf      = det.get("confidence_score")
    conf_str  = f"{conf:.0%}" if conf else "—"
    conf_clr  = "var(--green)" if conf and conf >= 0.85 else "var(--cyan)"

    st.markdown(f"""
    <div class="det-card">
      <div class="det-card-header">Hasil Deteksi AI</div>
      <div class="det-grid">
        <div>
          <div class="det-field-label">APD Tidak Terdeteksi</div>
          <div class="det-field-value" style="color:var(--red)">{apd_label}</div>
        </div>
        <div>
          <div class="det-field-label">Confidence AI</div>
          <div class="det-field-value" style="color:{conf_clr};
                      font-family:'Fira Code'">{conf_str}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Form verifikasi
    worker_name = st.text_input(
        "Nama Pekerja",
        placeholder="Masukkan nama pekerja yang terlihat di foto",
        key=f"wname_{det['id']}",
    )
    verified_by = st.text_input(
        "Nama Pengawas",
        placeholder="Nama pengawas K3 yang memverifikasi",
        key=f"vby_{det['id']}",
    )
    notes = st.text_area(
        "Catatan (opsional)",
        placeholder="Tambahkan catatan jika perlu",
        height=60,
        key=f"notes_{det['id']}",
    )

    # Action buttons
    bc1, bc2 = st.columns(2)
    with bc1:
        confirm = st.button(
            "✓  Konfirmasi",
            use_container_width=True,
            type="primary",
            key=f"confirm_{det['id']}",
        )
    with bc2:
        false_alarm = st.button(
            "✗  False Alarm",
            use_container_width=True,
            key=f"fa_{det['id']}",
        )

    if confirm or false_alarm:
        if not verified_by.strip():
            st.error("⚠ Nama pengawas wajib diisi.")
        elif confirm and not worker_name.strip():
            st.error("⚠ Nama pekerja wajib diisi untuk konfirmasi pelanggaran.")
        else:
            status  = "confirmed" if confirm else "false_alarm"
            success = verify_detection(
                detection_id=det["id"],
                status=status,
                worker_name=worker_name.strip(),
                verified_by=verified_by.strip(),
                notes=notes.strip(),
            )
            if success:
                msg = "Pelanggaran dikonfirmasi ✓" if confirm else "Ditandai false alarm ✗"
                st.success(f"{msg} — Data tersimpan.")
                st.cache_data.clear()
                st.rerun()
            else:
                if not det_live:
                    st.info("Mode demo — verifikasi tidak dikirim ke backend.")
                else:
                    st.error("Gagal menyimpan. Periksa koneksi ke backend.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render():
    st.markdown('<p class="section-label">Monitor & Verifikasi</p>',
                unsafe_allow_html=True)

    col_live, col_verify = st.columns([1, 1], gap="large")

    with col_live:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        _render_live_feed()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_verify:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        _render_verification()
        st.markdown('</div>', unsafe_allow_html=True)
