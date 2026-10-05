from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from datetime import datetime
from Automation_TestCase.Askred.Subrogasi import Entry_Recovery_Tanpa_Perlimpahan
import fpdf
import traceback
import sys
import re
import pytest
from Automation_QAMap.qamap_client import record_step


# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Inquiry_Hak_Subrogasi"]
testcase_id = data["testcase_id"]
testcase_name = data["testcase_name"]
module_name = data["module_name"]
actual_result = data["actual_result"]
expected_result = data["expected_result"]
jenis_test = data["jenis_test"]
preconditon = data["precondition"]
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


def run_inquiry_hak_subrogasi(generate_pdf=True):
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None
    execution_time = datetime.now().strftime("%d/%m/%Y")
    keterangan = None

    print("="*50)
    print("🔄 [SETUP] Entry Recovery sedang berjalan...")
    print("="*50)
    entry_recovery = Entry_Recovery_Tanpa_Perlimpahan.run_Entry_Recovery_Tanpa_Permohonan_Perlimpahan(
        generate_pdf=False
    )
    no_registrasi = entry_recovery.get("no_registrasi")

    print("="*50)
    print(f"✅ [SETUP DONE] No Klaim: {no_registrasi}")
    print("="*50)

    print("🚀 [TEST] Inquiry Hak Subrogasi...")

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
            Inquery_Hak_Subrogasi = page.locator(
                '(//a[contains(@class,"ng-star-inserted") and contains(text(),"Inquery Hak Subrogasi")])[1]')
            Inquery_Hak_Subrogasi.wait_for(state="visible")
            Inquery_Hak_Subrogasi.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred -> Subrogasi & Recoveries Askred -> Entry Recovery -> Entry Recovery Tanpa Permohonan Pelimpahan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    askred_menu,
                    subrogasi_recoveries_askred,
                    Inquery_Hak_Subrogasi
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
            saldo_recovery = int(
                re.sub(r"[^\d]", "", nilai_recovery_text.split(",")[0]))
            print(f"Nilai Recovery before: {saldo_recovery}")

            nilai_saldo_hak_subrogasi = page.locator(
                "(//p[contains(@class,'text-right')])[3]")
            nilai_saldo_hak_subrogasi.wait_for(state="visible", timeout=10000)
            nilai_saldo_hak_subrogasi_text = nilai_saldo_hak_subrogasi.text_content().strip()
            saldo_hak_subrogasi = int(
                re.sub(r"[^\d]", "", nilai_saldo_hak_subrogasi_text.split(",")[0]))
            print(
                f"Nilai Saldo Hak Subrogasi Before: {saldo_hak_subrogasi}")

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

            total_recovery = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.recoveriesId']")
            total_recovery.wait_for(state="visible", timeout=10000)
            total_recovery_text = total_recovery.input_value()
            saldo_recovery1 = int(
                float(re.sub(r"[^\d.]", "", total_recovery_text)))
            print(f"Nilai Recovery: {saldo_recovery1}")

            nilai_saldo_hak_subrogasi1 = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.saldoHakSubrogasiId']")
            nilai_saldo_hak_subrogasi1.wait_for(state="visible", timeout=10000)
            nilai_saldo_hak_subrogasi_text = nilai_saldo_hak_subrogasi1.input_value()
            saldo_hak_subrogasi1 = int(
                float(re.sub(r"[^\d.]", "", nilai_saldo_hak_subrogasi_text)))
            print(f"Nilai Saldo Hak Subrogasi: {saldo_hak_subrogasi1}")

            if saldo_recovery != saldo_recovery1 or saldo_hak_subrogasi != saldo_hak_subrogasi1:
                raise Exception(
                    "Nilai Recovery dan Saldo Hak Subrogasi tidak sesuai")
            else:
                print(
                    "Nilai Recovery dan Saldo Hak Subrogasi sesuai dengan yang diharapkan")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Setelah itu, klik klaim yang muncul pada hasil pencarian, lalu pastikan nilai Recovery dan Saldo Hak Subrogasi sesuai dengan yang diharapkan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[total_recovery,
                          nilai_saldo_hak_subrogasi1],
                highlight=True
            ))
            keterangan = (
                f"Nilai Recovery dan Saldo Hak Subrogasi sesuai dengan yang diharapkan\n\n"
                f"Nilai Recovery pada table : {saldo_recovery}\n"
                f"Nilai Recovery pada form  : {saldo_recovery1}\n\n"
                f"Saldo Hak Subrogasi pada table : {saldo_hak_subrogasi}\n"
                f"Saldo Hak Subrogasi pada form  : {saldo_hak_subrogasi1}"
            )

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
                "No klaim": no_registrasi
            }
        })

    finally:
        print("="*50)
        print("✅ END Case - Inquiry Hak Subrogasi selesai dieksekusi")
        try:
            print("=== MASUK FUNCTION generate_pdf_report ===")
            if generate_pdf:
                generate_pdf_report(
                    status=status,
                    testcase_id=testcase_id,
                    testcase_name=testcase_name,
                    jenis_test=jenis_test,
                    screenshot_paths=screenshots_rendered,
                    actual_result=log_error or actual_result,
                    expected_result=expected_result,
                    test_steps_rendered=test_steps_rendered,
                    tester_name=tester_name,
                    precondition=preconditon,
                    keterangan=keterangan,
                    testdata={
                        "No klaim": no_registrasi
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

    return {
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "status": status,
        "actual_result": log_error or actual_result,
        "testdata": {
            "No klaim": no_registrasi
        }
    }


@pytest.mark.positive
@pytest.mark.subrogasi
@pytest.mark.regression
def test_run_inquiry_hak_subrogasi():
    run_inquiry_hak_subrogasi()
