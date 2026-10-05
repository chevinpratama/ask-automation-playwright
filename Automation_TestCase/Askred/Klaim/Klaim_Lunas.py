from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.data_loader import load_accounts, get_base_url, get_alt_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from datetime import datetime
from Automation_TestCase.Askred.Akseptasi import Akseptasi_RegistrasiDJP
import fpdf
import traceback
import sys
import re
import pytest
from Automation_QAMap.qamap_client import record_step

# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Klaim_Lunas"]
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

    dropdown = page.locator(f"#select2-{component_id}-container")

    dropdown.click()

    page.wait_for_selector(".select2-container--open")

    search = page.locator(".select2-container--open .select2-search__field")

    if search.count() > 0:
        search.fill(value)

    page.wait_for_selector(".select2-results__option")

    option = page.locator(
        ".select2-container--open .select2-results__option",
        has_text=value
    ).first

    option.click()

    return dropdown


def zk_combobox(page, locator, value):
    combo = page.locator(locator)

    # buka dropdown
    combo.click()

    # tunggu dropdown muncul
    dropdown = page.locator(".z-combobox-popup:visible")
    dropdown.wait_for(state="visible", timeout=3000)

    # pilih option
    option = dropdown.locator(f".z-comboitem-text:has-text('{value}')")
    option.wait_for(state="visible", timeout=5000)

    option.click()

    return combo


