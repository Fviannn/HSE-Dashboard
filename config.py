BACKEND_URL      = "http://localhost:8000"
STREAM_URL       = "http://localhost:8000/api/stream"
REFRESH_INTERVAL = 60          # detik auto-refresh data
CAMERA_REFRESH   = 3           # detik fallback polling capture (jika MJPEG stream tidak tersedia)

SHIFT_DISPLAY = {
    "PAGI":  "06:00–14:00",
    "SIANG": "14:00–22:00",
    "MALAM": "22:00–06:00",
}

# Chart styling
CHART_BG  = "rgba(0,0,0,0)"
FONT_MONO = "Fira Code"
FONT_MAIN = "Rajdhani"
GRID_CLR  = "rgba(0,212,255,0.07)"
TEXT_SEC   = "#7A8A99"
