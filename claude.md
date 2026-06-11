Hi Claude! Kita akan melanjutkan pengembangan frontend Streamlit untuk proyek Capstone: **APD Monitoring Dashboard (Studi Kasus PT Indonesia Epson Industry - Universitas Brawijaya 2026)**.

Saya berencana merombak desain antarmukanya (UI/UX) nanti, jadi silakan abaikan estetika warna/gaya CSS versi saat ini. Yang paling krusial untuk dipahami sekarang adalah **Alur Logika, Struktur Kode, Integrasi API Backend, serta Dokumen Kebutuhan Sistem** yang sudah di-overhaul ke **versi v3.1** di bawah ini.

---

### 1. ALUR UTAMA & LOGIKA SISTEM (FLOW)
*   **Alur Deteksi & Verifikasi:**
    1. CCTV menangkap gambar -> AI Model mendeteksi jika pekerja tidak menggunakan APD (Helm, Rompi, atau Masker).
    2. Hasil deteksi terkirim ke database backend (FastAPI) dengan status awal `unverified`.
    3. Pengawas K3 melihat antrean verifikasi di Dashboard Streamlit.
    4. Pengawas melihat foto bukti pelanggaran, mencocokkan wajah pekerja, lalu memasukkan nama pekerja secara manual (kolom *free-text*), menginput nama pengawas, menambahkan catatan, lalu menekan **"✓ Konfirmasi"** atau **"✗ False Alarm"**.
    5. Dashboard menembak API `PATCH` ke backend untuk meng-update status pelanggaran di database menjadi `confirmed` atau `false_alarm`.
*   **Logika Live Feed (3-Tier Fallback):**
    *   **Tier 1 (Utama):** Dashboard meng-embed MJPEG stream dari `GET /api/stream`.
    *   **Tier 2 (Fallback):** Jika stream tidak tersedia tetapi backend menyala, dashboard melakukan polling capture terbaru dari database (`GET /api/captures/`).
    *   **Tier 3 (Offline):** Jika backend mati total, dashboard otomatis berjalan dalam **Demo Mode (Offline)** dengan menampilkan data simulasi agar sistem tidak crash.

---

### 2. KEBUTUHAN SISTEM (Berdasarkan Laporan Lembar Kerja)

#### A. Kebutuhan Pengguna (User Requirements)
1. **Pengawas K3:** Dapat memantau kepatuhan penggunaan APD (helm, rompi, masker) secara otomatis dan real-time.
2. **Pengawas K3:** Dapat menerima notifikasi ketika terjadi pelanggaran APD.
3. **Manager/Supervisor:** Dapat melihat data pelanggaran yang tercatat secara otomatis.
4. **Manager/Supervisor:** Dapat menganalisis laporan pelanggaran untuk evaluasi keselamatan.
5. **Pengawas K3:** Dapat memantau beberapa area secara bersamaan.
6. **Pengawas K3:** Dapat menggunakan sistem dengan mudah tanpa mengganggu alur kerja harian.
7. **Admin Sistem:** Dapat mengelola dan memastikan sistem terintegrasi dengan CCTV dan jaringan yang ada.
8. **Admin Sistem:** Dapat memastikan sistem berjalan stabil secara kontinu.
9. **HR:** Dapat memastikan data pekerja dikelola dengan aman sesuai kebijakan privasi (keamanan data).
10. **Manajemen:** Dapat menggunakan data dari sistem untuk mendukung pengambilan keputusan.

