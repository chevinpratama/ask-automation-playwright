from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.TestData import testcase_data, detail_project
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from Automation_DataAccess.helper import *
from playwright.sync_api import expect
from pages.login_page import LoginPage
from datetime import datetime, timedelta
import re
from playwright.sync_api import sync_playwright
import fpdf
import traceback
import sys


# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Akseptasi_1701_AgenPerseorangan"]
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


def run_akseptasiPP_1701(is_child=False, generate_pdf=True):
    request_number = None
    polis = None
    nopks = "PKS-Marketing-UAT"
    test_steps_rendered = []
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None  # inisialisasi
    execution_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
    try:
        # ini bagian yang di ganti
        with sync_playwright() as p:
            # browsers = p.chromium.launch(channel="msedge", # -> utk pake browser edge
            browsers = p.chromium.launch(
                headless=False,
                args=["--start-maximized"])
            context = browsers.new_context(no_viewport=True)
            page = context.new_page()

            # ================================
            # LOGIN
            # ================================
            page.goto(get_base_url())
            page.wait_for_load_state("networkidle")

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(accounts["user0808"]["username"], accounts["user0808"]["password"])
            page.wait_for_selector("#form-login > button")
            
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
            
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            menu_udw = page.locator("a[title='Underwriting Surety']")
            menu_udw.wait_for(state="visible")
            menu_udw.click()

            # Pilih menu debitur        
            menu_PP = page.locator("//a[.//span[text()='Persetujuan Prinsip']]")
            menu_PP.wait_for(state="visible")
            menu_PP.click()

    except Exception as e:
        status = "Not Passed"
        log_error = str(e).strip() or "Tidak ada detail error"
        print(f"[ERROR] {log_error}")
        traceback.print_exc()
        raise

    finally:
        try:
            # =========================
            # PDF ONLY FOR PARENT
            # =========================
            final_actual_result = actual_result.format(
                request_number=request_number or "-",
                polis=polis or "-"
            )
            if generate_pdf:
                print("masuk generate pdf")
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
                        
                    }
                )

            # ==========================
            # SAVE TO DB (ALWAYS RUN)
            # =========================
            print("\n[SAVING TEST RESULTS TO DB]")
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
            print(f"[Warning] PDF/DB process failed: {inner_e}")


def test_run_RegistrasiDJP():
    run_akseptasiPP_1701()


if __name__ == "__main__":
    run_akseptasiPP_1701() #ini jalan kalo runningnya pakai pyhton bukan pytest