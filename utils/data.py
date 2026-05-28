import random
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import BACKEND_URL, REFRESH_INTERVAL, STREAM_URL


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _shift_from_hour(h: int) -> str:
    if 6 <= h < 14:  return "PAGI"
    if 14 <= h < 22:  return "SIANG"
    return "MALAM"


def _parse_ts(raw: str):
    """Parse ISO timestamp string, return datetime or None."""
    try:
        return datetime.fromisoformat(raw.split("+")[0].split("Z")[0])
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND CONNECTIVITY — single fast check, cached
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=15, show_spinner=False)
def _is_backend_alive() -> bool:
    """Satu kali ping cepat ke backend. Hasilnya di-cache 15 detik."""
    try:
        r = requests.get(f"{BACKEND_URL}/docs", timeout=1.5)
        return r.status_code < 500
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# DEMO DATA  — dipakai saat backend offline
# ─────────────────────────────────────────────────────────────────────────────
def make_demo_data():
    random.seed(42)
    today = datetime.now()

    # Trend 30 hari
    trend = []
    for i in range(29, -1, -1):
        d         = today - timedelta(days=i)
        total     = random.randint(80, 160)
        compliant = random.randint(int(total * 0.70), total)
        trend.append({
            "date":            d.strftime("%d %b"),
            "total":           total,
            "compliant":       compliant,
            "compliance_rate": round(compliant / total * 100, 1),
        })
    df_trend = pd.DataFrame(trend)

    # Summary
    total_v      = random.randint(80, 130)
    verified     = random.randint(40, 70)
    unverified   = random.randint(20, 40)
    false_alarms = max(total_v - verified - unverified, 0)
    summary = {
        "total_violations":     total_v,
        "verified":             verified,
        "unverified":           unverified,
        "false_alarms":         false_alarms,
        "missing_helmet_count": random.randint(30, 60),
        "missing_vest_count":   random.randint(20, 45),
        "missing_mask_count":   random.randint(15, 35),
        "overall_compliance":   round(random.uniform(74, 91), 1),
    }

    # Shift compliance
    shift_compliance = {
        "PAGI":  round(random.uniform(78, 95), 1),
        "SIANG": round(random.uniform(72, 90), 1),
        "MALAM": round(random.uniform(65, 85), 1),
    }

    # Violation rows
    rows = []
    for _ in range(30):
        ts   = today - timedelta(hours=random.randint(0, 72), minutes=random.randint(0, 59))
        helm = random.choice([True, False])
        vest = random.choice([True, False])
        mask = random.choice([True, False])
        if not helm and not vest and not mask:
            helm = True
        apd_parts = []
        if helm: apd_parts.append("Helm")
        if vest: apd_parts.append("Rompi")
        if mask: apd_parts.append("Masker")
        rows.append({
            "time":   ts.strftime("%d/%m %H:%M"),
            "worker": f"Pekerja-{random.randint(100, 999)}",
            "shift":  _shift_from_hour(ts.hour),
            "apd":    "+".join(apd_parts),
            "status": random.choice(["verified", "verified", "unverified", "unverified", "false_alarm"]),
        })
    rows.sort(key=lambda x: x["time"], reverse=True)
    df_viol = pd.DataFrame(rows)

    return summary, shift_compliance, df_trend, df_viol


def make_demo_detections():
    """Demo data untuk antrian verifikasi — meniru DetectionResponse dari backend."""
    random.seed(99)
    today = datetime.now()
    items = []
    for i in range(1, 6):
        ts      = today - timedelta(minutes=random.randint(2, 90))
        missing = random.sample(["helmet", "vest", "mask"], k=random.randint(1, 2))
        items.append({
            "id":               i,
            "capture_id":       i,
            "has_helmet":       "helmet" not in missing,
            "has_vest":         "vest"   not in missing,
            "has_mask":         "mask"   not in missing,
            "confidence_score": round(random.uniform(0.68, 0.97), 2),
            "status":           "unverified",
            "detected_at":      ts.isoformat(),
            "_time_str":        ts.strftime("%d/%m %H:%M"),
        })
    return items


