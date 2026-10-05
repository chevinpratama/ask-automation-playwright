from numpy import inner

from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import testcase_data
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from Automation_DataAccess.helper import *
from Automation_DataAccess.helper_laporan import detail_project
from playwright.sync_api import expect
from pages.login_page import LoginPage
from datetime import datetime, timedelta
import re
from playwright.sync_api import sync_playwright
import fpdf
import traceback
import sys
from Automation_QAMap.qamap_client import record_step

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Akseptasi_RegistrasiDJP"]
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


def run_RegisDJP(generate_pdf=True):
    request_number = None
    polis = None
    nopks = "PKS-Marketing-UAT"
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
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
            login_page.login(
                accounts["userteam"]["username"], accounts["userteam"]["password"])
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

            menu_marketing = page.locator("a[title='Marketing']")
            menu_marketing.wait_for(state="visible")
            menu_marketing.click()

            # Pilih menu debitur
            menu_debitur = page.locator("//a[.//span[text()='Debitur']]")
            menu_debitur.wait_for(state="visible")
            menu_debitur.click()

            # search nama debitur
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')

            search.fill("MOERSIDI BP")
            search.press("Enter")

            row = page.locator("#dt_basic tbody tr",
                               has_text="MOERSIDI BP").first

            expect(row).to_be_visible(timeout=100000)
            row.click()

            # 1. Definisikan locator
            checkbox_input = page.locator(
                'input[id="sigma.checkbox.isBlacklistId"]')
            label_switch = page.locator(
                'label[for="sigma.checkbox.isBlacklistId"]')

            # 2. Tunggu elemen input muncul di DOM
            checkbox_input.wait_for(state="attached")

            # 3. Cek status (True/False)

            is_blacklist = checkbox_input.is_checked()

            # CATATAN :
            # is_blacklist = checkbox_input.get_attribute("value") == "true"

            if is_blacklist:
                print(
                    "Status: Ya (True). Mengklik label untuk mengubah ke Tidak (False)")
                # Klik pada labelnya
                label_switch.click()
            else:
                print("Status: Tidak (False). Posisi aman, tidak usah diklik.")

            # Klik tombol Simpan
            btn_simpan = page.get_by_role("button", name="Simpan")
            btn_simpan.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            #  tunggu logout muncul
            logout = page.locator('//a[@title="Sign Out"]')
            logout.wait_for(state="visible", timeout=15000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # LOGIN
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userutama"]["username"], accounts["userutama"]["password"])
            page.wait_for_selector("#form-login > button")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input username & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password"],
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
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            menu_askred = page.locator("a[title='ASKRED']")
            menu_askred.wait_for(state="visible")
            menu_askred.click()

            # Pilih menu Akseptasi Askred
            menu_Akseptasiaskred = page.locator(
                "//a[.//span[text()='Akseptasi Askred']]")
            menu_Akseptasiaskred.wait_for(state="visible")
            menu_Akseptasiaskred.click()

            # klik menu Registrasi DJP
            menu_RegisDJP = page.locator(
                "//a[contains(text(),'Registrasi DJP')]")
            menu_RegisDJP.wait_for(state="visible")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred/Akseptasi Askred kemudian menu Registrasi DJP")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//a[.//span[text()='Akseptasi Askred']]",
                          "//a[contains(text(),'Registrasi DJP')]"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            menu_RegisDJP.click()
            # ================================
            # TOMBOL TAMBAH DATA
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            create_button = page.locator('//a[@name="create-data"]')
            create_button.wait_for(state="visible")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Tambah Data"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//a[@name="create-data"]'],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            create_button.click()

            # ================================
            # Isi Field Mandatory
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            unique = str(int(time.time()))

            page.locator(
                '//*[@id="sigma.input.Nomor Register"]').fill(f"REG-{unique}")
            page.locator(
                '//*[@id="sigma.input.Nomor Surat Pengantar"]').fill(f"SP{unique}")
            page.locator(
                '//*[@id="sigma.input.Nomor DJP"]').fill(f"DJP-{unique}")

            # page.wait_for_selector("#sigma\.textarea\.Catatan")
            page.locator('//*[@id="sigma.textarea.Catatan"]').fill("Catatan")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Insert Registrasi dan Isi semua Mandatory Field"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="sigma.input.Nomor Register"]',
                    '//*[@id="sigma.input.Nomor Surat Pengantar"]',
                    '//*[@id="sigma.input.Nomor DJP"]',
                    '//*[@id="sigma.textarea.Catatan"]',
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))

            # page.wait_for_selector("#lookupPksButton")
            page.locator('//*[@id="lookupPksButton"]').click()

            # page.wait_for_selector("#sigma\.input\.Nomor\ PKS")
            page.locator(
                '//*[@id="sigma.input.Nomor PKS"]').fill(nopks)

            # page.wait_for_selector("#btnCari")
            page.locator('//*[@id="btnCari"]').click()

            page.locator(
                '//datatable-row-wrapper//input[@type="checkbox"][1]').first.click()

            page.wait_for_selector(
                '//button[contains(@class,"btn btn-primary pull-right") and normalize-space()="Pilih"]')
            page.locator(
                '//button[contains(@class,"btn btn-primary pull-right") and normalize-space()="Pilih"]').first.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : input dan pilih nomor PKS"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="lookupPksButton"]',
                    '//*[@id="sigma.input.Nomor PKS"]',
                    '//*[@id="btnCari"]',
                    '//datatable-row-wrapper//input[@type="checkbox"][1]',
                    '//button[contains(@class,"btn btn-primary pull-right") and normalize-space()="Pilih"]',
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))

            stepno += 1

            # pilih tanggal surat pengantar
            today = datetime.today().day
            page.wait_for_selector('//input[@placeholder="periode"]')
            page.locator('//input[@placeholder="periode"]').nth(1).click()

            page.locator(f'//td[normalize-space()="{today}"]').click()

            # pilih tanggal periode DJP Dari-sampai
            today = datetime.today()
            date_from = today.replace(year=2025, month=12)

            # Desember (tanggal tetap hari ini)
            date_to = today.replace(month=12)

            # TANGGAL DARI (jangka waktu kredit)
            day_from = date_from.day
            month_from = date_from.strftime("%b")
            year_from = str(date_from.year)

            page.locator('//input[@placeholder="Dari"]').click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_from)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_from)

            page.locator(f'//td[normalize-space()="{day_from}"]').click()

            # TANGGAL SAMPAI
            day_to = date_to.day
            month_to = date_to.strftime("%b")
            year_to = str(date_to.year)

            page.locator('//input[@placeholder="Sampai"]').click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_to)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_to)

            page.locator(f'//td[normalize-space()="{day_to}"]').click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Insert Registrasi dan Isi semua Mandatory Field"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[

                    '//input[@placeholder="periode"]',
                    '//input[@placeholder="Dari"]',
                    '//input[@placeholder="Sampai"]',
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))
            # ================================
            # Isi Field Realisasi
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            page.locator('//button[normalize-space()="REALISASI"]').click()

            page.locator(
                "//label[contains(text(),'Product PKS')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="A13 - KI Perluasan - PKS-APRIL/2024").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik button REALISASI dan Pilih Produk PKS"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//button[normalize-space()="REALISASI"]',
                          "//label[contains(text(),'Product PKS')]/following::span[contains(@class,'select2-selection')][1]",
                          "//button[normalize-space()='PROCEED']",
                          ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            stepno += 1
            page.wait_for_selector("//button[normalize-space()='PROCEED']")
            page.locator("//button[normalize-space()='PROCEED']").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik Button PROCEED"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//button[normalize-space()='PROCEED']",
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # pilih nama debitur
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            page.wait_for_selector(
                "//li[@data-name='askred-objek-pertanggungan']")
            page.locator(
                "//li[@data-name='askred-objek-pertanggungan']").click()

           # search nama debitur
            page.locator(
                "//*[@id='sigma.dual.input']//section[2]//button").click()
            page.locator(
                "//p[normalize-space()='MOERSIDI BP']/ancestor::div[contains(@class,'datatable-row')]//input[@type='checkbox']").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi field mandatory menu Objek Pertanggungan pada data debitur, Informasi Kredit")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//p[normalize-space()='MOERSIDI BP']/ancestor::div[contains(@class,'datatable-row')]//input[@type='checkbox']"

                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.get_by_role("button", name="Pilih").click()
            # ================================
            # isi dan lengkapi Akseptasi Detail pada menu objek pertanggungan
            # ================================
            stepno += 1
            # isi informasi kredit
            unique = str(int(time.time()))
            page.locator(
                '//*[@id="sigma.input.No Perjanjian Kredit"]').fill(f"PK-{unique}")
            page.locator(
                '//*[@id="sigma.input.Nomor Rekening Pinjaman"]').fill(f"{unique}")
            page.locator(
                '//*[@id="sigma.numeric.sigma.currency.amount.plafondKredit1"]').type("100000000")

            # Isi pertanggungan
            nilai = page.locator(
                '//input[@id="sigma.numeric.sigma.currency.amount.nilaiPertanggungan1" and not(@disabled)]')
            nilai.click()
            nilai.type("100000000")

            # TANGGAL DARI (jangka waktu kredit
            page.locator('//input[@placeholder="Dari"]').nth(0).click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_from)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_from)

            page.locator(f'//td[normalize-space()="{day_from}"]').click()

            # TANGGAL SAMPAI (jangka waktu kredit)
            page.locator('//input[@placeholder="Sampai"]').nth(0).click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_to)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_to)

            page.locator(f'//td[normalize-space()="{day_to}"]').click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi field mandatory menu Objek Pertanggungan pada data debitur, Informasi Kredit")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//input[@placeholder="Sampai"]',
                    '//input[@placeholder="Dari"]',
                    '//*[@id="sigma.input.Nomor Rekening Pinjaman"]',
                    '//*[@id="sigma.input.No Perjanjian Kredit"]',

                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # klik field dropdown
            page.locator('//*[@id="sigma.select.Kolektibilitas"]/span').click()
            page.wait_for_selector(
                "//ul[contains(@class,'select2-results__options')]")
            page.locator("//li[contains(text(),'1')]").click()

            stepno += 1
            # isi dan lengkapi petanggungan
            page.locator('//*[@id="sigma.percentage.Rate Premi"]').fill("1")

            # klik hitung premi
            btn = page.locator('#btnHitungPremi')

            btn.wait_for(state="attached")
            btn.wait_for(state="visible")

            btn.scroll_into_view_if_needed()
            btn.click()

            # validasi nilai muncul
            formula = page.locator(
                '//*[@id="sigma.numeric.sigma.currency.amount.netNilaiPremi1"]')

            expect(formula).not_to_have_value("", timeout=15000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi field mandatory menu Objek Pertanggungan pada data debitur, isi rate premi lalu klik button Hitung Premi")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//*[@id="sigma.numeric.sigma.currency.amount.plafondKredit1"]',
                          '//*[@id="sigma.percentage.Rate Premi"]'
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # ================================
            # hitung summary
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            # menu summary
            page.wait_for_selector("//li[@data-name='askred-summary']")
            page.locator("//li[@data-name='askred-summary']").click()

            # klik hitung summary
            page.locator('//button[@id="btnHitungPremiSummary"]').click()

            # tunggu summary muncul
            page.wait_for_selector('//askred-summary//datatable-row-wrapper')

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("on process")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Hitung Summary")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//li[@data-name='askred-summary']",
                          '//askred-summary//datatable-row-wrapper',
                          '//button[@id="btnHitungPremiSummary"]',
                          '//button[contains(@class,"workflow-btn") and normalize-space()="Save"]',
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_selector(
                '//button[contains(@class,"workflow-btn") and normalize-space()="Save"]')
            page.locator(
                '//button[contains(@class,"workflow-btn") and normalize-space()="Save"]').click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # kirim ke kabag UW (review)
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            # klik review kabag UW
            page.click('//button[normalize-space()="Review KABAG UW"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik Review KABAG UW")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//button[normalize-space()="Review KABAG UW"]',
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # pilih approval list
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            # pilih approval list olan UDW KCU ASKRED
            nama = "Olan UDW KCU ASKRED"

            row = page.locator(f'''
            //div[@class="modal-body"]
            //datatable-row-wrapper[.//div[contains(.,"{nama}")]]
            ''')

            row.wait_for(state="visible")
            row.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : pilih approval list")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '[id^="smallbox"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))
            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').first

            notif.wait_for(state="visible")
            text = notif.inner_text()

            notif.click()

            #  tunggu logout muncul
            logout = page.locator('//a[@title="Sign Out"]')
            logout.wait_for(state="visible", timeout=15000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # login dengan user approval 1 (review kabag UW)
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userkabaguw"]["username"], accounts["userkabaguw"]["password"])

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input username review kabag UW & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password", "#form-login > button"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
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
            # cari no. dokumen yg ingin di approve
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator('//*[@id="activity"]').click()

            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            # ambil request number
            request_number = get_request_number_from_notif(page)

            # search req number
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(request_number)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{request_number}"]')

            cell.wait_for(state="visible", timeout=25000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. request")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//button[@title="See Details"]',
                    '//*[@id="dt_basic"]/tbody/tr',
                    '//input[@type="search" and @aria-controls="dt_basic"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # klik row
            row = page.locator(
                f'//tr[.//td[normalize-space()="{request_number}"]]')
            row.click()

            # ================================
            # klik send to pincab
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("reviewed")

            page.wait_for_selector(
                '//button[normalize-space()="Send To PINCAB"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button send to PINCAB")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="Send To PINCAB"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.locator(
                '//button[normalize-space()="Send To PINCAB"]').click()

            # ================================
            # pilih approval list 2
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            # pilih approval list Olan PINCAB KCU ASKRED
            nama = "Olan PINCAB KCU ASKRED"

            row = page.locator(f'''
            //div[@class="modal-body"]
            //datatable-row-wrapper[.//div[contains(.,"{nama}")]]
            ''')

            row.wait_for(state="visible")
            row.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : pilih approval list (2)")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    f'''
            //div[@class="modal-body"]
            //datatable-row-wrapper[.//div[contains(.,"{nama}")]]
            '''
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').first

            notif.wait_for(state="visible")
            text = notif.inner_text()

            notif.click()

            #  tunggu logout muncul
            logout = page.locator('//a[@title="Sign Out"]')
            logout.wait_for(state="visible", timeout=15000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # login dengan user approval 2 (Pinca)
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userpinca"]["username"], accounts["userpinca"]["password"])

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input username PINCAB & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password", "#form-login > button"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
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
            # cari no. dokumen yg ingin di approve (2)
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator('//*[@id="activity"]').click()

            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            # search req number
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(request_number)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{request_number}"]')

            cell.wait_for(state="visible", timeout=10000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. request")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="dt_basic"]/tbody/tr',
                    '//input[@type="search" and @aria-controls="dt_basic"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # klik row
            row = page.locator(
                f'//tr[.//td[normalize-space()="{request_number}"]]')
            row.click()

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').first

            notif.wait_for(state="visible")
            text = notif.inner_text()

            notif.click()

            # ================================
            # klik approve
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("approve")

            page.wait_for_selector('//button[normalize-space()="Approve"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button Approve")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="Approve"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_timeout(5000)
            page.locator('//button[normalize-space()="Approve"]').click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').first

            notif.wait_for(state="visible")
            text = notif.inner_text()

            notif.click()

            #  tunggu logout muncul
            logout = page.locator('//a[@title="Sign Out"]')
            logout.wait_for(state="visible", timeout=15000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            stepno += 1
            page.wait_for_load_state("networkidle")

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userutama"]["username"], accounts["userutama"]["password"])

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Kembali ke akun utama dan Input username & password lalu klik login")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["#name", "#password", "#form-login > button"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
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
            # cari no. dokumen yg ingin diterbitkan
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator('//*[@id="activity"]').click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik icon activity lalu klik see details")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="activity"]',
                    '//button[@title="See Details"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            stepno += 1
            page.wait_for_load_state("networkidle")

            # search req number
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(request_number)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{request_number}"]')

            cell.wait_for(state="visible", timeout=10000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. request")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//input[@type="search" and @aria-controls="dt_basic"]',
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # klik row
            row = page.locator(
                f'//tr[.//td[normalize-space()="{request_number}"]]')
            row.click()

            # ================================
            # klik terbit
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("Terbit")

            page.wait_for_selector('//button[normalize-space()="Terbit"]')
            page.locator('//button[normalize-space()="Terbit"]').click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi Analisa/Saran/Disposisi/Kesimpulan")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="Terbit"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # klik ya pada overlay konfirmasi
            # ================================
            stepno += 1

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button terbit lalu klik 'ya' pada overlay konfirmasi")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//div[contains(@class,'MessageBoxButtonSection')]//button[2]"
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # cek polis yg udh terbit
            # ================================
            stepno += 1
            page.wait_for_selector(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]')
            page.locator(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]').click()

            # ambil request number
            request_number = get_request_number_from_notif(page)

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

            polis = get_no_polis(page)
            print(f'No Polis : {polis}')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : cek polis yg sdh berhasil terbit"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//input[@id="idNomorRequest"]',
                    '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]',
                    '//input[@type="search" and @aria-controls="dt_basic"]'
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
                "No PKS": nopks,
            }
        })

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
                        "No PKS": nopks,
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
                    f"[{status}] {testcase_id} - {testcase_name} berhasil disimpan ke DB ✅"
                )

        except Exception as inner_e:
            print(f"[Warning] PDF/DB process failed: {inner_e}")

    # =========================
    # RETURN CONTROL
    # =========================
    return {
        "request_number": request_number,
        "polis": polis,
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "status": status,
        "actual_result": log_error or final_actual_result,
        "testdata": {
            "No PKS": nopks,
        }
    }


def test_run_RegistrasiDJP():
    run_RegisDJP()


if __name__ == "__main__":
    run_RegisDJP()  # ini jalan kalo runningnya pakai pyhton bukan pytest