def run_Registrasi_Klaim_Lunas(generate_pdf=True, polis=None):
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None  # inisialisasi
    execution_time = datetime.now().strftime("%d/%m/%Y")

    if not polis:
        print("="*50)
        print("🔄 START Case - Akseptasi Polis sedang berjalan")
        print("="*50)

        akseptasi = Akseptasi_RegistrasiDJP.run_RegisDJP(generate_pdf=False)
        polis = akseptasi.get("polis")
        print("POLIS DARI DJP:", polis)

        print("="*50)
        print(f"✅ END Case - Akseptasi Polis Selesai. No Polis: {polis}")
        print("="*50)

    # ⬇️ INI SELALU JALAN (baik dari parent maupun dari DJP)
    print("="*50)
    print("🔄 START Case - Klaim Disetujui sedang berjalan")
    print("="*50)
    print(f"♻️ Menggunakan polis: {polis}")
    print("="*50)

    tanggal_terima_surat = "01/01/2026"
    tanggal_kejadian = "01/01/2026"
    nilai_tuntutan_claim = "10000000"
    disposisi1 = "Harap di Analisa kembali"
    total_kerugian_tertanggung = "10000000"
    tanggal_terjadi_penyebab_klaim = "01/01/2026"
    nilai_pokok = "10000000"
    nilai_bunga = "0"
    nilai_denda = "0"
    disposisi2 = "Harap diproses"
    disposisi3 = "Klaim di Approve"
    accounts = load_accounts()
    user_staff_kemayoran_fms_uat = accounts["fms_staff_kemayoran"]["username"]
    pass_staff_kemayoran_fms_uat = accounts["fms_staff_kemayoran"]["password"]
    user_kasie_kemayoran_fms_uat = accounts["fms_kasie_kemayoran"]["username"]
    pass_kasie_kemayoran_fms_uat = accounts["fms_kasie_kemayoran"]["password"]
    user_kabag_kemayoran_fms_uat = accounts["fms_kabag_kemayoran"]["username"]
    pass_kabag_kemayoran_fms_uat = accounts["fms_kabag_kemayoran"]["password"]
    database_verifications = []

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

            # Klik submenu Klaim Askred
            klaim_askred = page.locator('//span[text()="Klaim Askred"]')
            klaim_askred.wait_for(state="visible")
            klaim_askred.click()

            # Klik Registrasi Klaim
            registrasi_klaim = page.locator(
                "a[href='#/home/askrindo/askred/claim-registration']")
            registrasi_klaim.wait_for(state="visible")
            registrasi_klaim.click()
            page.wait_for_timeout(5000)  # ⬅ delay 5 detik
            # tombol Home biasanya langsung ke atas
            # page.keyboard.press("Home")
            tambah_button = page.locator("a[name='create-data']")
            tambah_button.wait_for()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred -> Klaim Askred -> Klaim Registration lalu Klik tombol Tambah"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    askred_menu,
                    klaim_askred,
                    registrasi_klaim,
                    tambah_button
                ],
                highlight=True
            ))
            tambah_button.click()

            page.wait_for_timeout(5000)
            page.keyboard.press("Home")
            # -----------------------------------------------------------------------------------------3

            # Form Registrasi Klaim
            page.fill(
                "input[disableselector='sigma.datepicker.Tanggal Terima Surat']", tanggal_terima_surat)
            page.click("#lookupPolicyNoButton")
            page.wait_for_timeout(2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Tanggal Terima Surat lalu Klik Tombol Cari Polis"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "input[disableselector='sigma.datepicker.Tanggal Terima Surat']",
                    "#lookupPolicyNoButton"
                ],
                highlight=True
            ))
            # ----------------------------------------------------------------------------------------------#

            # Cari Polisnya
            page.wait_for_timeout(5000)
            input_no_polis = page.locator(
                "input[id='sigma.input.Nomor Polis']")
            input_no_polis.wait_for(state="visible")
            input_no_polis.fill(polis)

            # Klik tombol Cari
            cari_button = page.locator(
                "button.btn.btn-labeled.btn-primary:has-text('Cari')")
            cari_button.wait_for(state="visible")
            cari_button.click()

            # Pilih radio button pertama
            ditemukan_no_polis = page.locator(
                "datatable-body-row:nth-child(1) input[type=radio]")
            ditemukan_no_polis.wait_for(state="visible", timeout=60000)
            ditemukan_no_polis.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari Polis yang ingin di klaim lalu klik tombol pilih"
            )
            # Screenshot semua elemen penting
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    input_no_polis,
                    cari_button,
                    ditemukan_no_polis,
                    "xpath=//button[normalize-space()='Pilih']"
                ],
                highlight=True
            ))
            page.click("xpath=//button[normalize-space()='Pilih']")
            page.wait_for_timeout(3000)
            # ----------------------------------------------------------------------------------#

            # Tanggal Kejadian dan Nilai Tuntutan Claim
            page.click(
                "input[disableselector='sigma.datepicker.Tanggal Kejadian']")
            page.fill(
                "input[disableselector='sigma.datepicker.Tanggal Kejadian']", tanggal_kejadian)

            amount = page.locator(
                '//*[@id="sigma.numeric.sigma.currency.amount.amtEstimateId"]')
            amount.click()
            amount.type(nilai_tuntutan_claim, delay=100)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Tanggal Kejadian dan Nilai Tuntutan Claim"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    amount,
                    "input[disableselector='sigma.datepicker.Tanggal Kejadian']",
                ],
                highlight=True
            ))
            # ----------------------------------------------------------------------------------------#

            # Save Registasi
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.fill(
                "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']", disposisi1)
            saveregist_button = page.locator(
                "xpath=//button[normalize-space()='SAVE REGIS !!']")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Disposisi dan Klik Tombol Save Registrasi"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']",
                    saveregist_button
                ],
                highlight=True
            ))

            saveregist_button.click()
            konfirmasi = page.locator(
                "p.pText:has-text('Apakah anda yakin memproses dokumen ini?')")
            konfirmasi.wait_for(state="visible")
            page.locator("#bot2-Msg1").click()  # Ya
            # ---------------------------------------------------------------------------#

            # Get Message Box
            success_msg = page.locator(
                "p:has-text('berhasil diproses Registrasi NO')")
            success_msg.wait_for(state="visible")

            # Ambil teks lengkap
            full_text = success_msg.inner_text()
            print("Teks penuh:", full_text)

            match = re.search(r"NO\s*:\s*(\S+)", full_text)
            if match:
                no_registrasi = match.group(1)
                print("Nomor Registrasi:", no_registrasi)
            else:
                print("Nomor registrasi tidak ditemukan")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Simpan No Registrasi Klaimnya setelah klik tombol Save Registrasi"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    success_msg,
                ],
                highlight=True
            ))
            success_msg.click()
            # --------------------------------------------------------------------------------#

            # Kirim Ke Analyst
            page.wait_for_timeout(3000)
            kirimkeanalyst_button = page.locator(
                "//button[normalize-space()='KIRIM KE ANALYST']")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Setelah disimpan dan sudah didapatkan No Registrasinya, lalu klik Tombol Kirim Ke Analyst"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    kirimkeanalyst_button,
                ],
                highlight=True
            ))
            kirimkeanalyst_button.click()

            page.wait_for_timeout(5000)
            runggawarsito = page.get_by_text("Runggawarsito")
            ariyani = page.get_by_text("Ariyani")

            if runggawarsito.count() > 0:
                print("Teks 'Runggawarsito' ditemukan!")
                username_Runggawarsito = accounts["runggawarsito"]["username"]
                password_Runggawarsito = accounts["runggawarsito"]["password"]

                print(username_Runggawarsito)
                print(password_Runggawarsito)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Kirim ke User Analyst Runggawarsito"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=["text=Runggawarsito"],
                    highlight=True
                ))

                runggawarsito.first.click()

                konfirmasi_Runggawarsito = page.locator(
                    "p.pText:has-text('Anda yakin ingin mengirim dokumen ini ke user Runggawarsito ?')")
                konfirmasi_Runggawarsito.wait_for(
                    state="visible", timeout=5000)
                page.locator("#bot2-Msg1").click()  # Ya
                page.wait_for_timeout(3000)
                success_msg.click()

                signout_button = page.locator("a[title='Sign Out']")
                signout_button.wait_for(state="visible", timeout=2000)
                signout_button.click()

                konfirmasi_signout = page.locator(
                    "p.pText:has-text('You can improve your security further after logging out by closing this opened browser')")
                konfirmasi_signout.wait_for(state="visible", timeout=5000)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Setelah dikirim ke Analyst lalu Klik Tombol SignOut"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=[
                        signout_button,
                    ],
                    highlight=True
                ))
                page.locator("#bot2-Msg1").click()  # Yes
                page.wait_for_timeout(3000)

                page.fill("#name", username_Runggawarsito)
                page.fill("#password", password_Runggawarsito)
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
                force_login_btn = page.get_by_role(
                    "button", name="Force Login")
                if force_login_btn.count() > 0 and force_login_btn.is_visible():
                    force_login_btn.click()
                    page.wait_for_timeout(5000)  # ⬅ delay 5 detik

            elif ariyani.count() > 0:
                print("Teks 'Ariyani' ditemukan!")

                username_Ariyani = accounts["ariyani"]["username"]
                password_Ariyani = accounts["ariyani"]["password"]

                print(username_Ariyani)
                print(password_Ariyani)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Kirim ke User Analyst Ariyani"
                )

                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=["text=Ariyani"],
                    highlight=True
                ))

                ariyani.first.click()

                konfirmasi_Ariyani = page.locator(
                    "p.pText:has-text('Anda yakin ingin mengirim dokumen ini ke user Ariyani ?')")
                konfirmasi_Ariyani.wait_for(
                    state="visible", timeout=5000)
                page.locator("#bot2-Msg1").click()  # Ya
                page.wait_for_timeout(3000)
                success_msg.click()

                signout_button = page.locator("a[title='Sign Out']")
                signout_button.wait_for(state="visible", timeout=2000)
                signout_button.click()

                konfirmasi_signout = page.locator(
                    "p.pText:has-text('You can improve your security further after logging out by closing this opened browser')")
                konfirmasi_signout.wait_for(state="visible", timeout=5000)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Setelah dikirim ke Analyst lalu Klik Tombol SignOut"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=[
                        signout_button,
                    ],
                    highlight=True
                ))
                page.locator("#bot2-Msg1").click()  # Yes

                page.wait_for_timeout(3000)

                page.fill("#name", username_Ariyani)
                page.fill("#password", password_Ariyani)
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
                force_login_btn = page.get_by_role(
                    "button", name="Force Login")
                if force_login_btn.count() > 0 and force_login_btn.is_visible():
                    force_login_btn.click()
                    page.wait_for_timeout(5000)  # ⬅ delay 5 detik

            # ------------------------------------------------------------------------------------------------------#
            # Tasklist
            activity = page.locator("#activity")
            activity.wait_for(state="visible", timeout=5000)
            activity.click()
            page.wait_for_timeout(3000)

            details = page.locator("//button[@title='See Details']")
            details.wait_for(state="visible", timeout=5000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Activity lalu klik tombol details")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    activity,
                    details],
                highlight=True
            ))
            details.click()

            # Tasklist Detail
            tasklist_dateil = page.locator("#dt_basic_filter > label > input")
            tasklist_dateil.wait_for(state="visible", timeout=5000)
            tasklist_dateil.fill(no_registrasi)

            page.click("//*[@id='dt_basic_filter']/label/span")

            status_registered = page.locator("//td[text()='Registered']")
            status_registered.wait_for(state="visible", timeout=15000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari No Klaim di Tasklist lalu Klik klaim tersebut")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    tasklist_dateil,
                    "//*[@id='dt_basic_filter']/label/span",
                    status_registered
                ],
                highlight=True
            ))
            status_registered.click()

            # Form Analis
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            analis_claim_button = page.locator("#analis")
            analis_claim_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Analis Claim")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    analis_claim_button,
                ],
                highlight=True
            ))
            analis_claim_button.click()

            kerugian_tertanggung = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.toTtertanggungId']")
            kerugian_tertanggung.wait_for(state="visible", timeout=3000)
            kerugian_tertanggung.type(total_kerugian_tertanggung, delay=100)
            kerugian_tertanggung.press("Tab")

            page.locator(
                "//label[contains(text(),'Kolektibilitas Saat Pengajuan Klaim')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(
                "//li[contains(@class,'select2-results__option') and contains(text(),'5')]").click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Total Kerugian Tertanggung dan Kolektibilitas saat pengajuan klaim")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    kerugian_tertanggung,
                    "//label[contains(text(),'Kolektibilitas Saat Pengajuan Klaim')]/following::span[contains(@class,'select2-selection')][1]"
                ],
                highlight=True
            ))

            # Peyebab Klaim
            page.locator(
                "//label[contains(text(),'Resiko yang di Claim')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="Kredit Macet").click()

            page.locator(
                "//label[contains(text(),'Type Penyebab Claim')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="terjamin beritikad tidak baik").click()

            tgl_terjadi_penyebab_klaim = page.locator(
                'input[placeholder="Tgl Terjadinya Penyebab Claim"]')
            tgl_terjadi_penyebab_klaim.wait_for(state="visible", timeout=5000)
            tgl_terjadi_penyebab_klaim.fill(tanggal_terjadi_penyebab_klaim)

            page.locator(
                "//label[contains(text(),'Kode Pos')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="10110 - Gambir, Gambir, Jakarta Pusat, D.K.I Jakarta").click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Penyebab Klaim")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//label[contains(text(),'Resiko yang di Claim')]/following::span[contains(@class,'select2-selection')][1]",
                          "//label[contains(text(),'Type Penyebab Claim')]/following::span[contains(@class,'select2-selection')][1]",
                          tgl_terjadi_penyebab_klaim,
                          "//label[contains(text(),'Kode Pos')]/following::span[contains(@class,'select2-selection')][1]"
                          ],
                highlight=True
            ))

            bank_penerima = page.locator(
                "//input[@id='sigma.input.Bank Penerima']")
            bank_penerima.wait_for(state="visible", timeout=2000)
            bank_penerima.fill("Mandiri")

            validasi_analisa_button = page.locator("#valanalis")
            validasi_analisa_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Bank Penerima lalu klik tombol Validasi Analis")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    bank_penerima,
                    validasi_analisa_button
                ],
                highlight=True
            ))

            validasi_analisa_button.click()

            page.locator(
                "//label[contains(text(),'Kesimpulan')]/following::span[contains(@class,'select2-selection')][1]").first.click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="Klaim Dibayar").click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih Kesimpulan Klaim Dibayar")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["//label[contains(text(),'Kesimpulan')]/following::span[contains(@class,'select2-selection')][1]"
                          ],
                highlight=True
            ))

            # Kerugian menurut Askrindo
            pokok = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.pokokId']")
            pokok.wait_for(state="visible", timeout=1000)
            pokok.type(nilai_pokok, delay=100)
            pokok.press("Tab")

            bunga = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.bungaId']")
            bunga.wait_for(state="visible", timeout=1000)
            bunga.type(nilai_bunga, delay=100)
            bunga.press("Tab")

            denda = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.dendaId']")
            denda.wait_for(state="visible", timeout=1000)
            denda.type(nilai_denda, delay=100)
            denda.press("Tab")

            pembayaran = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentCurrentId']")
            pembayaran1 = pembayaran.input_value()
            print(pembayaran1)

            # Kerugian menurut Askrindo
            page.wait_for_timeout(2000)
            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Kerugian menurut Askrindo")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    pokok,
                    bunga,
                    denda,
                    pembayaran
                ],
                highlight=True
            ))

            page.fill(
                "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']", disposisi2)
            procced_button = page.locator(
                "//button[normalize-space()='PROCEED BAYAR']")
            procced_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Disposisi lalu klik Tombol Procced Bayar")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']",
                          procced_button
                          ],
                highlight=True
            ))
            procced_button.click()

            page.wait_for_timeout(5000)

            vanessa = page.get_by_text("Vanessa")
            sari = page.get_by_text("Sari Kusuma Ningrum")

            if vanessa.count() > 0:
                print("Teks 'vanessa' ditemukan!")
                username_vanessa = accounts["vanessa"]["username"]
                password_vanessa = accounts["vanessa"]["password"]

                print(username_vanessa)
                print(password_vanessa)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Kirim ke User untuk procced bayar"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=["text=Vanessa"],
                    highlight=True
                ))

                vanessa.first.click()

                konfirmasi_vanessa = page.locator(
                    "p.pText:has-text('Anda yakin ingin mengirim dokumen ini ke user Vanessa ?')")
                konfirmasi_vanessa.wait_for(
                    state="visible", timeout=5000)
                page.locator("#bot2-Msg1").click()  # Ya
                page.wait_for_timeout(3000)
                success_msg.click()

                signout_button = page.locator("a[title='Sign Out']")
                signout_button.wait_for(state="visible", timeout=2000)
                signout_button.click()

                konfirmasi_signout = page.locator(
                    "p.pText:has-text('You can improve your security further after logging out by closing this opened browser')")
                konfirmasi_signout.wait_for(state="visible", timeout=5000)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Setelah dikirim ke Analyst lalu Klik Tombol SignOut"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=[
                        signout_button,
                    ],
                    highlight=True
                ))
                page.locator("#bot2-Msg1").click()  # Yes
                page.wait_for_timeout(3000)

                page.fill("#name", username_vanessa)
                page.fill("#password", password_vanessa)
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
                force_login_btn = page.get_by_role(
                    "button", name="Force Login")
                if force_login_btn.count() > 0 and force_login_btn.is_visible():
                    force_login_btn.click()
                    page.wait_for_timeout(5000)  # ⬅ delay 5 detik

            elif sari.count() > 0:
                print("Teks 'Sari Kusumna Ningrum' ditemukan!")

                username_sari = accounts["sari"]["username"]
                password_sari = accounts["sari"]["password"]

                print(username_sari)
                print(password_sari)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Kirim ke User untuk Procced Bayar "
                )

                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=["text=Sari Kusuma Ningrum"],
                    highlight=True
                ))

                sari.first.click()

                konfirmasi_sari = page.locator(
                    "p.pText:has-text('Anda yakin ingin mengirim dokumen ini ke user Sari Kusuma Ningrum ?')")
                konfirmasi_sari.wait_for(
                    state="visible", timeout=5000)
                page.locator("#bot2-Msg1").click()  # Ya
                page.wait_for_timeout(3000)
                success_msg.click()

                signout_button = page.locator("a[title='Sign Out']")
                signout_button.wait_for(state="visible", timeout=2000)
                signout_button.click()

                konfirmasi_signout = page.locator(
                    "p.pText:has-text('You can improve your security further after logging out by closing this opened browser')")
                konfirmasi_signout.wait_for(state="visible", timeout=5000)

                stepno += 1
                test_steps_rendered.append(
                    f"[Test_Step_{stepno}] : Setelah dikirim ke Analyst lalu Klik Tombol SignOut"
                )
                screenshots_rendered.append(save_screenshot(
                    page=page,
                    selector=[
                        signout_button,
                    ],
                    highlight=True
                ))
                page.locator("#bot2-Msg1").click()  # Yes

                page.wait_for_timeout(3000)

                page.fill("#name", username_sari)
                page.fill("#password", password_sari)
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
                force_login_btn = page.get_by_role(
                    "button", name="Force Login")
                if force_login_btn.count() > 0 and force_login_btn.is_visible():
                    force_login_btn.click()
                    page.wait_for_timeout(5000)  # ⬅ delay 5 detik

            # ------------------------------------------------------------------------------------------------------#
            # Tasklist
            activity = page.locator("#activity")
            activity.wait_for(state="visible", timeout=3000)
            activity.click()
            page.wait_for_timeout(3000)

            details = page.locator("//button[@title='See Details']")
            details.wait_for(state="visible", timeout=3000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Activity lalu klik tombol details")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    activity,
                    details
                ],
                highlight=True
            ))
            details.click()

            # Tasklist Detail
            tasklist_dateil = page.locator("#dt_basic_filter > label > input")
            tasklist_dateil.wait_for(state="visible", timeout=3000)
            tasklist_dateil.fill(no_registrasi)

            page.click("//*[@id='dt_basic_filter']/label/span")

            status_approval_kasie_cab = page.locator(
                "//td[text()='Approval Kepala Seksi Cabang']")
            status_approval_kasie_cab.wait_for(state="visible", timeout=15000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari Klaim tersebut di Tasklist lalu klik klaim tersebut")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[tasklist_dateil,
                          "//*[@id='dt_basic_filter']/label/span",
                          status_approval_kasie_cab
                          ],
                highlight=True
            ))
            status_approval_kasie_cab.click()

            # Form Analis
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            analis_claim_button = page.locator("#analis")
            analis_claim_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Analis Claim")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    analis_claim_button
                ],
                highlight=True
            ))
            analis_claim_button.click()

            page.wait_for_load_state("networkidle")

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.fill(
                "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']", disposisi3)
            approve_button = page.locator(
                "xpath=//button[normalize-space()='Approve']")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Disposisi dan Klik Tombol Approve"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']",
                    approve_button
                ],
                highlight=True
            ))

            approve_button.click()
            konfirmasi = page.locator(
                "p.pText:has-text('Apakah anda yakin memproses dokumen ini?')")
            konfirmasi.wait_for(state="visible", timeout=5000)
            page.locator("#bot2-Msg1").click()  # Ya

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            success_msg.click()

            # Cek data Klaimnya
            cari_klaim_approve = page.locator(
                "input[type='search'][aria-controls='dt_basic']")
            cari_klaim_approve.wait_for(state="visible", timeout=2000)
            cari_klaim_approve.fill(no_registrasi)
            page.wait_for_timeout(2000)

            page.locator(".input-group-addon .glyphicon-search").click()

            klaimdisetujui = page.locator(
                "td.class-data", has_text="Setuju/Approved")
            klaimdisetujui.wait_for(state="visible", timeout=10000)

            no_lpk_locator = page.locator(
                '//*[@id="dt_basic"]/tbody/tr[1]/td[11]')
            no_lpk_locator.wait_for(state="visible", timeout=5000)
            no_lpk = no_lpk_locator.inner_text()
            print("No LPK:", no_lpk)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari data klaim yang telah disetujui dan status doc Setuju/Approve"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    cari_klaim_approve,
                    ".input-group-addon .glyphicon-search",
                    klaimdisetujui,
                    no_lpk_locator
                ],
                highlight=True
            ))
            klaimdisetujui.click()

            page.wait_for_timeout(5000)

            nomor_nota_field = page.locator(
                "xpath=//input[@id='sigma.input.Nomor Nota']")
            nomor_nota = nomor_nota_field.input_value()

            print(nomor_nota)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Simpan No Notanya untuk dilakukan perlunasan di FMS"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    nomor_nota_field
                ],
                highlight=True
            ))

            # ------------------------------------------------------------------------------------------#
            # Pindah Tab ke FMS UAT untuk dilakukan perlunasan
            page = context.new_page()
            page.goto(get_alt_url())

            page.wait_for_load_state("networkidle")

            userfms_staff_kemayoran = page.locator("input[name='username']")
            userfms_staff_kemayoran.wait_for(state="visible", timeout=30000)
            userfms_staff_kemayoran.fill(user_staff_kemayoran_fms_uat)

            passfms_staff_kemayoran = page.locator("input[name='password']")
            passfms_staff_kemayoran.wait_for(state="visible", timeout=30000)
            passfms_staff_kemayoran.fill(pass_staff_kemayoran_fms_uat)

            loginfms_button = page.locator("#confirmBtn")
            loginfms_button.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : New Tab baru, lalu buka Portal FMSUAT dan login dengan username yang terdaftar"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    userfms_staff_kemayoran,
                    passfms_staff_kemayoran,
                    loginfms_button
                ],
                highlight=True
            ))

            loginfms_button.click()
            page.wait_for_timeout(3000)

            menu_fms = page.locator("a.app-box-icon i.z-icon-usd")
            menu_fms.wait_for(state="visible")
            menu_fms.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    menu_fms
                ],
                highlight=True
            ))

            page.wait_for_timeout(5000)

            page.keyboard.press("Escape")
            page.locator("button:has-text('Yes')").wait_for()
            page.locator("button:has-text('Yes')").click()

            # -------------------------------------------------------------------------#
            menu_financeaccounting = page.locator(
                "//span[text()='Finance & Accounting']")
            menu_financeaccounting.wait_for(state="visible", timeout=2000)
            menu_financeaccounting.click()

            menu_buktibank = page.locator("//span[text()='Bukti Bank']")
            menu_buktibank.wait_for(state="visible", timeout=2000)
            menu_buktibank.click()

            entri_buktibank = page.locator("//span[text()='Entri Bukti Bank']")
            entri_buktibank.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu finance & accounting -> Bukti Bank -> Entri Bukti Bank"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    menu_financeaccounting,
                    menu_buktibank,
                    entri_buktibank
                ],
                highlight=True
            ))
            entri_buktibank.click()

            bbk_button = page.locator(
                "//button[contains(text(),'BBK : Bukti Bank Keluar')]")
            bbk_button.wait_for(state="visible", timeout=6000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu finance & accounting -> Bukti Bank -> Entri Bukti Bank"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    bbk_button
                ],
                highlight=True
            ))
            bbk_button.click()

            page.wait_for_timeout(3000)

            kode_rekening_bank = select2(page, "cmbBankCode", "Kemayoran")
            page.wait_for_timeout(3000)
            transaksi = zk_combobox(
                page, "(//input[contains(@class,'z-combobox-input')])[11]", "BBK1 - Pembayaran Bank")
            page.wait_for_timeout(3000)

            tanggal_akutansi = page.locator(
                "(//input[contains(@class,'z-datebox-input')])[3]")
            tanggal_akutansi.click()
            page.wait_for_timeout(2000)

            page.locator(
                "(//td[contains(@class,'z-calendar-selected')])[3]").click()
            page.wait_for_timeout(3000)
            nominal_kredit = page.locator(
                "(//input[contains(@class,'form-control')])[14]")
            nominal_kredit.wait_for(state="visible")

            # ========================
            # DEBUG AWAL
            # ========================
            print("RAW pembayaran1:", pembayaran1)

            # convert dari "1,000,000.00" → "1000000"
            clean = pembayaran1.replace(",", "")
            print("SETELAH HAPUS KOMA:", clean)

            clean = float(clean)
            print("SETELAH JADI FLOAT:", clean)

            clean = str(int(clean))
            print("FINAL CLEAN (STRING):", clean)

            # ========================
            # SEBELUM INPUT
            # ========================
            print("VALUE SEBELUM INPUT:", nominal_kredit.input_value())

            # ========================
            # INPUT
            # ========================
            nominal_kredit.fill("")
            nominal_kredit.fill(clean)

            # trigger validation
            nominal_kredit.press("Tab")

            # ========================
            # SETELAH INPUT
            # ========================
            page.wait_for_timeout(1000)

            print("VALUE SETELAH INPUT:", nominal_kredit.input_value())

            dibayar_kepada = page.locator(
                "(//input[contains(@class,'form-control')])[17]")
            dibayar_kepada.wait_for(state="visible", timeout=2000)
            dibayar_kepada.fill("Gerfana Jahya")

            page.wait_for_timeout(2000)

            dibayar_dengan = zk_combobox(
                page, "(//input[contains(@class,'z-combobox-input')])[13]", "Transfer")

            page.wait_for_timeout(2000)
            no_referensi = page.locator(
                "(//input[contains(@class,'form-control')])[18]")
            no_referensi.wait_for(state="visible", timeout=2000)
            no_referensi.fill(
                f"No Polis : {polis} No Klaim : {no_registrasi}")

            page.wait_for_timeout(2000)
            keterangan = page.locator(
                "(//textarea[contains(@class,'form-control')])[1]")
            keterangan.fill("Pembayaran klaim")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input field field mandatory dan cari No Notanya"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    tanggal_akutansi,
                    kode_rekening_bank,
                    transaksi,
                    nominal_kredit,
                    dibayar_kepada,
                    dibayar_dengan,
                    no_referensi,
                    keterangan

                ],
                highlight=True
            ))
            # Rincian Jurnal
            page.locator(
                "//span[contains(@class,'z-listitem-radio')]").first.click()

            table_scroll = page.locator(
                "(//div[contains(@class,'z-listbox-body')])[2]")
            table_scroll.wait_for(state="visible")
            table_scroll.evaluate("el => el.scrollLeft = el.scrollWidth")

            hapus_button = page.locator("button[title='Hapus']")
            hapus_button.wait_for(state="visible", timeout=5000)
            hapus_button.click()
            page.wait_for_timeout(2000)
            page.locator("//button[text()='Yes']").click()

            page.wait_for_timeout(3000)

            multiplesetle_button = page.locator(
                "//button[contains(text(),'Multiple Settlement')]")
            multiplesetle_button.wait_for(state="visible", timeout=5000)
            multiplesetle_button.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Multiple Settlement"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    multiplesetle_button
                ],
                highlight=True
            ))

            nomor_jurnal_field = page.locator(
                "(//input[contains(@class, 'input-sm') and contains(@class, 'form-control')])[20]")
            nomor_jurnal_field.wait_for(state="visible", timeout=5000)
            nomor_jurnal_field.fill(nomor_nota)
            nomor_jurnal = nomor_jurnal_field.input_value()
            print("Nomor Jurnal:", nomor_jurnal)

            carinonota_button = page.locator(
                "(//button[contains(., 'Cari')])[3]")
            carinonota_button.click()
            page.wait_for_timeout(5000)
            page.locator(".z-listitem-checkbox").click()
            page.wait_for_timeout(5000)

            # locator tombol pilih
            Pilih_button = page.locator(
                "//button[contains(@class,'btn-primary') and contains(text(),'Pilih')]")
            Pilih_button.wait_for(state="visible", timeout=5000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari No Jurnalnya, check dan klik tombol Pilih"
            )

            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    nomor_jurnal_field,
                    carinonota_button,
                    ".z-listitem-checkbox",
                    Pilih_button
                ],
                highlight=True
            ))

            page.wait_for_timeout(5000)
            # pastikan tombol ada di viewport
            Pilih_button.scroll_into_view_if_needed()
            # klik tombol
            Pilih_button.click()
            print("Berhasil di klik")
            page.wait_for_timeout(10000)

            # isi catatan
            catatan = page.locator("textarea.form-control").nth(1)
            catatan.wait_for(state="visible", timeout=10000)
            catatan.fill("Harap di Proses")

            submit_button_fms = page.locator(
                "//button[.//text()[contains(.,'Submit')]]")
            submit_button_fms.wait_for(state="visible", timeout=3000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input keterangan Harap di Proses dan klik tombol Submit"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    catatan,
                    submit_button_fms
                ],
                highlight=True
            ))
            submit_button_fms.click()
            page.wait_for_timeout(3000)

            yes_button = page.locator("button:has-text('Yes')")
            yes_button.wait_for(state="visible", timeout=3000)
            yes_button.click()

            Ok_button = page.locator("button:has-text('Ok')")
            Ok_button.wait_for(state="visible", timeout=3000)
            Ok_button.click()

            page.wait_for_timeout(3000)
            nomor_jurnal_bbk_field = page.locator(
                "(//input[contains(@class,'form-control-readonly')])[1]")
            nomor_jurnal_bbk = nomor_jurnal_bbk_field.input_value()
            print(nomor_jurnal_bbk)

            page.locator("//span[contains(text(),'staff.kemayoran')]").click()
            signout_button_fms = page.locator(
                "//span[contains(text(),'Keluar')]")
            signout_button_fms.wait_for(state="visible", timeout=3000)
            signout_button_fms.click()

            userfms_kasie_kemayoran = page.locator("input[name='username']")
            userfms_kasie_kemayoran.wait_for(state="visible", timeout=30000)
            userfms_kasie_kemayoran.fill(user_kasie_kemayoran_fms_uat)

            passfms_kasie_kemayoran = page.locator("input[name='password']")
            passfms_kasie_kemayoran.wait_for(state="visible", timeout=30000)
            passfms_kasie_kemayoran.fill(pass_kasie_kemayoran_fms_uat)

            loginfms_button = page.locator("#confirmBtn")
            loginfms_button.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : login dengan username kasie_kemayoran yang terdaftar"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    userfms_kasie_kemayoran,
                    passfms_kasie_kemayoran,
                    loginfms_button
                ],
                highlight=True
            ))

            loginfms_button.click()
            page.wait_for_timeout(3000)

            menu_fms = page.locator("a.app-box-icon i.z-icon-usd")
            menu_fms.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    menu_fms
                ],
                highlight=True
            ))
            menu_fms.click()
            page.wait_for_timeout(5000)

            page.keyboard.press("Escape")

            yes_button = page.locator("button:has-text('Yes')")
            yes_button.wait_for(state="visible", timeout=3000)
            yes_button.click()

            tasklist = page.locator(
                "(//span[contains(text(),'Task Lists')])[1]")
            tasklist.wait_for(state="visible", timeout=3000)
            tasklist.click()

            bbk = page.locator("//span[contains(text(),'BBK')]")
            bbk.wait_for(state="visible", timeout=3000)
            bbk.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu tasklist, lalu klik BBK"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    tasklist,
                    bbk
                ],
                highlight=True
            ))
            page.wait_for_timeout(5000)
            xpath = f"//span[text()='{nomor_jurnal_bbk}']"
            page.locator(xpath).wait_for(state="visible", timeout=5000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari No Jurnal BBK yang telah disimpan lalu klik No Jurnal BBK tersebut"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    xpath
                ],
                highlight=True
            ))
            page.locator(xpath).click()

            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            catatan.fill("Setuju")

            setuju_button_fms = page.locator(
                "//button[.//text()[contains(.,'Setuju')]]")
            setuju_button_fms.wait_for(state="visible", timeout=3000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Setuju untuk perlunasan fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    catatan,
                    setuju_button_fms
                ],
                highlight=True
            ))
            setuju_button_fms.click()
            page.wait_for_timeout(3000)
            yes_button.click()
            page.wait_for_timeout(3000)
            Ok_button.click()

            page.locator("//span[contains(text(),'kasie.kemayoran')]").click()
            signout_button_fms = page.locator(
                "//span[contains(text(),'Keluar')]")
            signout_button_fms.wait_for(state="visible", timeout=3000)
            signout_button_fms.click()

            userfms_kabag_kemayoran = page.locator("input[name='username']")
            userfms_kabag_kemayoran.wait_for(state="visible", timeout=30000)
            userfms_kabag_kemayoran.fill(user_kabag_kemayoran_fms_uat)

            passfms_kabag_kemayoran = page.locator("input[name='password']")
            passfms_kabag_kemayoran.wait_for(state="visible", timeout=30000)
            passfms_kabag_kemayoran.fill(pass_kabag_kemayoran_fms_uat)

            loginfms_button = page.locator("#confirmBtn")
            loginfms_button.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : login dengan username kabag_kemayoran yang terdaftar"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    userfms_kabag_kemayoran,
                    passfms_kabag_kemayoran,
                    loginfms_button
                ],
                highlight=True
            ))

            loginfms_button.click()
            page.wait_for_timeout(3000)

            menu_fms = page.locator("a.app-box-icon i.z-icon-usd")
            menu_fms.wait_for(state="visible")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    menu_fms
                ],
                highlight=True
            ))

            menu_fms.click()
            page.wait_for_timeout(5000)

            page.keyboard.press("Escape")

            yes_button = page.locator("button:has-text('Yes')")
            yes_button.wait_for(state="visible", timeout=3000)
            yes_button.click()

            tasklist = page.locator(
                "(//span[contains(text(),'Task Lists')])[1]")
            tasklist.wait_for(state="visible", timeout=3000)
            tasklist.click()

            bbk = page.locator("//span[contains(text(),'BBK')]")
            bbk.wait_for(state="visible", timeout=3000)
            bbk.click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik menu tasklist, lalu klik BBK"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    tasklist,
                    bbk
                ],
                highlight=True
            ))
            page.wait_for_timeout(5000)
            xpath = f"//span[text()='{nomor_jurnal_bbk}']"
            page.locator(xpath).wait_for(state="visible", timeout=5000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari No Jurnal BBK yang telah disimpan lalu klik No Jurnal BBK tersebut"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    xpath
                ],
                highlight=True
            ))
            page.locator(xpath).click()

            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            catatan.fill("Setuju")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Setuju untuk perlunasan fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    catatan,
                    setuju_button_fms
                ],
                highlight=True
            ))
            setuju_button_fms.click()
            page.wait_for_timeout(2000)
            yes_button.click()
            page.wait_for_timeout(2000)
            Ok_button.click()

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            catatan.fill("Posting")

            posting_button_fms = page.locator(
                "//button[.//text()[contains(.,'Posting')]]")
            posting_button_fms.wait_for(state="visible", timeout=3000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Klik tombol Posting untuk perlunasan fms"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    catatan,
                    posting_button_fms
                ],
                highlight=True
            ))

            posting_button_fms.click()
            page.wait_for_timeout(2000)
            yes_button.click()
            page.wait_for_timeout(2000)
            Ok_button.click()

            page.wait_for_timeout(4000)

            status_fms = page.locator("(//input[@readonly='readonly'])[5]")
            status_fms.wait_for(state="visible")

            status_posting = status_fms.input_value()
            print("STATUS POSTING:", status_posting)

            if status_posting != "Posted":
                raise Exception(
                    f"Expected 'Open' namun yang didapat '{status_posting}'")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cek field pada status posting, apakah berubah jadi Posted"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    status_fms
                ],
                highlight=True
            ))
            page.wait_for_timeout(2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Verifikasi data di database, apakah DOC_STATUS = 5 (SETUJU) dan PAYMENT_STATUS = 'F'?"
            )

            screenshots_rendered.append(None)

            query = query_klaim_settlement(no_registrasi)
            db_result = execute_query(query)

            # Simpan ke PDF
            database_verifications.append({
                "step": stepno,
                "query": query,
                "result": db_result
            })

            # =========================
            # VALIDASI DATABASE
            # =========================
            if not db_result:
                raise Exception(
                    f"Data settlement dengan nomor registrasi "
                    f"'{no_registrasi}' tidak ditemukan di database"
                )

            row = db_result[0]

            if row.get("DOC_STATUS") != 5:
                raise Exception(
                    f"DOC_STATUS bernilai "
                    f"{row.get('DOC_STATUS')} "
                    f"({row.get('DOC_STATUS_KLAIM')}), "
                    f"seharusnya 5 (SETUJU)"
                )

            if row.get("ENDORSE_VALUE_TYPE") is not None:
                raise Exception(
                    f"ENDORSE_VALUE_TYPE bernilai "
                    f"'{row.get('ENDORSE_VALUE_TYPE')}', "
                    f"seharusnya NULL"
                )

            if row.get("SETTLE_NOTE_NO") is None:
                raise Exception(
                    "SETTLE_NOTE_NO tidak terisi"
                )

            if row.get("PAYMENT_STATUS") != "F":
                raise Exception(
                    f"PAYMENT_STATUS bernilai "
                    f"'{row.get('PAYMENT_STATUS')}', "
                    f"seharusnya 'F'"
                )

            if row.get("PAYMENT_DATE") is None:
                raise Exception(
                    "PAYMENT_DATE tidak terisi"
                )

            if row.get("BANK_NOTE_NUMBER") is None:
                raise Exception(
                    "BANK_NOTE_NUMBER tidak terisi"
                )

            if row.get("AMT_PAYMENT") is None:
                raise Exception(
                    "AMT_PAYMENT tidak terisi"
                )

            print("[PASS] Validasi berhasil")

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
            "database_verifications": database_verifications,
            "testdata": {
                "No Polis": polis,
                "No Klaim": no_registrasi,
                "No Nota": nomor_nota,
                "No Lpk": no_lpk,
            }
        })

    finally:
        print("="*50)
        print("✅ END Case - Klaim Lunas selesai dieksekusi")
        try:
            final_actual_result = actual_result.format(
                no_registrasi=no_registrasi or "-",
                no_lpk=no_lpk or "-",
                nomor_nota=nomor_nota or "-",
                nomor_jurnal_bbk=nomor_jurnal_bbk or "-",
            )
            if generate_pdf:
                generate_pdf_report(
                    status=status,
                    testcase_id=testcase_id,
                    testcase_name=testcase_name,
                    jenis_test=jenis_test,
                    screenshot_paths=screenshots_rendered,
                    actual_result=log_error or final_actual_result,
                    expected_result=expected_result,
                    test_steps_rendered=test_steps_rendered,
                    database_verifications=database_verifications,
                    tester_name=tester_name,
                    precondition=precondition,
                    testdata={
                        "No Polis": polis,
                        "No Klaim": no_registrasi,
                        "No Nota": nomor_nota,
                        "No Lpk": no_lpk
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
        "nomor_jurnal": nomor_jurnal,
        "nomor_jurnal_bbk": nomor_jurnal_bbk,
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "database_verifications": database_verifications,
        "status": status,
        "actual_result": log_error or final_actual_result,
        "testdata": {
            "No Polis": polis,
            "No Klaim": no_registrasi,
            "No Nota": nomor_nota,
            "No Lpk": no_lpk,
        }
    }


@pytest.mark.positive
@pytest.mark.klaim
@pytest.mark.regression
def test_run_registrasi_klaim_lunas():
    run_Registrasi_Klaim_Lunas()


# if __name__ == "__main__":
#     print("Running Case - Registrasi Klaim Lunas...")
#     run_Registrasi_Klaim_Lunas()
