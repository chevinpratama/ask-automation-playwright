# =========================
# IMPORT
# =========================
from Automation_Report.pdf_generator import generate_pdf_report
from Automation_DataAccess.testdata_askred import testcase_data
from Automation_Analyst.errror_patterns import format_error_to_human
import difflib
import importlib
import re
from Automation_Utils.testcase_scanner import scan_testcases
from Automation_Utils.testcase_loader import load_function
from Automation_Utils.menu_handler import pilih_menu
from Automation_Utils.menu_handler import input_with_timeout
from Automation_DataAccess.data_loader import load_config
from Automation_QAMap.qamap_client import (kirim_hasil, SesiProgres,
                                            start_step_logging,
                                            stop_step_logging)
from Automation_QAMap.pemilih_siklus import (pilih_project_qamap,
                                             pilih_siklus_qamap)
from Automation_DataAccess.helper_laporan import detail_project as _detail_project_qamap
import os
import sys
import traceback
import shutil

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def safe_input(prompt, timeout=30):
    val = input_with_timeout(prompt, timeout)

    if val is None:
        print(
            f"\n⏰ Tidak ada aktivitas selama {timeout} detik.")
        return "__EXIT__"

    return val.strip()

# 🔥 TAMBAHKAN DI SINI


def input_multiline(prompt="Masukkan Deskripsi (END untuk selesai):", timeout=1800):
    print(f"\n📝 {prompt}")
    lines = []

    while True:
        line = input_with_timeout("", timeout)

        if line is None:
            print("\n⏰ Timeout saat input deskripsi.")
            return "__EXIT__"

        if line.strip().upper() == "END":
            break

        if line.strip() == "0":
            return "__BACK__"

        lines.append(line)

    return "\n".join(lines).strip()


def extract_testdata_key(filepath):

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        match = re.search(
            r'testcase_data\["([^"]+)"\]',
            content
        )

        if match:
            return match.group(1)

    except Exception as e:
        print(f"❌ Gagal scan testdata key: {e}")
        traceback.print_exc()

    return None


def normalize(s):
    return s.replace("_", "").lower()

