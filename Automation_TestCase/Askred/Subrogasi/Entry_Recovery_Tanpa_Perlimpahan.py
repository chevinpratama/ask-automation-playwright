from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from datetime import datetime
from Automation_TestCase.Askred.Klaim import Klaim_Lunas
import pytest
import fpdf
import traceback
import sys
import re
from Automation_QAMap.qamap_client import record_step


# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Entry_Recovery_Tanpa_Perlimpahan"]
testcase_id = data["testcase_id"]
testcase_name = data["testcase_name"]
module_name = data["module_name"]
actual_result = data["actual_result"]
expected_result = data["expected_result"]
jenis_test = data["jenis_test"]
precondition = data["precondition"]
tester_name = data["tester_name"]

# ================== Variabel Global Dapat Diganti sesuai Project kalian ==================
project_code = detail_project["project_code"]
project_name = detail_project["project_name"]
project_type = detail_project["project_type"]
core_noncore = detail_project["core_noncore"]
platform = detail_project["platform"]
browser = detail_project["browser"]


def select2(page, component_id, value):
    page.locator(f"#{component_id} .select2-selection").click()
    page.wait_for_selector(".select2-container--open")

    page.locator(
        ".select2-container--open input.select2-search__field").fill(value)

    page.locator(
        ".select2-container--open li.select2-results__option", has_text=value).click()


