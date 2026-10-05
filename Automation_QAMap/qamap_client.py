"""
Pengirim hasil automation ke QAMap.

QAMap TIDAK menerima berkas PDF. Yang dikirim ke sana adalah datanya — langkah
pengujian, gambar tiap langkah, status, dan tanggal — lalu QAMap sendiri yang
mencetak dokumennya memakai format Report bawaannya. Dengan begitu hasil
automation tampil persis sama dengan hasil eksekusi manual, karena keduanya
melewati pencetak yang sama.

Modul ini sengaja berdiri sendiri dan tidak mengimpor apa pun dari
Automation_Report, supaya bisa dipanggil sebelum laporan PDF dibuat. Urutan itu
WAJIB: generate_pdf_report() memanggil cleanup_screenshots() di ujungnya, yang
MENGHAPUS berkas screenshot dari disk. Kalau pengiriman dilakukan sesudahnya,
seluruh path sudah mati dan buktinya terkirim kosong tanpa satu pun pesan
kesalahan.

Pemakaian paling ringkas, di ujung sebuah test case:

    from Automation_QAMap.qamap_client import kirim_hasil

    hasil = run_test()
    kirim_hasil([hasil], id_project="PRJ-013", tester="dewangga")   # SEBELUM PDF
    generate_pdf_report(all_cases=[hasil])
"""

import base64
import json
import mimetypes
import os
from datetime import datetime
from urllib import error as urlerror
from urllib import request as urlrequest

# Alamat QAMap. Bisa ditimpa lewat variabel lingkungan supaya skrip yang sama
# bisa diarahkan ke server lain tanpa mengubah kode.
QAMAP_BASE_URL = os.environ.get("QAMAP_BASE_URL", "http://localhost:3001")
QAMAP_TOKEN = os.environ.get("QAMAP_TOKEN", "")

# ── Kosakata status ─────────────────────────────────────────────────────────
# Pemilik proses membatasi hasil automation menjadi DUA saja: "kalo automation
# dijalankan pilihannya cuma 2 Passed atau failed, namun ketika sudah masuk ke
# QAMap statusnya bisa dirubah manual."
#
# Jadi apa pun yang bukan lulus menjadi "Failed" — termasuk hasil yang dilewati
# (skipped) dan status asing yang tidak dikenali. Arah itu yang aman: "Failed"
# yang keliru langsung terlihat dan bisa dibetulkan tester lewat layar Test
# Execution, sedangkan "Passed" yang keliru justru menyembunyikan masalah.
#
# Runner TIDAK boleh mengirim "Blocked", "Not Executed", maupun "Untested".
# Menandai skenario sebagai belum dieksekusi padahal runner baru menjalankannya
# akan membuatnya terhitung belum jalan di gerbang kesiapan project.
#
# Konsekuensi yang disengaja: karena automation bisa menghasilkan "Failed",
# aturan "skenario Failed wajib punya defect pendukung" ikut aktif, dan
# project tertahan sampai testernya membuat defect itu — secara manual.
LULUS = {"passed", "pass", "ok", "success", "lulus"}


def petakan_status(nilai):
    """Menyeragamkan status runner menjadi 'Passed' atau 'Failed' — hanya dua itu."""
    return "Passed" if str(nilai or "").strip().lower() in LULUS else "Failed"


