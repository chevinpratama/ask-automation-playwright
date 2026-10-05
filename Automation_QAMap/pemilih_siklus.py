"""
Pemilih siklus tujuan QAMap untuk runner automation.

Dipisahkan dari main_runner supaya bisa diimpor dan diuji sendiri: main_runner
menjalankan menunya di tingkat modul, sehingga mengimpornya berarti menjalankan
seluruh runner. Menu ini juga tidak dititipkan di qamap_client, karena berkas itu
sama sekali tidak bergantung pada lapisan menu - dan sebaiknya tetap begitu.
"""

from Automation_QAMap.qamap_client import (daftar_project, daftar_siklus,
                                            detail_project_qamap)
from Automation_Utils.menu_handler import input_with_timeout


def _seragam(nilai):
    """Kode Project disamakan bentuknya: spasi di ujung dibuang, huruf disamakan.

    Sama dengan `kodeSeragam` di QAMap (routes/automation.cjs dan routes/projects.cjs),
    supaya keputusan cocok/tidak di sini tidak pernah berbeda dari keputusan server.
    """
    return str(nilai or "").strip().upper()


def pilih_project_qamap(base_url, token, kode_project=None):
    """
    Menanyakan project tujuan di QAMap, lalu mengembalikan project_id-nya.

    Dipanggil hanya ketika project_id belum ditentukan - env QAMAP_PROJECT_ID dan
    config.json tetap menang.

    Kenapa memilih dari daftar lebih aman daripada menyimpannya di config: nilai
    yang tersimpan diwarisi diam-diam. Tester yang menyalin config rekannya lalu
    menjalankan test case-nya sendiri akan mengirim hasilnya ke project orang lain
    tanpa pernah memilih apa pun secara sadar.

    Pilihan yang PASTI ditolak QAMap tidak dibiarkan lanjut. Kode Project pada
    data runner dibandingkan dengan kode tiap project; yang tidak cocok akan
    ditolak 409 di ujung, sesudah seluruh skenario dijalankan. Menolaknya di sini
    mengubah kerugiannya dari sepuluh menit terbuang menjadi satu baris pesan.
    Pilihan yang cocok ditandai, jadi tester tidak perlu paham mekanismenya untuk
    tahu mana yang benar.

    Mengembalikan "" bila dilewati atau daftarnya tidak bisa diambil.
    """
    daftar = daftar_project(base_url, token)
    if not daftar:
        print("[QAMap] Daftar project tidak bisa diambil. Periksa alamat dan token "
              "QAMap di config.json, atau set QAMAP_PROJECT_ID bila sudah tahu "
              "project tujuannya.")
        return ""

    kode = _seragam(kode_project)
    cocok = [p for p in daftar if kode and _seragam(p.get("code")) == kode]

    print("")
    print("===== PROJECT TUJUAN QAMap =====")
    if kode:
        print("Kode Project pada data runner: %s" % str(kode_project).strip())
    else:
        print("Kode Project pada data runner belum diisi - isi dulu project_code di "
              "helper_laporan.py.")
    print("")

    for i, p in enumerate(daftar, 1):
        tanda = ""
        if kode and _seragam(p.get("code")) == kode:
            tanda = "  <-- cocok dengan data uji"
        elif kode:
            tanda = "  (kodenya beda, akan ditolak)"
        if p.get("sedangDitinjau"):
            tanda += "  [sedang ditinjau]"
        print("%2d. %-10s %-32s [%-12s] %s%s"
              % (i, p.get("id") or "-", (p.get("name") or "-")[:32],
                 p.get("code") or "-", p.get("status") or "-", tanda))
    print(" 0. Lewati (jalankan tanpa mengirim ke QAMap)")

    if kode and not cocok:
        # Tidak ada satu pun project yang kodenya cocok. Apa pun yang dipilih akan
        # ditolak, jadi menawarkan pilihan hanya menyesatkan.
        print("")
        print("[QAMap] Tidak ada project ber-Kode Project %s di QAMap. Perbaiki dulu "
              "project_code di helper_laporan.py, atau isi Kode Project projectnya "
              "di QAMap." % str(kode_project).strip())
        return ""

    while True:
        jawab = input_with_timeout("Pilih project: ", 60)
        if jawab in (None, "__EXIT__"):
            print("[QAMap] Tidak ada pilihan - pengiriman dilewati.")
            return ""
        jawab = str(jawab).strip()
        if jawab == "0":
            print("[QAMap] Pengiriman dilewati atas pilihan sendiri.")
            return ""
        if jawab.isdigit() and 1 <= int(jawab) <= len(daftar):
            terpilih = daftar[int(jawab) - 1]
            if kode and _seragam(terpilih.get("code")) != kode:
                print("[QAMap] %s berkode %s, sedangkan data runner berkode %s. "
                      "Kiriman ke sana pasti ditolak QAMap, jadi pilihan ini tidak "
                      "diteruskan. Pilih yang bertanda cocok."
                      % (terpilih.get("id"), terpilih.get("code") or "(kosong)",
                         str(kode_project).strip()))
                continue
            print("[QAMap] Project tujuan: %s (%s)"
                  % (terpilih.get("id"), terpilih.get("name") or "-"))
            return terpilih.get("id") or ""
        print("Pilihan tidak dikenali. Coba lagi.")