def modul_testdata(filepath):
    """
    Membaca NAMA MODUL testdata yang diimpor oleh berkas test itu sendiri.

    Tiap QA Engineer menamai berkas testdata-nya berbeda (testdata_askred,
    TestData, dan seterusnya), dan berkas test-lah yang menyatakan miliknya yang
    mana lewat barisnya sendiri:

        from Automation_DataAccess.testdata_askred import testcase_data

    Mengandalkan satu modul yang diimpor main_runner membuat seluruh testdata COB
    lain tidak ketemu tanpa satu pun pesan kesalahan.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            isi = f.read()
    except Exception as e:
        print(f"⚠️  Tidak bisa membaca {filepath} untuk mencari modul testdata: {e}")
        return None

    cocok = re.search(
        r"from\s+Automation_DataAccess\.(\w+)\s+import\s+[^\n]*testcase_data",
        isi,
    )
    return cocok.group(1) if cocok else None


def kamus_testdata(filepath):
    """
    Mengembalikan kamus testcase_data milik berkas test tersebut.

    Bila modulnya tidak bisa ditemukan atau gagal dimuat, dipakai kamus bawaan
    yang diimpor di atas - supaya perilaku lama tetap jalan, bukan meledak.
    """
    nama = modul_testdata(filepath)
    if not nama:
        return testcase_data
    try:
        modul = importlib.import_module("Automation_DataAccess." + nama)
        kamus = getattr(modul, "testcase_data", None)
        if isinstance(kamus, dict) and kamus:
            return kamus
        print(f"⚠️  Modul Automation_DataAccess.{nama} tidak memuat testcase_data - memakai bawaan.")
    except Exception as e:
        print(f"⚠️  Gagal memuat Automation_DataAccess.{nama} ({e}) - memakai bawaan.")
    return testcase_data


def get_testdata(tc_key, testcase_data):
    norm_tc = normalize(tc_key)

    for key in testcase_data:
        if normalize(key) == norm_tc:
            return testcase_data[key]

    # optional fallback
    match = difflib.get_close_matches(
        tc_key, testcase_data.keys(), n=1, cutoff=0.6)
    if match:
        return testcase_data[match[0]]

    return {}




def sasaran_qamap():
    """
    Sasaran pengiriman hasil ke QAMap: project, siklus, tester, dan token.

    Dibaca dari config.json bagian "qamap" lalu ditimpa variabel lingkungan,
    supaya repo yang sama bisa diarahkan ke siklus lain tanpa mengubah berkas.
    """
    dasar = {}
    try:
        dasar = load_config().get("qamap") or {}
    except Exception as e:
        print("[QAMap] bagian qamap di config.json tidak terbaca (%s) - memakai variabel lingkungan saja." % e)

    return {
        "base_url": os.environ.get("QAMAP_BASE_URL") or dasar.get("base_url") or "http://localhost:3001",
        "token": os.environ.get("QAMAP_TOKEN") or dasar.get("token") or "",
        "project_id": os.environ.get("QAMAP_PROJECT_ID") or dasar.get("project_id") or "",
        "run_id": os.environ.get("QAMAP_RUN_ID") or dasar.get("run_id") or "",
        "tester": os.environ.get("QAMAP_TESTER") or dasar.get("tester") or "",
    }

print("\n=== AUTOMATION REPORT GENERATOR ===\n")

while True:

    # =========================
    # STEP 1 - TIPE LAPORAN
    # =========================
    while True:
        print("===== TIPE LAPORAN =====")
        print("1. Dengan Cover")
        print("2. Tanpa Cover")
        print("0. Keluar")

        cover_choice = safe_input("Pilih: ")

        if cover_choice == "__EXIT__":
            print("\n👋 Program selesai.")
            exit()

        # EXIT PROGRAM
        if cover_choice == "0":
            print("\n👋 Program selesai.")
            exit()

        if cover_choice == "1":
            use_cover = True
            break

        elif cover_choice == "2":
            use_cover = False
            break

        else:
            print("❌ Salah input")

    # =========================
    # STEP 2 - BA
    # =========================
    while True:

        ba_map = {
            "1": "BA Regression Testing",
            "2": "BA System Integration Testing (SIT)",
            "3": "BA User Acceptance Testing (UAT)",
            "4": "BA Smoke Test"
        }

        while True:
            print("\n===== JENIS BA =====")

            for k, v in ba_map.items():
                print(f"{k}. {v}")

            print("0. Kembali")

            ba_choice = safe_input("Pilih: ")

            if ba_choice == "__EXIT__":
                print("\n👋 Program selesai.")
                exit()

            # kembali ke tipe laporan
            if ba_choice == "0":
                break

            if ba_choice in ba_map:
                ba_title = ba_map[ba_choice]
                break

            print("❌ Pilihan tidak valid")

        # balik ke STEP 1
        if ba_choice == "0":
            break

        # =========================
        # STEP 3 - DESKRIPSI
        # =========================
        deskripsi = ""

        back_to_ba = False

        if use_cover and "SIT" in ba_title.upper():

            while True:
                deskripsi = input_multiline(timeout=1800)

                if deskripsi == "__EXIT__":
                    print("\n👋 Program selesai.")
                    exit()

                # kembali ke BA
                if deskripsi == "__BACK__":
                    back_to_ba = True
                    break

                if deskripsi:
                    break

                print("❌ Deskripsi wajib diisi")

        # balik ke BA
        if back_to_ba:
            continue

        # =========================
        # STEP 4 - LINK TEST SCRIPT
        # =========================
        test_script_link = ""

        while True:

            if use_cover:

                print("\n===== LINK TEST SCRIPT =====")
                print("0. Kembali")

                test_script_link = safe_input(
                    "Masukkan Link Test Script: ",
                    timeout=300
                )

                if test_script_link == "__EXIT__":
                    print("\n👋 Program selesai.")
                    exit()

                # kembali ke BA
                if test_script_link == "0":
                    back_to_ba = True
                    break

                if not test_script_link:
                    print("❌ Link wajib diisi")
                    continue

            # balik ke BA
            if back_to_ba:
                continue

            # =========================
            # STEP 5 - JUDUL
            # =========================
            back_to_link = False

            while True:

                if use_cover:

                    print("\n===== JUDUL LAPORAN =====")
                    print("0. Kembali")

                    custom_title = safe_input(
                        "Masukkan Judul: ",
                        timeout=120
                    )

                    if custom_title == "__EXIT__":
                        print("\n👋 Program selesai.")
                        exit()

                    # kembali ke LINK TEST SCRIPT
                    if custom_title == "0":
                        back_to_link = True
                        break

                    final_title = (
                        custom_title
                        if custom_title
                        else ba_title
                    )

                else:
                    final_title = ba_title

                # =========================
                # STEP 6 - SCAN
                # =========================
                mapping = scan_testcases()

                # 🔥 default agar tidak NameError
                selected_testcases = []

                # =========================
                # STEP 7 - COB
                # =========================
                back_to_title = False

                while True:

                    selected_cob = pilih_menu(
                        "PILIH COB",
                        list(mapping.keys())
                    )

                    # =========================
                    # KEMBALI
                    # =========================
                    if selected_cob == "__BACK__":

                        # dengan cover → kembali ke Judul
                        if use_cover:
                            back_to_title = True
                            break

                        # tanpa cover → tetap di COB
                        else:
                            back_to_ba = True

                        break

                    # =========================
                    # STEP 8 - MODUL
                    # =========================
                    while True:

                        modul_list = list(mapping[selected_cob].keys())

                        print(f"\n===== MODUL ({selected_cob}) =====")

                        for i, modul in enumerate(modul_list, 1):
                            print(f"{i}. {modul}")

                        print(f"{len(modul_list)+1}. Jalankan All COB")
                        print("0. Kembali")

                        modul_choice = safe_input("Pilih: ")

                        if modul_choice == "__EXIT__":
                            print("\n👋 Program selesai.")
                            exit()

                        # =========================
                        # KEMBALI
                        # =========================
                        if modul_choice in ["0", "__BACK__"]:
                            selected_modul = "__BACK__"
                            break

                        # =========================
                        # JALANKAN ALL COB
                        # =========================
                        if modul_choice == str(len(modul_list)+1):

                            selected_testcases = []

                            for modul in modul_list:

                                for tc in mapping[selected_cob][modul]:

                                    selected_testcases.append({
                                        "modul": modul,
                                        "testcase": tc
                                    })

                            selected_modul = "ALL_MODUL"
                            break

                        # =========================
                        # PILIH MODUL NORMAL
                        # =========================
                        try:
                            selected_modul = modul_list[int(modul_choice)-1]

                        except:
                            print("❌ Input tidak valid")
                            continue

                        # =========================
                        # STEP 9 - TESTCASE
                        # =========================
                        while True:

                            cases = mapping[selected_cob][selected_modul]

                            print("\n===== PILIH TESTCASE =====")

                            for i, case in enumerate(cases, 1):
                                print(f"{i}. {case}")

                            print(f"{len(cases)+1}. Semua")
                            print("0. Kembali")

                            choice = safe_input("Pilih: ")

                            if choice == "__EXIT__":
                                print("\n👋 Program selesai.")
                                exit()

                            # kembali ke modul
                            if choice in ["0", "__BACK__"]:
                                break

                            if (
                                choice.lower() == "semua"
                                or choice == str(len(cases)+1)
                            ):
                                selected_testcases.extend(cases)
                                break

                            try:
                                indexes = [
                                    int(x.strip())
                                    for x in choice.split(",")
                                ]

                                selected_testcases.extend([
                                    cases[i - 1]
                                    for i in indexes
                                ])
                                break

                            except:
                                print("❌ Input tidak valid")

                        # kembali ke modul
                        if choice in ["0", "__BACK__"]:
                            continue

                        # lanjut execute
                        break

                    # 🔥 kembali ke COB
                    if selected_modul == "__BACK__":
                        continue

                    # 🔥 jika tidak ada testcase dipilih
                    if not selected_testcases:
                        continue

                    # lanjut execute
                    break

                # 🔥 kembali ke JUDUL
                if back_to_title:
                    continue

                break

            # 🔥 kembali ke LINK TEST SCRIPT
            if back_to_link:
                continue

            break

        if back_to_ba:
            selected_testcases = []
            continue

        # 🔥 user kembali menu / belum pilih testcase
        if not selected_testcases:
            continue

        print("\nDEBUG FINAL TESTCASE:")
        for tc in selected_testcases:
            print(tc)
        # =========================
        # EXECUTE TESTCASE
        # =========================
        all_cases = []

        # -- Pemantauan langsung di QAMap ------------------------------------
        # Dibuka SEBELUM skenario pertama berjalan, supaya layar Test Execution
        # sudah menampilkan sesinya sejak awal dan bukan baru sesudah semuanya
        # selesai. Kegagalan membuka sesi tidak menghentikan run: SesiProgres
        # yang gagal mendaftar tetap mengembalikan objek, hanya tidak aktif.
        _sasaran_progres = sasaran_qamap()

        # STEP 10 - SIKLUS TUJUAN QAMap
        #
        # Ditanyakan di sini, sesudah COB/Modul/Testcase dipilih dan tepat sebelum
        # nilainya dipakai: pertanyaannya baru bermakna setelah jelas apa yang akan
        # dijalankan, dan menaruhnya di sini membuat nilainya tidak melintasi
        # sembilan langkah menu dulu.
        #
        # Hanya muncul bila run_id memang belum ditentukan. QAMAP_RUN_ID dan
        # config.json tetap menang, jadi jalan otomatis tidak pernah menggantung.
        # Project ditanyakan lebih dulu bila belum ditentukan, lalu siklusnya.
        # Keduanya dipilih dari daftar QAMap, jadi tester tidak perlu mengetik
        # PRJ-110 maupun PRJ-110-RUN-001 - dua nilai yang tidak muncul di mana pun
        # kecuali di dalam QAMap sendiri.
        if not _sasaran_progres["project_id"]:
            _sasaran_progres["project_id"] = pilih_project_qamap(
                _sasaran_progres["base_url"],
                _sasaran_progres["token"],
                kode_project=_detail_project_qamap.get("project_code"),
            )

        if _sasaran_progres["project_id"] and not _sasaran_progres["run_id"]:
            _sasaran_progres["run_id"] = pilih_siklus_qamap(
                _sasaran_progres["project_id"],
                _sasaran_progres["base_url"],
                _sasaran_progres["token"],
                kode_project=_detail_project_qamap.get("project_code"),
            )

        # Nama penguji untuk label sesi diambil dari test data skenario yang dipilih,
        # bukan dari akun yang menjalankan runner - seirama dengan nama tester pada
        # hasil tiap skenario. Label "oleh automation" tidak memberi tahu siapa pun.
        #
        # Bila skenario yang dipilih membawa nama yang berbeda-beda, labelnya sengaja
        # dikosongkan: menonjolkan salah satu nama saja justru menyesatkan, dan QAMap
        # sudah menampilkan nama penguji per skenario di hasilnya.
        _nama_tester = set()
        for _item in selected_testcases:
            _kunci = _item["testcase"] if isinstance(_item, dict) else _item
            _nama = (get_testdata(_kunci, testcase_data) or {}).get("tester_name")
            if _nama and str(_nama).strip() and str(_nama).strip().lower() != "automation":
                _nama_tester.add(str(_nama).strip())
        _tester_sesi = list(_nama_tester)[0] if len(_nama_tester) == 1 else ""

        sesi_progres = SesiProgres.mulai(
            None,                                   # daftarnya diambil dari siklus QAMap
            id_project=_sasaran_progres["project_id"],
            kode_project=_detail_project_qamap.get("project_code"),
            run_id=_sasaran_progres["run_id"],
            tester=_sasaran_progres["tester"] or _tester_sesi,
            base_url=_sasaran_progres["base_url"],
            token=_sasaran_progres["token"],
        )

        for item in selected_testcases:
            # mode ALL COB
            if isinstance(item, dict):
                tc_key = item["testcase"]
                modul_execute = item["modul"]

            # mode normal
            else:
                tc_key = item
                modul_execute = selected_modul
            print(f"\n🚀 Running: {tc_key}")

            try:
                # 🔥 LOAD FUNCTION
                func = load_function(selected_cob, modul_execute, tc_key)

                # 🔥 AMBIL TESTDATA
                filepath = (
                    f"Automation_TestCase/"
                    f"{selected_cob}/"
                    f"{modul_execute}/"
                    f"{tc_key}.py"
                )

                # 🔥 AMBIL TESTDATA DARI ISI FILE
                testdata_key = extract_testdata_key(filepath)

                # Kamusnya diambil dari modul yang DIIMPOR berkas test itu,
                # bukan dari satu modul yang dipatok di atas.
                kamus = kamus_testdata(filepath)

                if testdata_key:
                    data = kamus.get(testdata_key) or get_testdata(testdata_key, kamus)
                else:
                    data = get_testdata(tc_key, kamus)

                if not data:
                    # Disebut terang-terangan: tanpa testdata, TC-ID jatuh ke nama
                    # berkas dan kirimannya akan ditolak QAMap karena bukan TC-<angka>.
                    print(f"⚠️  Testdata untuk '{testdata_key or tc_key}' tidak ketemu di "
                          f"modul testdata berkas ini. TC-ID, Expected Result, dan "
                          f"precondition akan kosong.")

                print(f"\n🚀 PYTEST RUNNING: {filepath}")

                # TC-ID QAMap ada di testdata; bila kosong, laporan progresnya
                # tidak akan cocok dengan siklus dan diabaikan server.
                _tc_id = (data or {}).get("testcase_id") or tc_key
                _tc_nama = (data or {}).get("testcase_name") or tc_key
                sesi_progres.kasus_mulai(_tc_id, _tc_nama)
                # Sasaran laporan per langkah. Berkas test yang memakai
                # record_step() akan mengabarkan tiap langkahnya ke sini pada
                # saat langkah itu terjadi, tanpa pemanggilan tambahan di badannya.
                start_step_logging(sesi_progres, _tc_id)

                try:
                    # Batch Mode
                    # Jangan generate PDF individual.
                    # Main Runner hanya mengambil hasil testcase.
                    result = func(generate_pdf=False)

                except Exception as e:

                    print(f"❌ ERROR GLOBAL di {tc_key}: {e}")

                    # jika raise Exception(dict)
                    if e.args and isinstance(e.args[0], dict):
                        result = e.args[0]

                    else:
                        result = {
                            "status": "Not Passed",
                            "actual_result": str(e),
                            "test_steps": [],
                            "screenshots": [],
                            "testdata": {}
                        }

                # 🔥 FORMAT ERROR
                actual_result_raw = result.get("actual_result", "")

                if result.get("status") == "Not Passed":
                    actual_result = format_error_to_human(actual_result_raw)
                else:
                    actual_result = actual_result_raw

                # 🔥 BUILD RESULT
                case_result = {
                    "testcase_id": data.get("testcase_id") or tc_key,
                    "testcase_name": data.get("testcase_name") or tc_key,
                    "module_name": modul_execute,
                    "severity": data.get("severity") or "-",
                    "fitur": data.get("fitur") or "-",
                    "reg_id": data.get("reg_id") or "-",
                    "jenis_test": data.get("jenis_test") or "-",
                    "tester_name": data.get("tester_name") or "Automation",
                    "precondition": data.get("precondition") or "-",
                    "expected_result": data.get("expected_result") or "-",
                    "testdata": (
                        result.get("testdata")
                        or data.get("testdata")
                        or {}
                    ),
                    "actual_result": actual_result,
                    "status": result.get("status") or "Not Passed",
                    "test_steps": result.get("test_steps") or [],
                    "screenshots": result.get("screenshots") or [],
                    "database_verifications": result.get("database_verifications") or [],

                }

                # Dilepas sebelum skenario berikutnya, supaya langkah tidak
                # pernah mendarat di skenario yang keliru.
                stop_step_logging()

                all_cases.append(case_result)

                # Langkahnya baru diketahui sekarang - berkas test menyusunnya
                # sambil berjalan - jadi rinciannya disetor di sini, bukan di awal.
                sesi_progres.kasus_selesai(
                    _tc_id,
                    case_result.get("test_steps") or [],
                    lulus=str(case_result.get("status", "")).strip().lower() in
                          ("passed", "pass", "ok", "success", "lulus"),
                    pesan=case_result.get("actual_result") or None,
                )

            except Exception as outer_error:
                print(f"❌ FATAL MAIN RUNNER ERROR: {outer_error}")
        # Sesi progres ditutup lebih dulu. Sesi yang dibiarkan terbuka akan
        # selamanya tampil "sedang berjalan" di QAMap, dan langkah yang tidak
        # pernah dijalankan ditandai 'skipped' oleh server saat penutupan ini.
        sesi_progres.tutup("selesai")

        # =========================
        # KIRIM KE QAMAP - WAJIB SEBELUM PDF
        # =========================
        #
        # generate_pdf_report() memanggil cleanup_screenshots() di ujungnya, yang
        # MENGHAPUS berkas screenshot dari disk. Kalau pengirimannya dilakukan
        # sesudah PDF, seluruh path gambar sudah mati dan buktinya terkirim kosong
        # tanpa satu pun pesan kesalahan.
        #
        # QAMap tidak menerima berkas PDF: yang disetorkan adalah langkah, gambar,
        # status, dan tanggalnya, lalu QAMap sendiri yang mencetak dokumennya lewat
        # format Report bawaannya - supaya hasil automation tampil sama persis
        # dengan hasil eksekusi manual.
        if all_cases:
            # Sasaran yang SAMA dengan yang dipakai sesi progres, bukan dibaca ulang.
            #
            # Membaca ulang berarti siklus yang barusan dipilih di STEP 10 hilang,
            # dan pengiriman jatuh kembali ke run_id lama di config - persis salah
            # kamar yang hendak dicegah. Membaca ulang juga membuka celah lain:
            # variabel lingkungan yang berubah di tengah run akan membuat sesi
            # progres dan hasil akhirnya mendarat di dua siklus yang berbeda.
            _sasaran = _sasaran_progres
            if not _sasaran["project_id"] or not _sasaran["run_id"]:
                print("[QAMap] Pengiriman DILEWATI: project_id atau run_id belum diisi.")
                print("[QAMap] Isi bagian qamap di Automation_DataAccess/config.json,")
                print("[QAMap] atau set QAMAP_PROJECT_ID dan QAMAP_RUN_ID.")
            else:
                try:
                    kirim_hasil(
                        all_cases,
                        id_project=_sasaran["project_id"],
                        tester=_sasaran["tester"],
                        run_id=_sasaran["run_id"],
                        base_url=_sasaran["base_url"],
                        token=_sasaran["token"],
                        kode_project=_detail_project_qamap.get("project_code"),
                    )
                except Exception as e:
                    # Dicetak mencolok: kegagalan di sini berarti hasilnya TIDAK
                    # masuk ke QAMap sementara PDF-nya tetap terbentuk - gejala yang
                    # mudah disangka baik-baik saja.
                    print("=" * 70)
                    print("[QAMap] GAGAL MENGIRIM - hasil TIDAK masuk ke QAMap: %s" % e)
                    print("=" * 70)


        # =========================
        # GENERATE PDF
        # =========================
        if all_cases:
            try:
                generate_pdf_report(
                    all_cases=all_cases,
                    show_page_number=True,
                    use_cover=use_cover,
                    ba_title=ba_title,
                    report_title=final_title,
                    deskripsi=deskripsi,
                    test_script_link=test_script_link

                )

                print("\n✅ PDF berhasil dibuat")


            except Exception as e:
                print(f"\n❌ Gagal generate PDF: {e}")

        else:
            print("\n❌ Tidak ada testcase yang berhasil dijalankan")

        break