class Langkah:
    """
    Pencatat langkah beserta gambarnya, sebagai SATU kesatuan.

    Sebelumnya test case memelihara dua daftar terpisah — test_steps_rendered dan
    screenshots_rendered — lalu memasangkannya berdasarkan urutan. Selama setiap
    langkah menambah tepat satu gambar, itu benar. Tetapi satu langkah yang lupa
    di-screenshot akan menggeser SELURUH pasangan sesudahnya, diam-diam, tanpa
    error: langkah ke-5 memakai gambar langkah ke-6, dan seterusnya. Cacat
    semacam itu baru ketahuan saat dokumennya dibaca orang.

    Kelas ini menutup kemungkinan itu dengan membuat pasangannya sekaligus.
    """

    def __init__(self, testcase_id, testcase_name=None):
        self.testcase_id = testcase_id
        self.testcase_name = testcase_name
        self.pasangan = []

    def catat(self, teks, page=None, base_name=None, fungsi_screenshot=None, **kwargs):
        """
        Mencatat satu langkah. Bila `page` diberikan, gambarnya diambil sekarang
        juga dan langsung dipasangkan dengan teks langkah ini.

        `fungsi_screenshot` dibuat bisa disuntikkan supaya modul ini tidak perlu
        mengimpor Automation_Report — impor itulah yang akan menyeret
        cleanup_screenshots ikut termuat.
        """
        gambar = ""
        if page is not None and fungsi_screenshot is not None:
            gambar = fungsi_screenshot(
                page,
                testcase_id=self.testcase_id,
                base_name=base_name or teks[:40],
                **kwargs,
            )
        self.pasangan.append({"text": teks, "image": gambar})
        return gambar

    def catat_gambar_siap(self, teks, path_gambar):
        """Mencatat langkah yang gambarnya sudah diambil di tempat lain."""
        self.pasangan.append({"text": teks, "image": path_gambar or ""})

    @property
    def test_steps(self):
        """Daftar teks langkah — bentuk yang dipahami pdf_generator."""
        return [p["text"] for p in self.pasangan]

    @property
    def screenshots(self):
        """Daftar path gambar — bentuk yang dipahami pdf_generator."""
        return [p["image"] for p in self.pasangan if p["image"]]


def pasangkan_langkah(test_steps, screenshots):
    """
    Memasangkan dua daftar terpisah menjadi bentuk yang dipahami QAMap.

    Dipakai oleh test case yang masih memelihara test_steps dan screenshots
    sebagai daftar terpisah. Ketidakcocokan jumlah TIDAK didiamkan: pasangannya
    tetap dibuat sebisanya, tetapi peringatannya dicetak supaya ketahuan lebih
    awal daripada saat dokumennya dibaca.
    """
    langkah = [str(s) for s in (test_steps or [])]
    gambar = [str(g) for g in (screenshots or []) if g]

    if len(langkah) != len(gambar):
        print(
            "[QAMap] PERINGATAN: jumlah langkah (%d) dan gambar (%d) tidak sama. "
            "Pasangan langkah-gambar kemungkinan bergeser — periksa apakah ada "
            "langkah yang belum di-screenshot." % (len(langkah), len(gambar))
        )

    hasil = []
    for i, teks in enumerate(langkah):
        hasil.append({"text": teks, "image": gambar[i] if i < len(gambar) else ""})
    # Gambar yang tersisa tanpa langkah tetap disertakan, supaya bukti tidak hilang.
    for sisa in gambar[len(langkah):]:
        hasil.append({"text": "(langkah tidak tercatat)", "image": sisa})
    return hasil


# Akar repo automation, dihitung dari letak modul ini: <akar>/Automation_QAMap/.
# Dipakai untuk menemukan berkas screenshot yang path-nya relatif.
AKAR_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cari_gambar(path):
    """
    Mencari berkas gambar di beberapa tempat yang masuk akal.

    Path screenshot yang datang dari runner umumnya RELATIF — baik dari
    save_screenshot() di jalur Python maupun dari attachment Playwright. Relatif
    terhadap apa, bergantung dari mana perintahnya dijalankan: jembatan Playwright
    misalnya dijalankan dari subfolder, sementara screenshot-nya ditulis di akar
    repo. Kalau hanya mengandalkan folder kerja, berkasnya "tidak ditemukan" dan
    buktinya terkirim kosong tanpa ada yang terlihat salah.
    """
    if os.path.isabs(path):
        return path if os.path.exists(path) else None
    kandidat = [
        path,                                   # relatif terhadap folder kerja
        os.path.join(AKAR_REPO, path),          # relatif terhadap akar repo
        os.path.join(os.getcwd(), os.pardir, path),  # satu tingkat di atas folder kerja
    ]
    for k in kandidat:
        if os.path.exists(k):
            return k
    return None


def _gambar_base64(path):
    """
    Membaca berkas gambar menjadi data URI.

    QAMap menyimpan gambar bukti sebagai base64, sama persis seperti eksekusi
    manual — itu keputusan pemilik proses supaya tidak ada dua mekanisme
    penyimpanan untuk satu jenis kejadian.
    """
    if not path:
        return ""
    if str(path).startswith("data:"):
        return path  # sudah berupa data URI
    berkas = _cari_gambar(str(path))
    if not berkas:
        print("[QAMap] Gambar tidak ditemukan, dilewati: %s "
              "(dicari relatif terhadap folder kerja dan akar repo)" % path)
        return ""
    tipe = mimetypes.guess_type(berkas)[0] or "image/png"
    with open(berkas, "rb") as f:
        return "data:%s;base64,%s" % (tipe, base64.b64encode(f.read()).decode("ascii"))