def pilih_siklus_qamap(id_project, base_url, token, kode_project=None):
    """
    Menanyakan siklus tujuan di QAMap, lalu mengembalikan run_id-nya.

    Dipanggil HANYA ketika run_id belum ditentukan - env QAMAP_RUN_ID dan
    config.json tetap menang, supaya jalan otomatis tidak pernah menggantung
    menunggu input.

    Kenapa ditanyakan dan tidak diingat di config: run_id adalah satu-satunya
    penentu hasil mendarat di siklus SIT atau UAT, dan QAMap TIDAK memeriksa
    kecocokan jenis testnya. Salah run_id berarti bukti UAT masuk ke siklus SIT
    tanpa satu pun pesan kesalahan - berbeda dari project_id, yang kalau salah
    langsung ditolak karena dicocokkan dengan Kode Project dari data runner.
    Nilai yang sering berganti dan gagal diam-diam tidak layak diingat berkas
    config.

    Mengembalikan "" bila dilewati atau daftarnya tidak bisa diambil; pemanggil
    memperlakukannya sama seperti run_id kosong, yaitu jalan tanpa mengirim.
    """
    if not id_project:
        print("[QAMap] project_id belum diisi - pemilihan siklus dilewati.")
        return ""

    proyek = detail_project_qamap(id_project, base_url, token)
    daftar = daftar_siklus(id_project, base_url, token)

    if not daftar:
        print("[QAMap] Tidak ada siklus yang bisa diambil untuk %s." % id_project)
        print("[QAMap] Buat dulu siklusnya di QAMap (Test Execution), atau set "
              "QAMAP_RUN_ID bila siklusnya sudah ada.")
        return ""

    # Kode Project dicocokkan DI SINI, sebelum satu skenario pun dijalankan.
    #
    # Penjagaan dua sumbernya tetap seperti semula: project_id datang dari
    # config.json (alamat kiriman), sedangkan Kode Project datang dari
    # helper_laporan.py (identitas project yang benar-benar diuji). Keduanya
    # sengaja TIDAK berasal dari satu tempat - kalau iya, keduanya akan selalu
    # cocok termasuk ketika dua-duanya salah, dan pencocokannya tidak lagi ada
    # gunanya.
    #
    # Yang ditambahkan di sini hanyalah WAKTUNYA. QAMap tetap menolak kiriman
    # yang kodenya tidak cocok, tetapi penolakan itu baru datang di ujung -
    # sesudah seluruh skenario dijalankan dan buktinya dikumpulkan. Memeriksanya
    # di muka mengubah kerugiannya dari sepuluh menit terbuang menjadi satu baris
    # peringatan.
    peringatan = []
    kode_qamap = (proyek or {}).get("code") or ""
    kode_sama = (str(kode_project or "").strip().upper()
                 == str(kode_qamap).strip().upper())
    if kode_project and kode_qamap and not kode_sama:
        peringatan.append(
            "Kode Project di helper_laporan.py (%s) TIDAK COCOK dengan yang "
            "tercatat di QAMap untuk %s (%s). Kiriman hasilnya nanti ditolak."
            % (kode_project, id_project, kode_qamap))

    print("")
    print("===== SIKLUS TUJUAN QAMap =====")
    if proyek:
        print("Project: %s - %s" % (id_project, proyek.get("name") or "-"))
        if proyek.get("sedangDitinjau"):
            # Peringatan, bukan penghalang: penilaian "sedang ditinjau" datang dari
            # QAMap sendiri, dan bukti yang masuk diam-diam pada tahap itu bisa
            # membuat dokumen yang sudah ditandatangani tidak lagi cocok isinya.
            print("PERINGATAN: project ini sedang ditinjau (%s). Bukti baru yang "
                  "masuk sekarang bisa membuat dokumen yang sudah ditandatangani "
                  "tidak lagi cocok." % (proyek.get("status") or "-"))
    else:
        print("Project: %s" % id_project)
    for pesan in peringatan:
        print("PERINGATAN: %s" % pesan)
    print("")

    for i, r in enumerate(daftar, 1):
        jumlah = r.get("jumlahSkenario") or 0
        tanda = ""
        if jumlah == 0:
            # Siklus tanpa skenario PASTI menolak kiriman: QAMap menuntut tiap
            # TC-ID sudah terdaftar di siklus tujuan.
            tanda = "  <-- kosong, kiriman akan ditolak"
        elif str(r.get("status") or "") == "Completed":
            tanda = "  <-- sudah selesai"
        # Nama yang kepanjangan dipotong dengan penanda, bukan diputus begitu
        # saja: "Siklus SIT Automation ACS All CO" terbaca seperti nama yang
        # memang begitu, padahal ada sisanya.
        nama = r.get("name") or "-"
        if len(nama) > 32:
            nama = nama[:31] + "~"
        print("%2d. %-16s %-32s [%-3s] %2d skenario  %s%s"
              % (i, r.get("id") or "-", nama,
                 r.get("jenisTest") or "SIT", jumlah,
                 r.get("status") or "-", tanda))
    print(" 0. Lewati (jalankan tanpa mengirim ke QAMap)")

    while True:
        jawab = input_with_timeout("Pilih siklus: ", 60)
        if jawab in (None, "__EXIT__"):
            print("[QAMap] Tidak ada pilihan - pengiriman dilewati.")
            return ""
        jawab = str(jawab).strip()
        if jawab == "0":
            print("[QAMap] Pengiriman dilewati atas pilihan sendiri.")
            return ""
        if jawab.isdigit() and 1 <= int(jawab) <= len(daftar):
            terpilih = daftar[int(jawab) - 1]
            print("[QAMap] Siklus tujuan: %s (%s) [%s]"
                  % (terpilih.get("id"), terpilih.get("name") or "-",
                     terpilih.get("jenisTest") or "SIT"))
            return terpilih.get("id") or ""
        print("Pilihan tidak dikenali. Coba lagi.")