#### B. Kebutuhan Fungsional (Functional Requirements)
1. **Deteksi APD:** Sistem dapat mendeteksi penggunaan APD (helm, rompi, masker) secara otomatis dari video CCTV.
2. **Monitoring Real-Time:** Melakukan pemantauan secara langsung pada area yang diawasi.
3. **Notifikasi Pelanggaran:** Memberikan notifikasi otomatis ketika terdeteksi pelanggaran APD.
4. **Pencatatan Pelanggaran:** Menyimpan data pelanggaran otomatis beserta foto bukti dan timestamp.
5. **Penyimpanan Data:** Menyimpan data pelanggaran ke dalam database secara terstruktur.
6. **Integrasi CCTV:** Terhubung dengan infrastruktur CCTV yang sudah ada (DVR, LAN, dan PC).
7. **Multi-Channel Monitoring:** Sistem mampu memproses beberapa input kamera secara bersamaan.
8. **Pengelolaan Data:** Menampilkan dan mengelola data pelanggaran untuk keperluan monitoring.
9. **Sistem Logging:** Mencatat seluruh aktivitas deteksi dan pelanggaran secara otomatis.
10. **Export Data:** Mengekspor data pelanggaran ke CSV untuk kebutuhan laporan dan evaluasi.

#### C. Kebutuhan Non-Fungsional (Non-Functional Requirements)
*   **Performa:** Sistem mendeteksi secara real-time dengan latensi rendah (< 3 detik).
*   **Reliabilitas:** Sistem berjalan stabil dan kontinu selama operasional pabrik (± 8 jam per shift).
*   **Skalabilitas:** Dapat dikembangkan untuk mendukung penambahan jumlah kamera atau area pengawasan.
*   **Keamanan & Privasi:** Menjamin keamanan data akses pengguna serta mengelola data pekerja sesuai kebijakan privasi (UU PDP).
*   **Kompatibilitas:** Mudah terintegrasi dengan infrastruktur yang ada (CCTV, DVR, LAN, PC).
*   **Usability & Efisiensi:** Antarmuka mudah digunakan oleh pengawas dan efisien (dapat berjalan di spesifikasi hardware terbatas tanpa wajib GPU khusus).
*   **Maintainability & Availability:** Mudah dipelihara dan terus dapat diakses selama waktu operasional tanpa gangguan signifikan.

---

### 3. EVOLUSI LOGIKA KODE: VERSI v2.x KE v3.1 (Under the Hood)
Meskipun desain visual akan kita rombak nanti, struktur logika di balik layar kode saat ini sudah dioptimalkan dengan cara berikut:
1.  **Pemberantasan Bug Sidebar:** Struktur sidebar Streamlit yang sering rusak akibat bentrokan CSS telah ditiadakan. Navigasi saat ini menggunakan tombol tab horizontal di bagian atas halaman.
2.  **Optimasi Page Loading & Transisi:**
    *   Dibuat fungsi cek koneksi backend tunggal `_is_backend_alive()` (timeout 1.5 detik, di-cache selama 15 detik).
    *   Jika backend terdeteksi offline, dashboard langsung me-load demo data tanpa menunggu timeout API di setiap halaman, membuat transisi halaman menjadi instan.
    *   Menghilangkan spinner loading default Streamlit (`show_spinner=False` pada decorator `@st.cache_data`) agar tidak terjadi visual *freeze* atau kedipan saat berpindah tab.
3.  **Database & Schema Alignment:** Semua model data dan field name di frontend (seperti `worker_name_manual`, `verified_by`, `status`) telah diselaraskan 100% dengan skema FastAPI di backend.

---

### 4. STRUKTUR ENDPOINT BACKEND YANG TERINTEGRASI
Dashboard frontend saat ini berkomunikasi dengan FastAPI menggunakan endpoint berikut:
*   `GET /api/violations/summary` : Data ringkasan/KPI kepatuhan.
*   `GET /api/violations/` : Riwayat seluruh pelanggaran.
*   `GET /api/captures/` : Mengambil tangkapan gambar CCTV terakhir.
*   `GET /api/captures/{id}/enhanced` & `/image` : File foto bukti.
*   `GET /api/detections/?status=unverified` : Daftar antrean yang perlu diverifikasi.
*   `PATCH /api/detections/{id}/verify` : Mengirim payload verifikasi pengawas.
*   `GET /api/stream` : MJPEG stream dari kamera pengawas.

Bagaimana tanggapanmu mengenai alur, kebutuhan sistem, dan pembaruan logika kode v3.1 di atas? Kita siap merencanakan perombakan desain antarmuka (UI/UX) baru di atas fondasi logika ini.