def run_Entry_Recovery_Tanpa_Permohonan_Perlimpahan(no_registrasi=None, generate_pdf=True):
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None
    execution_time = datetime.now().strftime("%d/%m/%Y")
    nilai_penerima_recovery = "8000000"

    # 🔹 Kalau tidak ada no_registrasi → buat klaim dulu
    if not no_registrasi:
        print("="*50)
        print("🔄 START Case - Klaim Lunas sedang berjalan...")
        print("="*50)

        klaim = Klaim_Lunas.run_Registrasi_Klaim_Lunas(
            generate_pdf=False
        )

        no_registrasi = klaim.get("no_registrasi")
        polis = klaim.get("polis")
        no_lpk = klaim.get("no_lpk")
        nomor_jurnal = klaim.get("nomor_jurnal")
        nomor_jurnal_bbk = klaim.get("nomor_jurnal_bbk")

        print("="*50)
        print(f"✅ END Case - Selesai. No Klaim: {no_registrasi}")
        print("="*50)

    else:
        print(f"♻️ Menggunakan no_registrasi existing: {no_registrasi}")

    print("🚀 START Case - Entry Recovery Tanpa Perlimpahan sedang berjalan...")
    print("="*50)

    try:
        with sync_playwright() as p:
            browsers = p.chromium.launch(
                channel="msedge",
                headless=False,
                args=["--start-maximized"]
            )

            context = browsers.new_context(no_viewport=True)
            page = context.new_page()
            # ================================
            # LOGIN
            # ================================
            page.goto(get_base_url())
            page.wait_for_load_state("networkidle")
            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Mengakses halaman login ACS UAT")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector="",
                highlight=False
            ))

            accounts = load_accounts()
            page.fill("#name", accounts["chevin_klaim"]["username"])
            page.fill("#password", accounts["chevin_klaim"]["password"])
            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input username & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password", "#form-login > button"],
                highlight=True
            ))
            page.get_by_role("button", name="Sign in").click()
            page.wait_for_timeout(5000)  # ⬅ delay 5 detik
            # ================================
            # HANDLE FORCE LOGIN (Optional)
            # ================================
            force_login_btn = page.get_by_role("button", name="Force Login")
            if force_login_btn.count() > 0 and force_login_btn.is_visible():
                force_login_btn.click()
                page.wait_for_timeout(5000)  # ⬅ delay 5 detik

             # ================================
            # DASHBOARD MENU
            # ================================

            # Klik menu ASKRED
            askred_menu = page.locator("a[title='ASKRED']")
            askred_menu.wait_for(state="visible")
            askred_menu.click()

            page.wait_for_timeout(2000)

            # Klik submenu Subrogasi & Recoveries Askred
            subrogasi_recoveries_askred = page.locator(
                '//span[text()="Subrogasi & Recoveries Askred"]')
            subrogasi_recoveries_askred.wait_for(state="visible")
            subrogasi_recoveries_askred.click()

            page.wait_for_timeout(2000)

            # Klik submenu Entry Recovery
            entry_recovery = page.locator(
                '(//a[contains(@class,"ng-star-inserted") and contains(text(),"Entry Recovery")])[1]')
            entry_recovery.wait_for(state="visible")
            entry_recovery.click()

            # Klik submenu Entry Recovery Tanpa Permohonan Pelimpahan
            entry_recovery_tanpa_permohonan_perlimpahan = page.locator(
                '//a[contains(text(),"Entry Recovery Tanpa Permohonan Pelimpahan")]')
            entry_recovery_tanpa_permohonan_perlimpahan.wait_for(
                state="visible")
            entry_recovery_tanpa_permohonan_perlimpahan.click()
            page.wait_for_timeout(5000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred -> Subrogasi & Recoveries Askred -> Entry Recovery -> Entry Recovery Tanpa Permohonan Pelimpahan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    askred_menu,
                    subrogasi_recoveries_askred,
                    entry_recovery,
                    entry_recovery_tanpa_permohonan_perlimpahan
                ],
                highlight=True
            ))

            # Inquiry Subrogasi
            no_agenda = page.locator(
                "//input[@id='sigma.input.claimNoId']")
            no_agenda.wait_for(state="visible", timeout=3000)
            no_agenda.fill(no_registrasi)

            button_cari = page.locator("//button[normalize-space()='Cari']")
            button_cari.wait_for(state="visible", timeout=3000)
            button_cari.click()

            page.wait_for_timeout(5000)

            # ================= Validasi sebelum di Entry =================
            nilai_recovery = page.locator(
                "(//p[contains(@class,'text-right')])[2]")
            nilai_recovery.wait_for(state="visible", timeout=10000)
            nilai_recovery_text = nilai_recovery.text_content().strip()
            saldo_recovery_before = int(
                re.sub(r"[^\d]", "", nilai_recovery_text.split(",")[0]))
            print(f"Nilai Recovery before: {saldo_recovery_before}")

            nilai_saldo_hak_subrogasi = page.locator(
                "(//p[contains(@class,'text-right')])[3]")
            nilai_saldo_hak_subrogasi.wait_for(state="visible", timeout=10000)
            nilai_saldo_hak_subrogasi_text = nilai_saldo_hak_subrogasi.text_content().strip()
            saldo_hak_subrogasi_before = int(
                re.sub(r"[^\d]", "", nilai_saldo_hak_subrogasi_text.split(",")[0]))
            print(
                f"Nilai Saldo Hak Subrogasi Before: {saldo_hak_subrogasi_before}")

            if saldo_recovery_before != 0:
                raise Exception(
                    f"Validasi Failed Recovery awal harus 0, tapi {saldo_recovery_before}")
            else:
                print(
                    f"Validasi Passed Recovery awal sesuai: {saldo_recovery_before}")

            if saldo_hak_subrogasi_before != 8000000:
                raise Exception(
                    f"Validasi Failed Saldo awal harus 8.000.000, tapi {saldo_hak_subrogasi_before}")
            else:
                print(
                    f"Validasi Passed Saldo Hak Subrogasi awal sesuai: {saldo_hak_subrogasi_before}")

            # ==========================================================================================================
            klik_klaim = page.locator("(//p[contains(@class,'text-left')])[3]")
            klik_klaim.wait_for(state="visible", timeout=10000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Lakukan inquiry subrogasi dengan memasukkan No Klaim {no_registrasi} pada field No Agenda, lalu klik tombol Cari. Setelah itu, klik klaim yang muncul pada hasil pencarian"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    no_agenda,
                    button_cari,
                    klik_klaim
                ],
                highlight=True
            ))

            klik_klaim.click()
            page.wait_for_timeout(5000)

            tambah_button = page.locator(
                "//button[normalize-space()='Tambah']")
            tambah_button.wait_for(state="visible", timeout=3000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Tambah untuk menambahkan entry recovery baru berdasarkan klaim yang sudah dipilih sebelumnya"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    tambah_button
                ],
                highlight=True
            ))

            tambah_button.click()
            page.wait_for_timeout(5000)

            dropdown_BankGiro = page.locator(
                "//label[contains(text(),'Bank Giro')]/following::span[contains(@class,'select2-selection')][1]")
            dropdown_BankGiro.wait_for(state="visible")
            dropdown_BankGiro.click()

            search_input = page.locator(
                "//input[@class='select2-search__field']")
            search_input.wait_for(state="visible", timeout=10000)
            search_input.fill("ASK Bank Netting")

            option = page.locator(
                "//li[normalize-space()='ASK Bank Netting Kantor Pusat - 001']")
            option.wait_for(state="visible", timeout=20000)
            option.click()

            penerima_recovery = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.porsiRecoveryAskrindoId']")
            penerima_recovery.wait_for(state="visible")
            penerima_recovery.type(nilai_penerima_recovery, delay=100)

            simpan_button = page.locator(
                "//button[normalize-space()='Simpan']")
            simpan_button.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Isi form entry recovery dengan memilh Bank Giro 'ASK Bank Netting Kantor Pusat - 001' dan mengisi Porsi Recovery Askrindo dengan nilai 1.000.000, lalu klik tombol Simpan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    dropdown_BankGiro,
                    penerima_recovery,
                    simpan_button
                ],
                highlight=True
            ))
            simpan_button.click()
            page.wait_for_timeout(7000)

            # ================= Validasi sesudah di Entry ================= #
            nilai_recovery_text = nilai_recovery.text_content().strip()
            saldo_recovery_after = int(
                re.sub(r"[^\d]", "", nilai_recovery_text.split(",")[0]))
            print(f"Nilai Recovery after: {saldo_recovery_after}")

            nilai_saldo_hak_subrogasi_text = nilai_saldo_hak_subrogasi.text_content().strip()
            saldo_hak_subrogasi_after = int(
                re.sub(r"[^\d]", "", nilai_saldo_hak_subrogasi_text.split(",")[0]))
            print(
                f"Nilai Saldo Hak Subrogasi After: {saldo_hak_subrogasi_after}")

            # VALIDASI AFTER
            if saldo_recovery_after != 8000000:
                raise Exception(
                    f"Validasi Failed Recovery after harus 8.000.000, tapi {saldo_recovery_after}")
            else:
                print(
                    f"Validasi Passed Recovery after sesuai: {saldo_recovery_after}")

            if saldo_hak_subrogasi_after != 0:
                raise Exception(
                    f"Validasi Failed Saldo Hak Subrogasi after harus 0, tapi {saldo_hak_subrogasi_after}")
            else:
                print(
                    f"Validasi Passed Saldo Hak Subrogasi after sesuai: {saldo_hak_subrogasi_after}")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Setelah entry recovery berhasil disimpan, lakukan validasi dengan memastikan bahwa nilai Recovery sudah berubah menjadi 1.000.000 dan Saldo Hak Subrogasi berubah menjadi 0")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    nilai_recovery,
                    nilai_saldo_hak_subrogasi
                ],
                highlight=True
            ))

    except Exception as e:
        status = "Not Passed"
        tb = traceback.extract_tb(sys.exc_info()[2])[-1]
        log_error = str(e).strip() or "Tidak ada detail error"
        print(f"[ERROR] {log_error}")
        traceback.print_exc()
        raise Exception({
            "status": status,
            "actual_result": log_error,
            "test_steps": test_steps_rendered,
            "screenshots": screenshots_rendered,
            "testdata": {
                "Polis": polis,
                "No klaim": no_registrasi,
                "No Jurnal": nomor_jurnal,
                "No Jurnal BBK": nomor_jurnal_bbk,
            }
        })

    finally:
        print("="*50)
        print("✅ END Case - Recovery selesai dieksekusi")
        try:
            final_actual_result = actual_result.format(
                saldo_hak_subrogasi_before=saldo_hak_subrogasi_before,
                saldo_recovery_before=saldo_recovery_before,
                nilai_penerima_recovery=nilai_penerima_recovery,
                saldo_hak_subrogasi_after=saldo_hak_subrogasi_after,
                saldo_recovery_after=saldo_recovery_after
            )
            if generate_pdf:
                print("=== MASUK FUNCTION generate_pdf_report ===")
                generate_pdf_report(
                    status=status,
                    testcase_id=testcase_id,
                    testcase_name=testcase_name,
                    jenis_test=jenis_test,
                    screenshot_paths=screenshots_rendered,
                    actual_result=log_error or final_actual_result,
                    expected_result=expected_result,
                    test_steps_rendered=test_steps_rendered,
                    tester_name=tester_name,
                    precondition=precondition,
                    testdata={
                        "Polis": polis,
                        "No klaim": no_registrasi,
                        "No Jurnal": nomor_jurnal,
                        "No Jurnal BBK": nomor_jurnal_bbk,
                    }
                )

                print("\n===== TEST STEPS =====")
                for i, step in enumerate(test_steps_rendered, start=1):
                    clean_step = re.sub(r"\[Test_Step_\d+\]\s*:\s*", "", step)
                    print(f"{i}. {clean_step}")
                print("===== END TEST STEPS =====\n")

                try:
                    print("\n[SAVING TEST RESULTS TO DB]")
                    # === Simpan hasil per field ke DB
                    save_test_result_auto({
                        "project_code": project_code,
                        "project_name": project_name,
                        "project_type": project_type,
                        "core_noncore": core_noncore,
                        "tester_name": tester_name,
                        "module_name": module_name,
                        "testcase_id": testcase_id,
                        "testcase_name": testcase_name,
                        "jenis_test": jenis_test,
                        "platform": platform,
                        "browser": browser,
                        "status": status,
                        "log_error": log_error,
                        "execution_time": execution_time,
                    })
                    print(
                        f"[{status}] {testcase_id} - {testcase_name} berhasil disimpan ke DB ✅")
                except Exception as inner_e:
                    print(
                        f"[Warning] Gagal simpan hasil field ke DB: {inner_e}")
        except Exception as e:
            print(f"[Failed] Gagal simpan ke DB: {e}")

    # =========================
    # RETURN CONTROL
    # =========================
    return {
        "polis": polis,
        "no_registrasi": no_registrasi,
        "no_lpk": no_lpk,
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "status": status,
        "actual_result": log_error or final_actual_result,
        "testdata": {
            "Polis": polis,
            "No klaim": no_registrasi,
            "No Jurnal": nomor_jurnal,
            "No Jurnal BBK": nomor_jurnal_bbk,
        }
    }


@pytest.mark.positive
@pytest.mark.subrogasi
@pytest.mark.regression
def test_run_Entry_Recovery_Tanpa_Permohonan_Perlimpahan():
    run_Entry_Recovery_Tanpa_Permohonan_Perlimpahan()


# if __name__ == "__main__":
#     print("Running Case - Registrasi Klaim Disetujui...")
#     run_Entry_Recovery_Tanpa_Permohonan_Perlimpahan()
