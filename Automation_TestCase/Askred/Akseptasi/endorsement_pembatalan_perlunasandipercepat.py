from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.helper_laporan import detail_project

# from Automation_DataAccess.config import Credential
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from datetime import datetime, timedelta
from pages.login_page import LoginPage
import fpdf
import traceback
import sys
import re
from Automation_TestCase.Askred.Akseptasi.Akseptasi_RegistrasiDJP import run_RegisDJP
import os
from Automation_QAMap.qamap_client import record_step

# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["endorsement_pembatalan_perlunasandipercepat"]
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


def test_endorse_dipercepat(generate_pdf=True):
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None  # inisialisasi
    execution_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
    akseptasi = run_RegisDJP(generate_pdf=False)
    request_number = akseptasi.get("request_number")
    polis = akseptasi.get("polis")

    print("polis:", polis)
    print("request_number:", request_number)

    try:
        # ini bagian yang di ganti
        with sync_playwright() as p:
            # browsers = p.chromium.launch(channel="msedge", -> utk pake browser edge
            browsers = p.chromium.launch(
                headless=False, args=["--start-maximized"])
            context = browsers.new_context(no_viewport=True)
            page = context.new_page()
            # ================================
            # LOGIN
            # ================================
            stepno += 1

            page.goto(get_base_url())
            page.wait_for_load_state("networkidle")
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Buka halaman login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector="",
                highlight=False,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            stepno += 1
            page.wait_for_load_state("networkidle")

            # # page.wait_for_selector('#name', state="visible")
            # page.fill('#name', Credential.userutama)

            # # page.wait_for_selector('#password', state="visible")
            # page.fill('#password', Credential.pass_utama)

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userutama"]["username"], accounts["userutama"]["password"])

            page.wait_for_selector("#form-login > button")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input username & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password", "#form-login > button"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.locator("#form-login > button").click()
            page.wait_for_timeout(5000)

            # ================================
            # HANDLE FORCE LOGIN (Optional)
            # ================================
            force_login_btn = page.get_by_role("button", name="Force Login")
            if force_login_btn.count() > 0 and force_login_btn.is_visible():
                force_login_btn.click()
                page.wait_for_timeout(3000)  # ⬅ delay 3 detik

            # ================================
            # DASHBOARD MENU
            # ================================
            stepno += 1
            # Pilih menu ASKRED
            menu_askred = page.locator("a[title='ASKRED']")
            menu_askred.wait_for(state="visible")
            menu_askred.click()

            # Pilih menu Akseptasi Askred
            menu_Akseptasiaskred = page.locator(
                "//a[.//span[text()='Akseptasi Askred']]")
            menu_Akseptasiaskred.wait_for(state="visible")
            menu_Akseptasiaskred.click()

            # klik menu inquiry Polis
            menu_inquiry = page.locator(
                "//a[contains(text(),'Inquiry Polis')]")
            menu_inquiry.wait_for(state="visible")
            menu_inquiry.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred/Akseptasi Askred kemudian menu Inquiry Polis")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//a[.//span[text()='Akseptasi Askred']]",
                          "//a[contains(text(),'Inquiry Polis')]"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # TOMBOL Filter
            # ================================
            stepno += 1
            page.wait_for_selector(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]')
            page.locator(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]').click()

            # ambil request number dri file request.txt
            with open("request.txt", "r") as f:
                request_number = f.read().strip()

            # isi ke field
            input_noreq = page.locator('//input[@id="idNomorRequest"]')

            input_noreq.wait_for(state="visible")
            input_noreq.fill(request_number)

            page.wait_for_selector(
                '//button[@id="searchBtn" and contains(@class,"btn-primary")]')
            page.locator(
                '//button[@id="searchBtn" and contains(@class,"btn-primary")]').click()

            page.wait_for_selector('#closeBtn')
            page.locator('#closeBtn').click()

            # biar gk turun
            page.locator('//h1').scroll_into_view_if_needed()

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{request_number}"]')

            cell.wait_for(state="visible", timeout=50000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol filter dan input nomor request"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # klik endorse pada data yang dipilih
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik endorse pada data polis yang dipilih"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//a[@data-action="endorse"]'
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_selector('//a[@data-action="endorse"]')
            page.locator('//a[@data-action="endorse"]').click()

            # ================================
            # pilih jenis endorsement
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//label[contains(text(),'Jenis Endorsement')]/following::span[contains(@class,'select2-selection')][1]").click()

            page.wait_for_selector(".select2-container--open")

            page.locator(".select2-container--open li.select2-results__option",
                         has_text="Pembatalan").click()

            page.locator(
                "//label[contains(text(),'Jenis Pembatalan')]/following::span[contains(@class,'select2-selection--single')][1]").click()

            page.wait_for_selector(".select2-container--open")

            page.locator(".select2-container--open li.select2-results__option",
                         has_text="Perlunasan Dipercepat").click()
            page.wait_for_selector(
                '//button[@id="submitModal" and normalize-space()="Lanjut"]')

            # ================================
            # klik endorse pada data yang dipilih
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih Jenis Endorsement -> pembatalan lalu klik lanjut"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//label[contains(text(),'Jenis Endorsement')]/following::span[contains(@class,'select2-selection')][1]",
                          '//button[@id="submitModal" and normalize-space()="Lanjut"]',
                          "//label[contains(text(),'Jenis Pembatalan')]/following::span[contains(@class,'select2-selection')][1]"
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            page.locator(
                '//button[@id="submitModal" and normalize-space()="Lanjut"]').click()

            # ================================
            # isi tanggal effective
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            today = datetime.today().day
            page.wait_for_selector('//input[@placeholder="Tanggal Effective"]')
            page.locator('//input[@placeholder="Tanggal Effective"]').click()

            page.locator(f'//td[normalize-space()="{today}"]').click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi tanggal effective"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//label[contains(text(),'Jenis Endorsement')]/following::span[contains(@class,'select2-selection')][1]",
                          '//button[@id="submitModal" and normalize-space()="Lanjut"]',
                          "//label[contains(text(),'Jenis Pembatalan')]/following::span[contains(@class,'select2-selection')][1]"
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

    except Exception as e:
        status = "Not Passed"
        log_error = str(e).strip() or "Tidak ada detail error"
        print(f"[ERROR] {log_error}")
        traceback.print_exc()

        raise Exception({
            "status": status,
            "actual_result": log_error,
            "test_steps": test_steps_rendered,
            "screenshots": screenshots_rendered,
            "testdata": {
                "No Request": request_number,
                "No Polis": polis,
            }
        })

    finally:
        try:
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
                    precondition=precondition,
                    testdata={
                        "No Request": request_number,
                        "No Polis": polis,
                    }
                )
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
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "status": status,
        "actual_result": actual_result or log_error,
        "testdata": {
            "No Request": request_number,
            "No Polis": polis,
        }
    }


if __name__ == "__main__":
    test_endorse_dipercepat()