def susun_payload(all_cases, id_project, tester, run_id=None, tanggal=None, jenis_test=None,
                  kode_project=None):
    """
    Menyusun badan permintaan untuk QAMap dari hasil runner.

    Menerima bentuk yang sudah dipakai runner apa adanya: `test_steps` dan
    `screenshots` sebagai daftar terpisah, ATAU `langkah` berupa daftar pasangan
    {text, image} bila test case sudah memakai kelas Langkah.
    """
    tanggal = tanggal or datetime.now().strftime("%Y-%m-%d")
    kasus = []

    for c in all_cases or []:
        if c.get("langkah"):
            pasangan = c["langkah"]
        else:
            pasangan = pasangkan_langkah(c.get("test_steps"), c.get("screenshots"))

        kasus.append({
            "testCaseId": c.get("testcase_id") or c.get("testCaseId") or "",
            "title": c.get("testcase_name") or "",
            # Nama penguji diambil dari test data skenarionya sendiri, bukan dari
            # akun yang menjalankan runner: satu QA sering menjalankan run milik
            # rekannya, sedangkan dokumen resmi harus menyebut penguji yang
            # bertanggung jawab atas skenario itu. QAMap memakai nilai ini dan baru
            # jatuh ke testerUsername bila kosong.
            "testerName": c.get("tester_name") or "",
            # Data uji per skenario. Di repo ini bentuknya dict {"No PKS": "..."},
            # sama seperti yang dicetak pdf_generator sebagai blok "Data:". QAMap
            # menerima dict maupun teks biasa dan merapikannya sendiri.
            "testData": c.get("testdata") or c.get("test_data") or "",
            "status": petakan_status(c.get("status")),
            "actualResult": c.get("actual_result") or "",
            "expectedResult": c.get("expected_result") or "",
            "jenisTest": c.get("jenis_test") or jenis_test or "SIT",
            "steps": [
                {"text": p.get("text", ""), "image": _gambar_base64(p.get("image"))}
                for p in pasangan
            ],
        })

    return {
        "projectId": id_project,
        # Kode Project dibandingkan QAMap dengan kolom code milik project
        # tujuan. Kalau tidak cocok, kiriman ditolak 409 dan tidak ada satu
        # baris pun yang ditulis - itulah gerbang "jangan salah kamar".
        "projectCode": str(kode_project or "").strip(),
        "runId": run_id or "",
        "testerUsername": tester,
        "tanggal": tanggal,
        "cases": kasus,
    }


