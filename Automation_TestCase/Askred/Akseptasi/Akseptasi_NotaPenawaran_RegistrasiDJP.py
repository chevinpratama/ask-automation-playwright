from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import testcase_data
from Automation_DataAccess.helper_laporan import detail_project
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from Automation_DataAccess.helper import *
from playwright.sync_api import expect
from pages.login_page import LoginPage
from datetime import datetime, timedelta
from pathlib import Path
import re
from playwright.sync_api import sync_playwright
import fpdf
import traceback
import sys
from Automation_QAMap.qamap_client import record_step


# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Akseptasi_NotaPenawaran_RegistrasiDJP"]
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


def run_RegisDJP_NotaPenawaran(generate_pdf=True):
    request_number = None
    polis = None
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
            # akses acs
            # ================================
            page.goto(get_base_url())
            page.wait_for_load_state("networkidle")

            # ================================
            # LOGIN
            # ================================
            stepno += 1

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

            # klik menu Analisa Debitur
            menu_analisa = page.locator(
                "//a[contains(text(),'Analisa Debitur')]")
            menu_analisa.wait_for(state="visible")
            menu_analisa.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : User Klik dropdown menu ASKRED -> klik Akseptasi Askred -> klik Analisa Debitur")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["a[title='ASKRED']", "//a[.//span[text()='Akseptasi Askred']]",
                          "//a[contains(text(),'Analisa Debitur')]"],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # ================================
            # TOMBOL TAMBAH DATA
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            create_button = page.locator('//a[@name="create-data"]')
            create_button.wait_for(state="visible")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Tambah Data")
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
            # pilih nama
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            select_combobox(page, "Tertanggung", "SEFI ANITA")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih Tertanggung")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.select.Tertanggung']//span[contains(@class,'select2-selection')]",
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # search nama debitur
            stepno += 1
            page.locator("button:has(i.glyphicon-search)").click()

            # row.click()
            page.locator('//*[@id="sigma.input.Kode"]').fill("YOG000708802")

            page.locator('//*[@id="btnCari"]').click()

            row = page.locator("//p[normalize-space()='YOG000708802']")

            row.wait_for(state="visible")
            row.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search dan pilih nama debitur")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//p[normalize-space()='YOG000708802']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.get_by_role("button", name="Pilih").click()
            # ================================
            # isi data pengajuan kredit
            # ================================

            stepno += 1
            select_combobox(page, "Product", "1401 - Kecil Program")
            select_combobox(page, "Jenis Kredit",
                            "A1 - Kredit Produk Investasi")
            select_combobox(page, "Sub Jenis Kredit", "A13 - KI Perluasan")

            # isi plafon kredit
            page.locator(
                "//input[@placeholder='Plafond Kredit']"
            ).type("100000000")

            select_combobox(page, "Cara Penarikan Kredit",
                            "Transaksi 1 Kali / Transaksional")

            today = datetime.today()
            date_from = today.replace(year=2025, month=12)

            # Desember (tanggal tetap hari ini)
            date_to = today.replace(month=12)

            # TANGGAL DARI (jangka waktu kredit)
            day_from = date_from.day
            month_from = date_from.strftime("%b")
            year_from = str(date_from.year)

            # Klik field "Dari"
            page.locator('//input[@placeholder="Dari"]').first.click()

            datepicker = page.locator(".ui-datepicker:visible")

            # Set tahun & bulan
            datepicker.locator(
                'select.ui-datepicker-year').select_option(year_from)
            datepicker.locator(
                'select.ui-datepicker-month').select_option(label=month_from)

            datepicker.locator(
                f'//td[@data-handler="selectDay" and normalize-space()="{day_from}"]').click()

            # TANGGAL Sampai (jangka waktu kredit)
            day_to = date_to.day
            month_to = date_to.strftime("%b")
            year_to = str(date_to.year)

            page.locator('//input[@placeholder="Sampai"]').first.click()

            datepicker = page.locator(".ui-datepicker:visible")

            datepicker.locator(
                'select.ui-datepicker-year').select_option(year_to)
            datepicker.locator(
                'select.ui-datepicker-month').select_option(label=month_to)

            datepicker.locator(
                f'//td[@data-handler="selectDay" and normalize-space()="{day_from}"]').click()

            select_combobox(page, "Jenis Plafond", "Aflopend")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi data pengajuan kredit")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//label[contains(text(),'Product')]/following::span[contains(@class,'select2-selection')][1]",
                          "//label[contains(text(),'Sub Jenis Kredit')]/following::span[contains(@class,'select2-selection')][1]",
                          "//label[normalize-space()='Cara Penarikan Kredit']/following::span[@role='combobox'][1]",
                          "//input[@placeholder='Plafond Kredit']",
                          "//input[@placeholder='Plafond Kredit']",
                          '//input[@placeholder="Dari"]',
                          '//input[@placeholder="Sampai"]',
                          ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # ================================
            # isi data pertanggungan
            # ================================
            stepno += 1
            select_combobox(page, "Pola Ganti Rugi", "PROPORSIONAL")

            page.locator("input[placeholder='Nilai Pertanggungan']:not([disabled])").type(
                "100000000")

            # isi coverage pertanggungan
            page.locator(
                "//input[@type='text' and contains(@id,'Coverage Kerugian')]").type("50")

            # set jangka waktu pertanggungan (dari)
            page.locator('//input[@placeholder="Dari"]').nth(1).click()

            dp = page.locator(".ui-datepicker:visible").last

            dp.locator('select.ui-datepicker-year').select_option(year_from)
            dp.locator(
                'select.ui-datepicker-month').select_option(label=month_from)

            dp.get_by_role("cell", name=str(day_from), exact=True).click()

            # sampai
            page.locator('//input[@placeholder="Sampai"]').nth(1).click()

            dp = page.locator(".ui-datepicker:visible").last

            dp.locator('select.ui-datepicker-year').select_option(year_to)
            dp.locator(
                'select.ui-datepicker-month').select_option(label=month_to)

            dp.get_by_role("cell", name=str(day_from), exact=True).click()

            # isi rate premi
            page.locator(
                "//input[@type='text' and contains(@id,'Rate Premi')]").type("1")

            page.locator(
                "//input[@type='text' and @placeholder='Min']").type("50000")

            page.locator(
                "//input[@type='text' and @placeholder='Max']").type("300000")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi data pertanggungan")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//label[contains(text(),'Pola Ganti Rugi')]/following::span[contains(@class,'select2-selection')][1]",
                    "input[placeholder='Nilai Pertanggungan']:not([disabled])",
                    "//input[@type='text' and contains(@id,'Coverage Kerugian')]",
                    "//input[@type='text' and contains(@id,'Rate Premi')]",
                    "//input[@type='text' and @placeholder='Min']",
                    "//input[@type='text' and @placeholder='Max']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            stepno += 1
            page.wait_for_selector(
                "//button[@type='button' and normalize-space()='Release']")
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button Release")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//button[@type='button' and normalize-space()='Release']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.locator(
                "//button[@type='button' and normalize-space()='Release']").click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # klik menu review analisa -> klik button tamdat lalu pilih COB dan TOC
            # ================================

            stepno += 1
            page.wait_for_load_state("networkidle")

            notif = page.locator('[id^="smallbox"]')
            notif.wait_for(state="visible")

            text = notif.inner_text()
            No_AN = get_No_AN(text)

            assert "Sukses" in text
            assert "Berhasil Rilis" in text

            stepno += 1
            # Pilih menu ASKRED
            page.wait_for_load_state("networkidle")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            # klik menu Analisa Debitur
            menu_analisa = page.locator(
                "//a[contains(text(),'Review Analisa')]")
            menu_analisa.wait_for(state="visible")
            menu_analisa.scroll_into_view_if_needed()
            menu_analisa.click()

            create_button = page.locator('//a[@name="create-data"]')
            create_button.wait_for(state="visible")
            create_button.click()

            select_combobox(page, "COB", "Asuransi Kredit")

            select_combobox(page, "TOC", "1400 - Askred")

            btn = page.locator("#submitModal")
            expect(btn).to_be_enabled()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik menu review analisa -> klik button tamdat lalu pilih COB dan TOC")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//span[contains(@class,'select2-selection--single') and .//span[normalize-space()='Asuransi Kredit']]",
                    "//span[contains(@class,'select2-selection--single') and .//span[normalize-space()='1400 - Askred']]",
                    "#submitModal"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            btn.click()
            # ================================
            # isi nama marketing dan no. nota penawaran
            # ================================
            select_combo(page, "Nama Marketing", "Dewi Gita")

            no_nota = generate_no_nota()
            page.locator('[id="sigma.input.No Nota Penawaran"]').fill(no_nota)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi nama marketing dan no. nota penawaran")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="sigma.input.No Nota Penawaran"]',
                    "//label[normalize-space()='Nama Marketing']/parent::*//span[@role='combobox']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

           # ================================
            # cari dan pilih nomor analisa
            # ================================
            page.locator(
                "//label[contains(text(),'No Analisa')]//following::button[contains(@class,'glyphicon-search')][1]").click()

            page.locator('//*[@id="sigma.input.Nomor Analisa"]').fill(No_AN)
            page.get_by_role("button", name="Cari").click()

            checkbox = page.locator(
                "datatable-row-wrapper input[type='checkbox']").first
            checkbox.wait_for()
            checkbox.click()

            page.wait_for_selector(
                "//button[.//i[contains(@class,'fa-check')] and contains(.,'Pilih')]")
            page.locator(
                "//button[.//i[contains(@class,'fa-check')] and contains(.,'Pilih')]").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : cari dan pilih nomor analisa")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="sigma.input.No Nota Penawaran"]',
                    '//datatable-row-wrapper//input[@type="checkbox"][1]',
                    "//button[.//i[contains(@class,'fa-check')] and contains(.,'Pilih')]"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # Add Daftar Product
            # ================================
            stepno += 1
            page.locator(
                '//*[@id="sigmangx.tambahbutton.columnsProduct"]').click()
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button tamdat/add daftar product")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//*[@id="sigmangx.tambahbutton.columnsProduct"]'
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            select_combo(page, "Mekanisme Penyaluran", "Langsung")
            select_combo(page, "Cara pembayaran Premi", "Sekaligus Dimuka")
            select_combo(page, "Mekanisme Refund Premi", "Kompensasi")
            select_combo(page, "Basis Refund Premi", "Net Premi")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi field mandatory pada daftar produk yang ditambahkan")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//label[normalize-space()='Mekanisme Penyaluran']/parent::*//span[@role='textbox']",
                    "//label[normalize-space()='Cara pembayaran Premi']/parent::*//span[@role='textbox']",
                    "//label[normalize-space()='Mekanisme Refund Premi']/parent::*//span[@role='textbox']",
                    "//label[normalize-space()='Basis Refund Premi']/parent::*//span[@role='textbox']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.get_by_role("button", name="Create").click()

            # ================================
            # isi product info
            # ================================
            fill_kode_produk_external(page)

            locator = page.locator(
                "//textarea[@id='sigma.textarea.Deskripsi Produk']")
            locator.wait_for(state="visible")
            locator.fill("Produk testing QA")

            select_combo(
                page, "Max Kolektibilitas Saat Pengajuan Pertanggungan", "5")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi product info")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//sa-select2[@id='sigma.select.Max Kolektibilitas Saat Pengajuan Pertanggungan']",
                    "input[placeholder='Kode Produk External']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # tambah daftar resiko
            # ================================
            stepno += 1
            daftar_risiko(page)

            page.locator('//*[@id="sigmangx.tambahbutton.columnsRes"]').click()

            select_combobox(page, "Nama Risiko", "Kredit Macet")
            select_combo(page, "Komponen Kerugian Yang di Tanggung",
                         "Pokok + Bunga + Denda")
            select_combo(
                page, "Minimum Kolektibilitas (saat pengajuan klaim)", "5")

            modal = page.locator(".modal:visible")

            btn = modal.locator("button.moveall")
            btn.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Tambah Daftar Risiko lalu klik Simpan")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//label[text()='Nama Risiko']/following::span[contains(@class,'select2-selection')][1]",
                    "//label[text()='Minimum Kolektibilitas (saat pengajuan klaim)']/following::span[contains(@class,'select2-selection')][1]",
                    "//label[text()='Komponen Kerugian Yang di Tanggung']/following::span[contains(@class,'select2-selection')][1]",
                    "#bootstrap-duallistbox-selected-list_dualListBoxComponent option"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            page.get_by_role("button", name="Simpan").click()
            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # isi ketentuan pertanggungan
            # ================================
            stepno += 1
            ketentuan_pertanggungan(page)

            field = page.locator(
                "//input[@id='inputNumeric.Toleransi Jangka Waktu']")
            field.wait_for(state="visible")
            field.click()
            field.fill("15")

            field = page.locator(
                "//input[@id='sigma.percentage.(%) Kompensasi Premi']")

            field.wait_for(state="visible")

            field.click()
            field.fill("70")
            field.press("Tab")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : pilih menu ketentuan pertanggungan dan isi field mandatory")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[@id='inputNumeric.Toleransi Jangka Waktu']",
                    "//input[@id='sigma.percentage.(%) Kompensasi Premi']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # isi biaya pertanggungan
            # ================================
            stepno += 1
            biaya_pertanggungan(page)

            ensure_toggle_on(page, "sigma.checkbox.isUnlimitedRatePremi")
            ensure_toggle_on(page, "sigma.checkbox.isUnlimitedCoverage")
            ensure_toggle_on(page, "sigma.checkbox.isUnlimitedCoverageLoss")

            page.keyboard.press("Escape")

            combo = page.locator("label:has-text('Proportional Round Up')") \
                .locator("xpath=following::span[contains(@class,'select2-selection')][1]")

            combo.click(force=True)

            page.locator(".select2-results__option",
                         has_text="Bulan").first.click()

            page.wait_for_selector(
                "//input[@id='inputNumeric.Proportional Round Up']")
            page.locator(
                "//input[@id='inputNumeric.Proportional Round Up']").fill("12")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik menu biaya pertanggungan lalu isi field mandatory")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[@id='inputNumeric.Proportional Round Up']",
                    "//input[@id='sigma.percentage.(%) Kompensasi Premi']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            # ================================
            # isi biaya lain
            # ================================
            stepno += 1
            biaya_lain(page)

            field = page.locator("//input[contains(@id,'Endorsement Fee')]")
            field.wait_for(state="visible")

            field.click()
            field.type("50000")
            field.press("Tab")

            field = page.locator("//input[contains(@id,'Biaya Materai')]")
            field.wait_for(state="visible")

            field.click()
            field.type("10000")

            page.locator(
                "//button[@type='button' and normalize-space()='Save']").click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik menu biaya lain lalu isi endorsement fee dan biaya materai")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[contains(@id,'Endorsement Fee')]",
                    "//input[contains(@id,'Biaya Materai')]"
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
            # isi document attachment list
            # ================================
            stepno += 1
            page.locator("//button[@id='sigma.docAttach.btn.']").click()

            file_path = Path(__file__).resolve(
            ).parents[3] / "Automation_DataAccess" / "logo_askrindo.png"

            assert file_path.exists(), f"File tidak ditemukan: {file_path}"

            page.locator(
                "//input[@id='file.']").set_input_files(str(file_path))

            ensure_toggle_on(page, "sigma.checkbox.isDocumentCompletedModal")
            upload_btn = page.locator(
                "//button[.//span[normalize-space()='Upload']]")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button tamdat dan upload dokumen attachment list")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[@placeholder='Include some files']",
                    "//button[.//span[normalize-space()='Upload']]"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            upload_btn.click()

            # isi disposisi/kesimpulan
            stepno += 1

            textarea = page.locator(
                "[id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']")
            textarea.fill("Draft")
            textarea.blur()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi disposisi/kesimpulan lalu klik button SAVE")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//button[contains(@class,'workflow-btn') and normalize-space()='SAVE']",
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']"
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            save_btn = page.locator("//button[normalize-space()='SAVE']").first

            print("enabled:", save_btn.is_enabled())

            save_btn.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # klik send to UW muda
            # ================================
            stepno += 1

            page.wait_for_selector(
                '//button[normalize-space()="Send To UW Muda"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button Send To UW Muda")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    '//button[normalize-space()="Send To UW Muda"]'
                ],

                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))

            page.locator(
                '//button[normalize-space()="Send To UW Muda"]').click()

            # pilih approval list Vira Miranda P
            stepno += 1
            nama = "Vira Miranda P"

            row = page.locator(f'''
            //div[@class="modal-body"]
            //datatable-row-wrapper[.//div[contains(.,"{nama}")]]
            ''')

            row.wait_for(state="visible")
            row.click()

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : pilih approval list")
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
            # LOGIN uw muda
            # ================================

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["uservira"]["username"], accounts["uservira"]["password"])
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
            # cari no. dokumen/no nota
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').last

            notif.wait_for(state="visible")
            notif.click()

            page.locator('//*[@id="activity"]').click()

            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            # search no nota
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(no_nota)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{no_nota}"]')

            cell.wait_for(state="visible", timeout=10000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. Nota")
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
                f'//tr[.//td[normalize-space()="{no_nota}"]]')
            row.click()

            # ================================
            # klik send to udw madya
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("reviewed")

            page.wait_for_selector(
                '//button[normalize-space()="Send To Udw Madya"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button send to Udw Madya")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="Send To Udw Madya"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.locator(
                '//button[normalize-space()="Send To Udw Madya"]').click()

            # ================================
            # pilih approval list 2
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            # pilih approval list udw madya
            nama = "Vira Miranda P"

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

            stepno += 1
            page.wait_for_selector(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]')
            page.locator(
                '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]').click()

            # isi ke field
            input_nota = page.locator("//input[@id='idNoNota']")

            input_nota.wait_for(state="visible")
            input_nota.fill(no_nota)

            page.wait_for_selector(
                '//button[@id="searchBtn" and contains(@class,"btn-primary")]')
            page.locator(
                '//button[@id="searchBtn" and contains(@class,"btn-primary")]').click()

            page.wait_for_selector('#closeBtn')
            page.locator('#closeBtn').click()

            # biar gk turun
            page.locator('//h1').scroll_into_view_if_needed()

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{no_nota}"]')

            cell.wait_for(state="visible", timeout=50000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : cek data yang berhasil dikirim di activity list"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[@id='idNoNota']",
                    '//button[contains(@class,"dropdown-toggle") and @data-toggle="dropdown"]',
                    '//input[@type="search" and @aria-controls="dt_basic"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            cell.click()

            # ================================
            # klik send to udw utama
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("reviewed")

            page.wait_for_selector(
                '//button[normalize-space()="Send To Udw Utama"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button send to UDW Utama")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="Send To Udw Utama"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.locator(
                '//button[normalize-space()="Send To Udw Utama"]').click()

            # ================================
            # pilih approval list udw utama
            # ================================

            stepno += 1
            page.wait_for_load_state("networkidle")
            # pilih approval list udw madya
            nama = "Super Pusat Dua"

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
                f"[Test_Step_{stepno}] : pilih approval list Super Pusat Dua (Send to UDW UTAMA)")
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
            notif = page.locator('[id^="smallbox"]').last

            notif.wait_for(state="visible")
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
            # LOGIN superpusat2
            # ================================
            page.wait_for_load_state("networkidle")
            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["usersp2"]["username"], accounts["usersp2"]["password"])
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

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').last

            notif.wait_for(state="visible")
            notif.click()

            # ================================
            # cari no. dokumen/no nota
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator('//*[@id="activity"]').click()

            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            # search no nota
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(no_nota)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{no_nota}"]')

            cell.wait_for(state="visible", timeout=10000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. nota yang berhasil dikirim di activity list")
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
                f'//tr[.//td[normalize-space()="{no_nota}"]]')
            row.click()

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

            page.locator('//button[normalize-space()="Approve"]').click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            notif = page.locator('[id^="smallbox"]').last
            notif.wait_for(state="visible", timeout=5000)

            notif_text = notif.inner_text()
            print("NOTIF:", notif_text)
            assert "berhasil diproses" in notif_text.lower(), "Approve tidak sukses"

            page.wait_for_timeout(2000)

            # ================================
            # GUARD SESSION
            # ================================
            if "login" in page.url:
                raise Exception("Session drop setelah approve")

            # kasih waktu UI commit
            page.wait_for_timeout(2000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # LOGIN user utama
            # ================================
            page.context.clear_cookies()
            page.goto(get_base_url())

            accounts = load_accounts()
            login_page = LoginPage(page)
            login_page.login(
                accounts["userutama"]["username"], accounts["userutama"]["password"])
            page.wait_for_selector("#form-login > button")

            page.locator("#form-login > button").click()

            page.wait_for_timeout(5000)

            # =================================
            # HANDLE FORCE LOGIN (Optional)
            # ================================

            force_login_btn = page.get_by_role("button", name="Force Login")
            if force_login_btn.count() > 0 and force_login_btn.is_visible():
                force_login_btn.click()
                page.wait_for_timeout(3000)  # ⬅ delay 3 detik

            # ================================
            # cari no. dokumen/no nota
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator('//*[@id="activity"]').click()

            page.wait_for_selector('//button[@title="See Details"]')
            page.locator('//button[@title="See Details"]').click()

            # search no nota
            search = page.locator(
                '//input[@type="search" and @aria-controls="dt_basic"]')
            search.fill(no_nota)
            search.press("Enter")

            # tunggu data muncul setelah search
            cell = page.locator(f'//td[normalize-space()="{no_nota}"]')

            cell.wait_for(state="visible", timeout=10000)

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : search no. nota yang berhasil dikirim di activity list")
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
                f'//tr[.//td[normalize-space()="{no_nota}"]]')
            row.click()

            # isi tgl konfirmasi
            stepno += 1
            textarea = page.locator(
                "[id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']")
            textarea.fill("Draft")
            textarea.blur()

            save_btn = page.locator("//button[normalize-space()='SAVE']").first

            print("enabled:", save_btn.is_enabled())

            save_btn.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()
            day = str(datetime.now().day)

            field = page.locator(
                "//input[@placeholder='Tgl Terima Konfirmasi']")
            field.click()

            page.wait_for_timeout(2000)

            page.locator(
                f"//td[normalize-space()='{day}' and not(contains(@class,'old')) and not(contains(@class,'new'))]"
            ).first.click()

            select_combo(page, "Hasil Konfirmasi", "Setuju")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : isi tanggal dan hasil konfirmasi")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//input[@placeholder='Tgl Terima Konfirmasi']",
                    "//sa-select2[@id='sigma.select.Hasil Konfirmasi']//span[contains(@class,'select2-selection__rendered')]"
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            # ================================
            # klik save
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")

            page.locator(
                "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']").fill("Confirmed")

            page.wait_for_selector('//button[normalize-space()="SAVE"]')

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : klik button SAVE")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//*[@id='sigma.textarea.Analisa/Saran/Disposisi/Kesimpulan']",
                    '//button[normalize-space()="SAVE"]'
                ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name
            ))
            page.wait_for_timeout(5000)
            page.locator('//button[normalize-space()="SAVE"]').click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # tutup semua notif (kalau ada lebih dari satu)
            notif = page.locator('[id^="smallbox"]').last

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
            # LOGIN Teamsupport untuk cek blacklist debitur
            # ================================
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

            search.fill("YOG000708802")
            search.press("Enter")

            row = page.locator("#dt_basic tbody tr", has_text="SUDARTI").first

            expect(row).to_be_visible(timeout=50000)
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

            page.locator('//*[@id="sigma.textarea.Catatan"]').fill("Catatan")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Insert Registrasi dan Isi semua Mandatory Field"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//*[@id="sigma.input.Nomor Register"]',
                          '//*[@id="sigma.input.Nomor Surat Pengantar"]',
                          '//*[@id="sigma.input.Nomor DJP"]',
                          '//*[@id="sigma.textarea.Catatan"]',
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))

            stepno += 1
            # cari no nota
            page.locator("//button[@id='lookupNotaButton']").click()

            # isi field
            field = page.locator("//input[@id='sigma.input.Nomor NP']")
            field.wait_for(state="visible")
            field.fill(no_nota)

            modal = page.locator(
                ".modal:has-text('Pop Up Nota Penawaran')").last
            modal.wait_for(state="visible")

            modal.locator("button:has-text('Cari'):visible").click()

            # tunggu row muncul
            row = page.locator("datatable-row-wrapper", has_text=no_nota).first
            row.wait_for(state="visible", timeout=10000)

            checkbox = row.locator("input[type='checkbox']")
            checkbox.click()

            modal = page.locator(
                ".modal:has-text('Pop Up Nota Penawaran')").last

            btn_pilih = modal.locator("button:has-text('Pilih'):visible").first

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input dan cari Nota Penawaran lalu klik Pilih"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//button[@id='lookupNotaButton']",
                          "//input[@id='sigma.input.Nomor NP']",
                          '//*[@id="btnCari"]',
                          '//button[contains(@class,"btn btn-primary pull-right") and normalize-space()="Pilih"]'
                          ],
                highlight=True,
                base_name=f"step_{stepno}",
                testcase_id=testcase_id,
                testcase_name=testcase_name

            ))
            btn_pilih.click()

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

            page.locator('//input[@placeholder="Dari"]').nth(0).click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_from)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_from)

            page.locator(f'//td[normalize-space()="{day_from}"]').click()

            # TANGGAL SAMPAI
            day_to = date_to.day
            month_to = date_to.strftime("%b")
            year_to = str(date_to.year)

            page.locator('//input[@placeholder="Sampai"]').nth(0).click()

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
                selector=['//input[@placeholder="periode"]',
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

            select_combobox(page, "Product Nota Penawaran",
                            "A13 - KI Perluasan")

            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik button REALISASI dan Pilih Produk"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=['//button[normalize-space()="REALISASI"]',
                          "//sa-select2[@id='sigma.select.Product Nota Penawaran']//span[contains(@class,'select2-selection__rendered')]",
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
            # isi dan lengkapi Akseptasi Detail pada menu objek pertanggungan
            # ================================
            stepno += 1
            page.wait_for_load_state("networkidle")
            page.wait_for_selector(
                "//li[@data-name='askred-objek-pertanggungan']")
            page.locator(
                "//li[@data-name='askred-objek-pertanggungan']").click()

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

            # TANGGAL DARI (jangka waktu kredit)
            day_from = date_from.day
            month_from = date_from.strftime("%b")
            year_from = str(date_from.year)

            page.locator('//input[@placeholder="Dari"]').nth(0).click()

            page.locator(
                '//select[contains(@class,"year")]').select_option(year_from)
            page.locator(
                '//select[contains(@class,"month")]').select_option(label=month_from)

            page.locator(f'//td[normalize-space()="{day_from}"]').click()

            # TANGGAL SAMPAI (jangka waktu kredit)
            day_to = date_to.day
            month_to = date_to.strftime("%b")
            year_to = str(date_to.year)

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

            # ambil request number
            request_number = get_request_number_from_notif(page)

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
            notif = page.locator('[id^="smallbox"]').last

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
            notif = page.locator('[id^="smallbox"]').last

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

            notif = page.locator('[id^="smallbox"]').last
            notif.wait_for(state="visible", timeout=5000)

            notif_text = notif.inner_text()
            print("NOTIF:", notif_text)
            assert "berhasil diproses" in notif_text.lower(), "Approve tidak sukses"

            page.wait_for_timeout(2000)

            # ================================
            # GUARD SESSION
            # ================================
            if "login" in page.url:
                raise Exception("Session drop setelah approve")

            # kasih waktu UI commit
            page.wait_for_timeout(2000)

            # klik logout
            logout.scroll_into_view_if_needed()
            logout.click()

            page.wait_for_selector(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]")
            page.locator(
                "//div[contains(@class,'MessageBoxButtonSection')]//button[2]").click()

            # ================================
            # LOGIN user utama
            # ================================
            page.context.clear_cookies()
            page.goto(get_base_url())

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
                "No AN": No_AN,
                "No Request": request_number
                }
        })

    finally:
        try:
            # =========================
            # PDF ONLY FOR PARENT
            # =========================
            final_actual_result = actual_result.format(
                request_number=request_number or "-",
                polis=polis or "-",
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
                        "No AN": No_AN,
                        "No Request": request_number
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
            "No AN": No_AN,
            "No Request": request_number
        }
    }


def test_run_RegistrasiDJP_NotaPenawaran():
    run_RegisDJP_NotaPenawaran()


if __name__ == "__main__":
    run_RegisDJP_NotaPenawaran()  # ini jalan kalo runningnya pakai pyhton bukan pytest
