import random
import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from config import BACKEND_URL, REFRESH_INTERVAL
from utils.helpers import timestamp_to_shift


def make_demo_data():
    """Generate data dummy. Bentuknya sama persis dengan data dari backend."""
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

    # ViolationSummary 
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

    shift_compliance = {"PAGI": 0.0, "SIANG": 0.0, "MALAM": 0.0}

    # Violations
    rows = []
    for _ in range(15):
        ts   = today - timedelta(hours=random.randint(0, 48), minutes=random.randint(0, 59))
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
            "shift":  timestamp_to_shift(ts),
            "apd":    "+".join(apd_parts),
            "status": random.choice(["verified","verified","unverified","unverified","false_alarm"]),
        })
    rows.sort(key=lambda x: x["time"], reverse=True)
    df_viol = pd.DataFrame(rows)

    return summary, shift_compliance, df_trend, df_viol

@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_data():
    """
    Ambil data dari backend. Kalau gagal, otomatis fallback ke demo data.

    Field disesuaikan dengan skema backend:
      - ViolationSummary  (schemas/violation.py)
      - ViolationResponse (schemas/violation.py)
      - CaptureResponse   (schemas/capture.py)
    Shift dihitung dari created_at karena tidak ada field shift di backend.
    """
    try:
        r_sum  = requests.get(f"{BACKEND_URL}/api/violations/summary", timeout=3)
        r_viol = requests.get(f"{BACKEND_URL}/api/violations/",        timeout=3)
        r_cap  = requests.get(f"{BACKEND_URL}/api/captures/",          timeout=3)

        if not (r_sum.ok and r_viol.ok and r_cap.ok):
            raise ConnectionError("Salah satu endpoint tidak bisa diakses")

        # ── 1. Summary (sesuai ViolationSummary) ──
        raw          = r_sum.json()
        total_v      = raw.get("total_violations", 0)
        verified     = raw.get("verified", 0)
        unverified   = raw.get("unverified", 0)
        false_alarms = raw.get("false_alarms", 0)
        no_helm      = raw.get("missing_helmet_count", 0)
        no_vest      = raw.get("missing_vest_count", 0)
        no_mask      = raw.get("missing_mask_count", 0)

        # Compliance = (foto processed - violations) / foto processed
        caps           = r_cap.json()
        caps_processed = sum(1 for c in caps if c.get("status") == "processed")
        if caps_processed > 0 and total_v <= caps_processed:
            compliance = round((caps_processed - total_v) / caps_processed * 100, 1)
        else:
            compliance = 0.0

        summary = {
            "total_violations":     total_v,
            "verified":             verified,
            "unverified":           unverified,
            "false_alarms":         false_alarms,
            "missing_helmet_count": no_helm,
            "missing_vest_count":   no_vest,
            "missing_mask_count":   no_mask,
            "overall_compliance":   compliance,
        }

        # ── 2. Lookup capture_id → camera_location ──
        cap_lookup = {c["id"]: (c.get("camera_location") or "—") for c in caps}

        # ── 3. Parse violations (sesuai ViolationResponse) ──
        violations = r_viol.json()
        rows = []
        for v in violations:
            raw_ts = v.get("created_at", "")
            try:
                ts       = datetime.fromisoformat(raw_ts.split("+")[0].split("Z")[0])
                time_str = ts.strftime("%d/%m %H:%M")
                shift    = timestamp_to_shift(ts)
            except Exception:
                time_str = raw_ts[:16].replace("T", " ")
                shift    = "—"

            worker = v.get("worker_name_manual") or "—"
            cap_id = v.get("capture_id")
            area   = cap_lookup.get(cap_id, "—") if cap_id else "—"

            apd_parts = []
            if v.get("missing_helmet"): apd_parts.append("Helm")
            if v.get("missing_vest"):   apd_parts.append("Rompi")
            if v.get("missing_mask"):   apd_parts.append("Masker")

            rows.append({
                "time":   time_str,
                "worker": worker,
                "area":   area,
                "shift":  shift,
                "apd":    "+".join(apd_parts) if apd_parts else "—",
                "status": v.get("status", "unverified"),
            })

        df_viol = pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=["time","worker","area","shift","apd","status"])

        # ── 4. Trend per hari dari violations ──
        today = datetime.now()
        trend = []
        for i in range(29, -1, -1):
            d     = today - timedelta(days=i)
            d_key = d.strftime("%Y-%m-%d")
            day_v = sum(1 for v in violations if v.get("created_at","")[:10] == d_key)
            day_c = sum(1 for c in caps       if c.get("captured_at","")[:10] == d_key)
            total     = max(day_c, 1)
            compliant = max(total - day_v, 0)
            trend.append({
                "date":            d.strftime("%d %b"),
                "total":           total,
                "compliant":       compliant,
                "compliance_rate": round(compliant / total * 100, 1),
            })
        df_trend = pd.DataFrame(trend)

        # ── 5. Kepatuhan per area × shift ──
        area_shift: dict = {}
        for v in violations:
            cap_id = v.get("capture_id")
            area   = cap_lookup.get(cap_id, "Unknown") if cap_id else "Unknown"
            raw_ts = v.get("created_at", "")
            try:
                ts    = datetime.fromisoformat(raw_ts.split("+")[0].split("Z")[0])
                shift = timestamp_to_shift(ts)
            except Exception:
                shift = "PAGI"
            key = (area, shift)
            if key not in area_shift:
                area_shift[key] = {"total": 0, "violations": 0}
            area_shift[key]["total"]      += 1
            area_shift[key]["violations"] += 1

        area_rows = [
            {
                "area":       a,
                "shift":      s,
                "rate":       round(max(d["total"]-d["violations"],0)/max(d["total"],1)*100, 1),
                "violations": d["violations"],
            }
            for (a, s), d in area_shift.items()
        ]
        df_area = pd.DataFrame(area_rows) if area_rows else pd.DataFrame(
            columns=["area","shift","rate","violations"])

        shift_compliance = (
            df_area.groupby("shift")["rate"].mean().round(1).to_dict()
            if not df_area.empty else {"PAGI": 0.0, "SIANG": 0.0, "MALAM": 0.0}
        )

        return summary, shift_compliance, df_trend, df_viol, True

    except Exception:
        summary, shift_c, df_trend, df_viol = make_demo_data()
        return summary, shift_c, df_trend, df_viol, False