def kirim_hasil(all_cases, id_project, tester, run_id=None, tanggal=None,
                base_url=None, token=None, jenis_test=None, timeout=180,
                kode_project=None):
    """
    Mengirim hasil automation ke QAMap.

    HARUS dipanggil SEBELUM generate_pdf_report(), karena pembuatan laporan
    menghapus berkas screenshot dari disk di ujungnya.

    Mengembalikan (berhasil, keterangan) supaya pemanggil bisa memutuskan sendiri
    apakah kegagalan pengiriman perlu menghentikan proses. Sengaja tidak
    melempar exception: gagal mengirim ke QAMap tidak boleh membatalkan laporan
    PDF yang sudah berhasil dibuat.
    """
    alamat = (base_url or QAMAP_BASE_URL).rstrip("/") + "/api/automation/hasil"
    kunci = token or QAMAP_TOKEN
    if not kunci:
        return False, ("Token QAMap belum diisi. Set variabel lingkungan QAMAP_TOKEN "
                       "atau kirimkan lewat argumen token=.")
    if not str(kode_project or "").strip():
        # Ditolak di sini, bukan dibiarkan menjadi 400 dari server: pesannya
        # lebih jelas dan tidak ada permintaan besar berisi gambar yang
        # dikirim sia-sia lewat jaringan.
        return False, ("Kode Project belum diisi. QAMap mewajibkannya untuk memastikan "
                       "kiriman tidak masuk ke project yang salah.")

    payload = susun_payload(all_cases, id_project, tester, run_id, tanggal, jenis_test,
                            kode_project)
    jumlah_gambar = sum(1 for k in payload["cases"] for s in k["steps"] if s["image"])
    print("[QAMap] Mengirim %d test case, %d langkah, %d gambar ke %s"
          % (len(payload["cases"]),
             sum(len(k["steps"]) for k in payload["cases"]),
             jumlah_gambar, alamat))
    print("[QAMap] Sasaran: project %s (Kode Project %s), siklus %s"
          % (payload["projectId"], payload["projectCode"] or "-", payload["runId"]))

    if jumlah_gambar == 0:
        print("[QAMap] PERINGATAN: tidak ada satu pun gambar yang terbaca. "
              "Pastikan kirim_hasil() dipanggil SEBELUM generate_pdf_report(), "
              "karena laporan PDF menghapus berkas screenshot di ujungnya.")

    data = json.dumps(payload).encode("utf-8")
    ukuran_mb = len(data) / (1024 * 1024)
    print("[QAMap] Ukuran kiriman: %.1f MB" % ukuran_mb)
    if ukuran_mb > 100:
        # Peringatan dini. Penolakan karena badan permintaan terlalu besar datang
        # sebagai HTTP 413 berisi halaman HTML, yang tidak menyebut sebabnya sama
        # sekali - jadi lebih baik disebut di sini sebelum dikirim.
        print("[QAMap] PERINGATAN: kiriman sangat besar. Bila ditolak HTTP 413, "
              "kurangi jumlah/ukuran screenshot atau naikkan batas badan permintaan "
              "di server QAMap.")

    permintaan = urlrequest.Request(alamat, data=data, method="POST")
    permintaan.add_header("Content-Type", "application/json")
    permintaan.add_header("Authorization", "Bearer " + kunci)

    try:
        with urlrequest.urlopen(permintaan, timeout=timeout) as tanggapan:
            isi = tanggapan.read().decode("utf-8", "replace")
            print("[QAMap] Terkirim. HTTP %s :: %s" % (tanggapan.status, isi[:200]))
            return True, isi
    except urlerror.HTTPError as e:
        isi = e.read().decode("utf-8", "replace")
        print("[QAMap] GAGAL. HTTP %s :: %s" % (e.code, isi[:300]))
        return False, isi
    except Exception as e:  # jaringan mati, server belum menyala, dan sejenisnya
        print("[QAMap] GAGAL menghubungi QAMap: %s" % e)
        return False, str(e)


# ═══════════════════════════════════════════════════════════════════════════
# Pemantauan langsung: progres selagi runner masih bekerja
# ═══════════════════════════════════════════════════════════════════════════
#
# Sebelum ini runner hanya melapor SEKALI di ujung, lewat kirim_hasil(). Selama
# ia bekerja, QAMap tidak menerima kabar apa pun — layar Test Execution sudah
# punya panel progresnya, tetapi tidak pernah ada yang mengisinya.
#
# Pemilik proses meminta dua hal sekaligus: jalannya automation bisa dipantau
# langsung DAN jejaknya tetap tersimpan untuk dibuka lagi. Karena itu progresnya
# ditulis ke server, bukan sekadar dicetak ke layar terminal.
#
# Batas yang perlu diketahui sejak awal: berkas test menyusun daftar langkahnya
# SAMBIL berjalan, sehingga main_runner baru mengetahui langkah sebuah skenario
# setelah skenario itu selesai. Yang benar-benar dilaporkan detik itu juga adalah
# pergantian SKENARIO; rincian langkahnya menyusul begitu skenario itu tuntas.
# Jadi selama satu run, QAMap menampilkan skenario yang sedang dikerjakan, lalu
# langkah-langkahnya bermunculan lengkap dengan vonisnya, skenario demi skenario.
#
# Seluruh fungsi di bawah SENGAJA tidak pernah melempar exception dan tidak
# pernah menghentikan run. Pemantauan adalah kenyamanan, bukan tujuan; pengujian
# yang batal hanya karena server QAMap sedang mati adalah kerugian yang jauh
# lebih besar daripada progres yang tidak tampil.