# ─────────────────────────────────────────────────────────────────────────────
# FETCH DARI BACKEND
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def fetch_data():
    """
    Ambil summary, violations, captures dari backend.
    Return: (summary, shift_compliance, df_trend, df_viol, is_live)
    """
    # Quick check dulu — kalau backend mati, langsung demo tanpa tunggu timeout
    if not _is_backend_alive():
        summary, shift_c, df_trend, df_viol = make_demo_data()
        return summary, shift_c, df_trend, df_viol, False

    try:
        r_sum  = requests.get(f"{BACKEND_URL}/api/violations/summary", timeout=3)
        r_viol = requests.get(f"{BACKEND_URL}/api/violations/",        timeout=3)
        r_cap  = requests.get(f"{BACKEND_URL}/api/captures/",          timeout=3)

        if not (r_sum.ok and r_viol.ok and r_cap.ok):
            raise ConnectionError()

        # ── Summary ──────────────────────────────────────────────────────
        raw = r_sum.json()
        summary = {
            "total_violations":     raw.get("total_violations", 0),
            "verified":             raw.get("verified", 0),
            "unverified":           raw.get("unverified", 0),
            "false_alarms":         raw.get("false_alarms", 0),
            "missing_helmet_count": raw.get("missing_helmet_count", 0),
            "missing_vest_count":   raw.get("missing_vest_count", 0),
            "missing_mask_count":   raw.get("missing_mask_count", 0),
            "overall_compliance":   raw.get("overall_compliance", 0.0),
        }

        # Jika backend belum return overall_compliance, hitung dari captures
        if summary["overall_compliance"] == 0.0:
            caps           = r_cap.json()
            caps_processed = sum(1 for c in caps if c.get("status") == "processed")
            total_v        = summary["total_violations"]
            if caps_processed > 0:
                summary["overall_compliance"] = round(
                    max(caps_processed - total_v, 0) / caps_processed * 100, 1
                )
        else:
            caps = r_cap.json()

        # ── Violations → DataFrame ───────────────────────────────────────
        violations = r_viol.json()
        rows = []
        for v in violations:
            ts = _parse_ts(v.get("created_at", ""))
            if ts:
                time_str = ts.strftime("%d/%m %H:%M")
                shift    = _shift_from_hour(ts.hour)
            else:
                time_str = v.get("created_at", "")[:16].replace("T", " ")
                shift    = "—"

            worker = v.get("worker_name_manual") or "—"
            apd_parts = []
            if v.get("missing_helmet"): apd_parts.append("Helm")
            if v.get("missing_vest"):   apd_parts.append("Rompi")
            if v.get("missing_mask"):   apd_parts.append("Masker")

            rows.append({
                "id":     v.get("id"),
                "time":   time_str,
                "worker": worker,
                "shift":  shift,
                "apd":    "+".join(apd_parts) if apd_parts else "—",
                "status": v.get("status", "unverified"),
            })

        df_viol = pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=["id", "time", "worker", "shift", "apd", "status"])

        # ── Trend 30 hari ────────────────────────────────────────────────
        today = datetime.now()
        trend = []
        for i in range(29, -1, -1):
            d     = today - timedelta(days=i)
            d_key = d.strftime("%Y-%m-%d")
            day_v = sum(1 for v in violations if v.get("created_at", "")[:10] == d_key)
            day_c = sum(1 for c in caps       if c.get("captured_at", "")[:10] == d_key)
            total     = max(day_c, 1)
            compliant = max(total - day_v, 0)
            trend.append({
                "date":            d.strftime("%d %b"),
                "total":           total,
                "compliant":       compliant,
                "compliance_rate": round(compliant / total * 100, 1),
            })
        df_trend = pd.DataFrame(trend)

        # ── Shift compliance ─────────────────────────────────────────────
        shift_buckets: dict = {"PAGI": {"ok": 0, "all": 0},
                               "SIANG": {"ok": 0, "all": 0},
                               "MALAM": {"ok": 0, "all": 0}}
        for c in caps:
            ts = _parse_ts(c.get("captured_at", ""))
            if ts:
                s = _shift_from_hour(ts.hour)
                shift_buckets[s]["all"] += 1
        for v in violations:
            ts = _parse_ts(v.get("created_at", ""))
            if ts:
                s = _shift_from_hour(ts.hour)
                shift_buckets[s]["ok"] += 1

        shift_compliance = {}
        for s, b in shift_buckets.items():
            if b["all"] > 0:
                shift_compliance[s] = round(max(b["all"] - b["ok"], 0) / b["all"] * 100, 1)
            else:
                shift_compliance[s] = 0.0

        return summary, shift_compliance, df_trend, df_viol, True

    except Exception:
        summary, shift_c, df_trend, df_viol = make_demo_data()
        return summary, shift_c, df_trend, df_viol, False


# ─────────────────────────────────────────────────────────────────────────────
# DETECTIONS (untuk panel verifikasi)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=15, show_spinner=False)
def fetch_detections_unverified():
    """
    Ambil deteksi yang belum diverifikasi.
    GET /api/detections/?status=unverified
    Fallback ke demo jika backend offline.
    """
    if not _is_backend_alive():
        return make_demo_detections(), False

    try:
        r = requests.get(
            f"{BACKEND_URL}/api/detections/",
            params={"status": "unverified"},
            timeout=3,
        )
        if r.ok:
            data = r.json()
            if isinstance(data, list):
                for d in data:
                    ts = _parse_ts(d.get("detected_at", ""))
                    d["_time_str"] = ts.strftime("%d/%m %H:%M") if ts else "—"
                return data, True
        raise ConnectionError()
    except Exception:
        return make_demo_detections(), False


@st.cache_data(ttl=10, show_spinner=False)
def fetch_latest_capture():
    """Ambil capture terbaru dari backend. Return: (capture_dict, is_live)."""
    if not _is_backend_alive():
        return None, False

    try:
        r = requests.get(f"{BACKEND_URL}/api/captures/", timeout=2)
        if r.ok:
            caps = r.json()
            if caps:
                return caps[0], True
        return None, False
    except Exception:
        return None, False


# ─────────────────────────────────────────────────────────────────────────────
# STREAM CHECK
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=15, show_spinner=False)
def check_stream_available() -> bool:
    """Cek apakah MJPEG stream endpoint bisa diakses."""
    if not _is_backend_alive():
        return False
    try:
        r = requests.head(STREAM_URL, timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# VERIFY DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def verify_detection(detection_id: int, status: str,
                     worker_name: str, verified_by: str,
                     notes: str = "") -> bool:
    """
    Kirim verifikasi ke backend.
    PATCH /api/detections/{detection_id}/verify
    """
    try:
        payload = {
            "status":              status,
            "worker_name_manual":  worker_name,
            "verified_by":         verified_by,
            "notes":               notes,
        }
        r = requests.patch(
            f"{BACKEND_URL}/api/detections/{detection_id}/verify",
            json=payload,
            timeout=5,
        )
        return r.ok
    except Exception:
        return False
