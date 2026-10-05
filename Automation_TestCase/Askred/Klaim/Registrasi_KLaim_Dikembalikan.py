from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from Automation_TestCase.Askred.Akseptasi import Akseptasi_RegistrasiDJP

from datetime import datetime
import fpdf
import traceback
import sys
import re
import pytest
from Automation_QAMap.qamap_client import record_step

# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Registrasi_Klaim_Dikembalikan"]
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


def run_Registrasi_Klaim_Askred(generate_pdf=True):
    # Wadah langkah yang mengabarkan tiap penambahannya ke QAMap saat itu
    # juga. Di luar main_runner atau ketika QAMap tidak dipakai, ia
    # berperilaku persis seperti list kosong biasa.
    test_steps_rendered = record_step()
    screenshots_rendered = []
    status = "Passed"
    stepno = 0
    log_error = None  # inisialisasi
    execution_time = datetime.now().strftime("%d/%m/%Y")

    print("="*50)
    print("🔄 START Case - Akseptasi Polis sedang berjalan")
    print("="*50)

    akseptasi = Akseptasi_RegistrasiDJP.run_RegisDJP(generate_pdf=False)
    polis = akseptasi.get("polis")
    print("POLIS DARI DJP:", polis)

    print("="*50)
    print(f"✅ END Case - Akseptasi Polis Selesai. No Polis: {polis}")
    print("="*50)
    print("🔄 START Case - Klaim Dikembalikan sedang berjalan")
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
    disposisi2 = "Klaim Dikembalikan"
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
            ditemukan_no_polis.wait_for(state="visible", timeout=45000)
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
                         has_text="Kebakaran").click()

            page.locator(
                "//label[contains(text(),'Type Penyebab Claim')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(".select2-container--open li.select2-results__option",
                         has_text="Huru Hara").click()

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
                         has_text="Klaim Dikembalikan / Batal - Klaim Ditarik").click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih Kesimpulan Klaim Dikembalikan")
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

            page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentCurrentId']")

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
                    "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentCurrentId']"
                ],
                highlight=True
            ))

            page.fill(
                "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']", disposisi2)
            procced_button = page.locator(
                "//button[normalize-space()='PROCEED KEMBALI']")
            procced_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Disposisi lalu klik Tombol Procced kembali")
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=["textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']",
                          procced_button
                          ],
                highlight=True
            ))
            procced_button.click()

            page.wait_for_timeout(5000)

            konfirmasi = page.locator(
                "p.pText:has-text('Apakah anda yakin memproses dokumen ini?')")
            konfirmasi.wait_for(state="visible", timeout=5000)
            page.locator("#bot2-Msg1").click()  # Ya

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            success_msg.click()

            # Cek data Klaimnya
            cari_klaim_dikembalikan = page.locator(
                "input[type='search'][aria-controls='dt_basic']")
            cari_klaim_dikembalikan.wait_for(state="visible", timeout=2000)
            cari_klaim_dikembalikan.fill(no_registrasi)
            page.wait_for_timeout(2000)

            page.locator(".input-group-addon .glyphicon-search").click()

            klaimdikembalikan = page.locator(
                "td.class-data", has_text="Di kembalikan")
            klaimdikembalikan.wait_for(state="visible", timeout=10000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari data klaim yang telah disetujui dan status doc Dikembalikan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    cari_klaim_dikembalikan,
                    ".input-group-addon .glyphicon-search",
                    klaimdikembalikan
                ],
                highlight=True
            ))

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Verifikasi data, Apakah klaimnya telah masuk ke DB dan apakah status Doc = 40 ?")

            screenshots_rendered.append(None)

            query = query_klaim_Dikembalikan_Ditolak(no_registrasi)
            db_result = execute_query(query)

            # Simpan ke PDF terlebih dahulu
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

            if row.get("DOC_STATUS") != 40:
                raise Exception(
                    f"DOC_STATUS bernilai "
                    f"{row.get('DOC_STATUS')} "
                    f"({row.get('DOC_STATUS_KLAIM')}), "
                    f"seharusnya 40 (DIKEMBALIKAN)"
                )

            if row.get("ENDORSE_VALUE_TYPE") is not None:
                raise Exception(
                    f"ENDORSE_VALUE_TYPE bernilai "
                    f"'{row.get('ENDORSE_VALUE_TYPE')}', "
                    f"seharusnya NULL"
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
            }
        })

    finally:
        print("=" * 50)
        print("✅ END Case - Klaim Dikembalikan selesai dieksekusi")

        try:
            final_actual_result = actual_result.format(
                no_registrasi=no_registrasi or "-"
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
                    }
                )

                print("\n===== TEST STEPS =====")
                for i, step in enumerate(test_steps_rendered, start=1):
                    clean_step = re.sub(
                        r"\[Test_Step_\d+\]\s*:\s*",
                        "",
                        step
                    )
                    print(f"{i}. {clean_step}")

                print("===== END TEST STEPS =====\n")
                # =========================
                # SAVE DB
                # =========================
                try:
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
                        f"[{status}] {testcase_id} - "
                        f"{testcase_name} berhasil disimpan ke DB ✅"
                    )

                except Exception as inner_e:
                    print(
                        f"[Warning] Gagal simpan hasil ke DB: {inner_e}"
                    )

        except Exception as e:
            print(
                f"[Warning] Gagal generate PDF: {e}"
            )

    return {
        "test_steps": test_steps_rendered,
        "screenshots": screenshots_rendered,
        "status": status,
        "actual_result": log_error or final_actual_result,
        "database_verifications": database_verifications,
        "testdata": {
            "No Polis": polis,
        }
    }


@pytest.mark.negative
@pytest.mark.klaim
@pytest.mark.regression
def test_run_Registrasi_Klaim_Askred():
    run_Registrasi_Klaim_Askred()

# if __name__ == "__main__":
#     test_Registrasi_Klaim_Askred()