def _kirim_json(jalur, payload, base_url=None, token=None, timeout=30):
    """Mengirim satu permintaan JSON ke QAMap. Mengembalikan (berhasil, isi)."""
    alamat = (base_url or QAMAP_BASE_URL).rstrip("/") + jalur
    kunci = token or QAMAP_TOKEN
    if not kunci:
        return False, "Token QAMap belum diisi."

    data = json.dumps(payload).encode("utf-8")
    permintaan = urlrequest.Request(alamat, data=data, method="POST")
    permintaan.add_header("Content-Type", "application/json")
    permintaan.add_header("Authorization", "Bearer " + kunci)
    try:
        with urlrequest.urlopen(permintaan, timeout=timeout) as tanggapan:
            return True, tanggapan.read().decode("utf-8", "replace")
    except urlerror.HTTPError as e:
        return False, "HTTP %s :: %s" % (e.code, e.read().decode("utf-8", "replace")[:300])
    except Exception as e:
        return False, str(e)


class SesiProgres:
    """
    Pelapor progres satu kali jalan automation.

    Dipakai sebagai penjaga konteks supaya sesinya PASTI ditutup, termasuk ketika
    run berhenti karena kesalahan:

        with SesiProgres.mulai(daftar, id_project, kode, run_id, tester) as sesi:
            for kasus in daftar:
                sesi.kasus_mulai(kasus_id, nama)
                ...
                sesi.kasus_selesai(kasus_id, langkah, lulus)

    Sesi yang tidak pernah ditutup akan selamanya tampil "sedang berjalan" di
    QAMap, jadi penutupannya tidak boleh bergantung pada jalannya mulus.
    """

    def __init__(self, sesi_id, base_url=None, token=None):
        self.sesi_id = sesi_id
        self.base_url = base_url
        self.token = token
        self.aktif = bool(sesi_id)
        self._gagal_beruntun = 0

    # -- Pembukaan ----------------------------------------------------------
    @classmethod
    def mulai(cls, kasus, id_project, kode_project, run_id, tester,
              base_url=None, token=None):
        """
        Mendaftarkan sesi ke QAMap. Selalu mengembalikan SesiProgres — yang tidak
        aktif bila pendaftarannya gagal, sehingga pemanggilnya tidak perlu
        memeriksa None di setiap tempat.

        `kasus` cukup berisi id dan judulnya; langkahnya boleh belum diketahui.
        """
        if not id_project or not run_id:
            print("[QAMap] Progres dilewati: project_id atau run_id belum diisi.")
            return cls(None, base_url, token)
        if not str(kode_project or "").strip():
            print("[QAMap] Progres dilewati: Kode Project belum diisi.")
            return cls(None, base_url, token)

        # Tanpa daftar kasus, isinya diambil dari siklus tujuan di QAMap. Itu satu-
        # satunya daftar yang dijamin lolos pemeriksaan keanggotaan siklus.
        if not kasus:
            kasus = skenario_siklus(run_id, base_url, token)
        if not kasus:
            print("[QAMap] Progres dilewati: siklus %s tidak punya skenario terdaftar."
                  % run_id)
            return cls(None, base_url, token)

        payload = {
            "projectId": id_project,
            "projectCode": str(kode_project).strip(),
            "runId": run_id,
            "testerUsername": tester or "automation",
            "cases": [
                {"testCaseId": str(k.get("testCaseId") or k.get("testcase_id") or ""),
                 "title": k.get("title") or k.get("testcase_name") or "",
                 "steps": k.get("steps") or []}
                for k in (kasus or [])
            ],
        }
        berhasil, isi = _kirim_json("/api/automation/progres/mulai", payload, base_url, token)
        if not berhasil:
            print("[QAMap] Progres tidak bisa dimulai (%s). Run tetap berjalan." % isi[:200])
            return cls(None, base_url, token)

        try:
            sesi_id = json.loads(isi).get("sesiId")
        except Exception:
            sesi_id = None
        if not sesi_id:
            print("[QAMap] Progres tidak bisa dimulai: server tidak mengembalikan sesiId.")
            return cls(None, base_url, token)

        print("[QAMap] Progres live aktif. Sesi %s pada siklus %s." % (sesi_id, run_id))
        return cls(sesi_id, base_url, token)

    # -- Pelaporan ----------------------------------------------------------
    def _lapor(self, test_case_id, step_index, status, teks=None, pesan=None):
        if not self.aktif:
            return False
        muatan = {
            "sesiId": self.sesi_id,
            "testCaseId": str(test_case_id),
            "stepIndex": int(step_index),
            "status": status,
            "stepText": teks,
            "message": pesan,
        }
        berhasil, isi = _kirim_json("/api/automation/progres/langkah", muatan,
                                    self.base_url, self.token)

        # Sekali coba ulang untuk kegagalan tingkat JARINGAN saja.
        #
        # Pelaporan langkah biasanya selesai dalam belasan milidetik, tetapi mesin
        # yang sedang sibuk bisa membuat satu permintaan menyentuh batas waktu —
        # dan tanpa percobaan kedua, langkah itu hilang dari pemantauan langsung
        # sampai run selesai, walau langkah berikutnya berhasil seperti biasa.
        #
        # Hanya untuk kegagalan jaringan: balasan HTTP 4xx berarti kiriman memang
        # DITOLAK (sesi tidak dikenal, misalnya), dan mengulanginya tidak akan
        # mengubah jawabannya. Aman diulang karena sisi QAMap memperbarui baris
        # yang sudah ada berdasarkan (sesi, skenario, nomor langkah), bukan
        # menambah baris baru.
        if not berhasil and not str(isi).startswith("HTTP "):
            berhasil, isi = _kirim_json("/api/automation/progres/langkah", muatan,
                                        self.base_url, self.token, timeout=15)

        if berhasil:
            self._gagal_beruntun = 0
            return True

        # Satu kegagalan bisa saja kedipan jaringan. Tetapi bila berturut-turut,
        # servernya memang sedang tidak bisa dihubungi — dan mencoba terus untuk
        # setiap langkah hanya memperlambat run tanpa ada gunanya.
        self._gagal_beruntun += 1
        if self._gagal_beruntun == 1:
            print("[QAMap] Gagal melaporkan progres: %s" % isi[:200])
        if self._gagal_beruntun >= 5:
            print("[QAMap] Pelaporan progres dihentikan setelah 5 kegagalan beruntun. "
                  "Run tetap berjalan dan hasil akhirnya tetap dikirim.")
            self.aktif = False
        return False

    def kasus_mulai(self, test_case_id, nama=None):
        """Menandai satu skenario sedang dikerjakan, sebelum langkahnya diketahui."""
        self._lapor(test_case_id, 1, "running",
                    teks=("Menjalankan %s" % nama) if nama else None)

    def kasus_selesai(self, test_case_id, langkah, lulus, pesan=None):
        """
        Menuliskan seluruh langkah skenario beserta vonisnya, sesudah skenario itu
        tuntas.

        Langkah yang TERCATAT adalah langkah yang sudah terlewati dengan selamat —
        berkas test mencatat langkahnya sesudah aksinya berhasil, sehingga langkah
        yang gagal tidak pernah sampai tercatat: eksekusinya sudah berhenti oleh
        exception sebelum sempat dicatat. Karena itu seluruh langkah yang ada
        ditandai lulus, apa pun vonis skenarionya.

        Kegagalan skenario ditulis sebagai SATU baris tambahan di ujung, bukan
        dengan membalik vonis langkah terakhir. Membaliknya akan menuduh langkah
        yang justru berhasil, dan menyesatkan pembaca yang sedang mencari titik
        berhentinya — yang sebenarnya ada SESUDAH langkah terakhir yang tercatat.
        """
        daftar = [str(t) for t in (langkah or [])]
        for n, teks in enumerate(daftar, start=1):
            self._lapor(test_case_id, n, "passed", teks=teks)

        if lulus:
            if not daftar:
                self._lapor(test_case_id, 1, "passed", teks="Menjalankan skenario")
            return

        self._lapor(test_case_id, len(daftar) + 1, "failed",
                    teks="Eksekusi berhenti di sini",
                    pesan=pesan or "Skenario gagal tanpa keterangan tambahan.")

    # -- Penutupan ----------------------------------------------------------
    def tutup(self, status="selesai", catatan=None):
        if not self.aktif:
            return
        berhasil, isi = _kirim_json("/api/automation/progres/selesai", {
            "sesiId": self.sesi_id, "status": status, "catatan": catatan,
        }, self.base_url, self.token)
        if not berhasil:
            print("[QAMap] Gagal menutup sesi progres: %s" % isi[:200])
        self.aktif = False

    def __enter__(self):
        return self

    def __exit__(self, jenis, nilai, jejak):
        self.tutup("gagal" if jenis else "selesai",
                   catatan=str(nilai)[:500] if nilai else None)
        return False   # kesalahannya tetap diteruskan; sesi hanya ikut ditutup


