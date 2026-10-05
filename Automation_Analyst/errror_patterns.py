ERROR_PATTERNS = [
    {
        "name": "API Error",
        "keywords": ["500", "502", "503", "failed to fetch", "internal server error"],
        "root_cause": "Terjadi kesalahan pada layanan backend (API).",
        "category": "API Issue",
        "severity": "Critical",
        "solution": "Periksa service backend atau API logs.",
        "human_message": "Sistem gagal memproses permintaan karena terjadi gangguan pada layanan backend."
    },
    {
        "name": "Locator Not Found",
        "keywords": ["waiting for selector", "waiting for locator", "strict mode violation"],
        "root_cause": "Elemen tidak ditemukan atau tidak muncul di halaman.",
        "category": "UI Issue",
        "severity": "High",
        "solution": "Periksa locator/selector atau pastikan elemen muncul.",
        "human_message": "Aksi gagal karena elemen yang dituju tidak ditemukan pada halaman."
    },
    {
        "name": "Click Timeout",
        "keywords": ["timeout", "click", "not visible", "not attached"],
        "root_cause": "Elemen tidak dapat diklik dalam waktu yang ditentukan.",
        "category": "UI Issue",
        "severity": "High",
        "solution": "Pastikan elemen visible dan siap diinteraksi.",
        "human_message": "Gagal melakukan klik karena elemen tidak tersedia atau tidak siap digunakan."
    },
    {
        "name": "Login Failed",
        "keywords": ["401", "unauthorized", "invalid credentials"],
        "root_cause": "Autentikasi gagal karena credential tidak valid.",
        "category": "Auth Issue",
        "severity": "Critical",
        "solution": "Periksa username/password atau token.",
        "human_message": "Login gagal karena data autentikasi tidak valid."
    },
    {
        "name": "Data Not Found",
        "keywords": ["no data", "0 rows", "empty result"],
        "root_cause": "Data yang dibutuhkan tidak tersedia di sistem.",
        "category": "Data Issue",
        "severity": "Medium",
        "solution": "Pastikan data sudah dibuat sebelum pengujian.",
        "human_message": "Proses gagal karena data yang dibutuhkan tidak tersedia."
    }
]


def format_error_to_human(error_text):
    # 🔥 SAFE (hindari None error)
    error_text = str(error_text or "")
    error_text_lower = error_text.lower()

    for pattern in ERROR_PATTERNS:
        if any(keyword in error_text_lower for keyword in pattern["keywords"]):
            return pattern.get("human_message", pattern["root_cause"])

    return "Terjadi kesalahan saat proses pengujian dijalankan."
