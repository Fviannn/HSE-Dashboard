from datetime import datetime


def timestamp_to_shift(dt: datetime) -> str:
    """Hitung nama shift dari jam di timestamp. Dipakai karena backend tidak punya field shift."""
    h = dt.hour
    if 6 <= h < 14:  return "PAGI"
    if 14 <= h < 22: return "SIANG"
    return "MALAM"


def color_class(rate: float) -> str:
    """Return CSS class warna berdasarkan compliance rate."""
    if rate >= 87: return "good"
    if rate >= 75: return "warn"
    return "crit"


def badge_html(status: str) -> str:
    """Return HTML badge untuk kolom status di tabel pelanggaran."""
    m = {
        "verified":    ("badge-verified",   "VERIFIED"),
        "unverified":  ("badge-unverified", "UNVERIFIED"),
        "false_alarm": ("badge-false",      "FALSE ALARM"),
    }
    cls, label = m.get(status, ("badge-unverified", status.upper()))
    return f'<span class="badge-v {cls}">{label}</span>'


def apd_tags(apd_str: str) -> str:
    """Return HTML tags untuk daftar APD yang dilanggar di tabel."""
    if not apd_str or apd_str == "—":
        return '<span style="color:var(--text-dim)">—</span>'
    return " ".join(
        f'<span class="apd-tag">{p.strip()}</span>'
        for p in apd_str.split("+")
    )