def _ambil_json(jalur, base_url=None, token=None, timeout=30):
    """Membaca satu sumber JSON dari QAMap. Mengembalikan (berhasil, data)."""
    alamat = (base_url or QAMAP_BASE_URL).rstrip("/") + jalur
    kunci = token or QAMAP_TOKEN
    if not kunci:
        return False, "Token QAMap belum diisi."
    permintaan = urlrequest.Request(alamat, method="GET")
    permintaan.add_header("Authorization", "Bearer " + kunci)
    try:
        with urlrequest.urlopen(permintaan, timeout=timeout) as tanggapan:
            return True, json.loads(tanggapan.read().decode("utf-8", "replace"))
    except urlerror.HTTPError as e:
        return False, "HTTP %s :: %s" % (e.code, e.read().decode("utf-8", "replace")[:300])
    except Exception as e:
        return False, str(e)


def daftar_project(base_url=None, token=None):
    """
    Daftar project di QAMap yang boleh dituju runner.

    Yang berstatus Closed tidak ikut - QAMap sengaja tidak menyertakannya, supaya
    project yang sudah ditutup tidak mungkin dipilih sama sekali.

    Tiap entri membawa Kode Project dan penanda apakah projectnya sedang
    ditinjau:

        {"id": "PRJ-110", "name": "Automation ACS All COB", "code": "000000",
         "status": "On Track", "sedangDitinjau": False}

    Mengembalikan list kosong bila gagal - pemanggilnya yang memutuskan apa yang
    dilakukan, sama seperti fungsi pembaca lain di berkas ini.
    """
    berhasil, data = _ambil_json("/api/automation/projects", base_url, token)
    if not berhasil or not isinstance(data, list):
        return []
    return data


def daftar_siklus(id_project, base_url=None, token=None):
    """
    Daftar siklus (test run) milik satu project di QAMap.

    Dipakai pemilih siklus di main_runner. Tiap entri sudah membawa jenis
    testnya, jumlah skenario, dan statusnya, jadi runner tidak perlu menebak
    apa pun dari nama siklusnya:

        {"id": "PRJ-111-02", "name": "Siklus UAT COB Askred",
         "jenisTest": "UAT", "status": "In Progress", "jumlahSkenario": 12}

    Kenapa jumlahSkenario ikut dibawa: siklus yang isinya nol skenario PASTI
    menolak kiriman apa pun, karena QAMap menuntut tiap TC-ID sudah terdaftar di
    siklus tujuan. Lebih baik terlihat sebelum run daripada sesudah seluruh
    skenario dijalankan.

    Mengembalikan list kosong bila gagal — pemanggilnya yang memutuskan apa yang
    dilakukan, sama seperti fungsi pembaca lain di berkas ini.
    """
    berhasil, data = _ambil_json("/api/automation/projects/%s/runs" % id_project,
                                 base_url, token)
    if not berhasil or not isinstance(data, list):
        return []
    return data


def detail_project_qamap(id_project, base_url=None, token=None):
    """
    Keterangan satu project dari QAMap, atau None bila tidak ketemu.

    Yang dipakai pemilih siklus adalah `sedangDitinjau`: project yang sedang di
    meja QMP atau QA Lead sebaiknya diberi peringatan sebelum ditimpa bukti baru,
    karena dokumen yang sudah ditandatangani bisa tidak lagi cocok dengan isinya.
    Penandanya dihitung QAMap sendiri, bukan disimpulkan ulang di sini.
    """
    for p in daftar_project(base_url, token):
        if str(p.get("id") or "") == str(id_project):
            return p
    return None


def skenario_siklus(run_id, base_url=None, token=None):
    """
    Daftar skenario yang terdaftar pada sebuah siklus di QAMap.

    Dipakai sebagai isi awal sesi progres. Mengambilnya dari QAMap, bukan
    menyusunnya sendiri di runner, karena dua alasan:

    1. TC-ID yang didaftarkan HARUS benar-benar ada di siklus tujuan — QAMap
       menolak seluruh pendaftaran bila ada satu saja yang asing. Daftar milik
       siklus itu sendiri dijamin lolos.
    2. Runner baru mengetahui TC-ID sebuah skenario setelah testdata-nya dibaca,
       yaitu di dalam perulangan eksekusi. Menunggu sampai saat itu berarti
       sesinya baru terdaftar ketika skenario pertama sudah berjalan.

    Skenario siklus yang ternyata tidak dijalankan runner akan tertutup sebagai
    'skipped' — dan itu memang keterangan yang jujur.
    """
    berhasil, data = _ambil_json("/api/automation/runs/%s/test-cases" % run_id,
                                 base_url, token)
    if not berhasil:
        return []
    return [{"testCaseId": t.get("id"), "title": t.get("title") or ""}
            for t in (data or {}).get("testCases", []) if t.get("id")]


# ═══════════════════════════════════════════════════════════════════════════
# Pelaporan per LANGKAH, saat langkahnya baru saja terjadi
# ═══════════════════════════════════════════════════════════════════════════
#
# SesiProgres di atas melaporkan pergantian skenario detik itu juga, tetapi
# rincian langkahnya baru menyusul ketika skenario itu tuntas. Sebabnya berkas
# test menyusun daftar langkahnya sendiri di dalam sebuah list biasa, dan
# main_runner tidak bisa melihat isi list itu selagi fungsinya masih berjalan.
#
# Yang diubah di sini bukan cara berkas test bekerja, melainkan WADAH-nya. Bila
# `test_steps_rendered` bukan list biasa melainkan list yang melapor setiap kali
# di-append, maka setiap langkah terkabar ke QAMap pada saat langkah itu benar-
# benar selesai dikerjakan — tanpa satu pun pemanggilan tambahan di badan test.
#
# Perubahan yang dituntut pada tiap berkas test karena itu hanya DUA baris:
#
#     from Automation_QAMap.qamap_client import record_step   # 1. impor
#     ...
#     test_steps_rendered = record_step()                     # 2. ganti []
#
# Sisa berkasnya tidak disentuh sama sekali: `.append(...)` yang sudah ada tetap
# berjalan seperti biasa, dan bila QAMap tidak dipakai — sesi tidak aktif, atau
# test dijalankan sendirian di luar main_runner — wadah ini berperilaku persis
# seperti list kosong biasa.
#
# Status yang dilaporkan adalah 'passed', bukan 'running'. Berkas test mencatat
# langkahnya SESUDAH aksinya berhasil; langkah yang gagal tidak pernah sampai
# di-append karena eksekusinya sudah berhenti oleh exception. Jadi setiap langkah
# yang muncul di sini memang langkah yang sudah terlewati dengan selamat.

_PELAPOR_LANGKAH = {"sesi": None, "test_case_id": None}


def start_step_logging(sesi, test_case_id):
    """Menetapkan ke mana langkah berikutnya dilaporkan. Dipanggil main_runner."""
    _PELAPOR_LANGKAH["sesi"] = sesi
    _PELAPOR_LANGKAH["test_case_id"] = test_case_id


def stop_step_logging():
    """Melepas sasaran laporan, supaya langkah tidak mendarat di skenario keliru."""
    _PELAPOR_LANGKAH["sesi"] = None
    _PELAPOR_LANGKAH["test_case_id"] = None


class DaftarLangkahHidup(list):
    """
    List langkah yang mengabarkan tiap penambahannya ke QAMap.

    Sengaja dibuat sebagai turunan `list`, bukan kelas baru: seluruh berkas test
    dan pembuat laporan PDF sudah memperlakukannya sebagai list — di-slice,
    di-len, di-iterasi, digabung. Turunan list tetap sah di semua tempat itu,
    sehingga tidak ada satu pun kode lain yang perlu ikut diubah.
    """

    def append(self, nilai):
        super(DaftarLangkahHidup, self).append(nilai)
        sesi = _PELAPOR_LANGKAH.get("sesi")
        tcid = _PELAPOR_LANGKAH.get("test_case_id")
        if sesi is None or not tcid:
            return
        try:
            sesi._lapor(tcid, len(self), "passed", teks=str(nilai))
        except Exception:
            # Kegagalan melapor TIDAK boleh merembet ke pengujiannya. Diam-diam
            # dilewati di sini, karena _lapor sendiri sudah mencetak sebabnya.
            pass


def record_step(awal=None):
    """
    Wadah langkah yang melapor langsung ke QAMap.

    Dipakai menggantikan `[]` di berkas test:

        test_steps_rendered = record_step()
    """
    return DaftarLangkahHidup(awal or [])
