from Automation_Report.pdf_generator import *
from Automation_DataAccess.db_utils import *
from Automation_DataAccess.db_writer import *
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.data_loader import load_accounts, get_base_url
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from Automation_TestCase.Askred.Klaim import Registrasi_KLaim_Disetujui

from datetime import datetime
import fpdf
import traceback
import sys
import re
import pytest
from Automation_QAMap.qamap_client import record_step

# bagian testcase_data disesuaikan dengan project kalian
data = testcase_data["Klaim_Pembatalan"]
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


@pytest.mark.positive
@pytest.mark.klaim
@pytest.mark.regression
def test_klaim_pembatalan_askred(generate_pdf=True):
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
    print("🚀 START Case - Klaim Disetujui sedang berjalan...")
    print("="*50)

    klaim_askred = Registrasi_KLaim_Disetujui.run_Registrasi_Klaim_Askred(
        generate_pdf=False)

    no_registrasi = klaim_askred.get("no_registrasi")
    no_lpk = klaim_askred.get("no_lpk")
    polis = klaim_askred.get("polis")

    print("="*50)
    print(f"✅ END Case - Klaim Disetujui selesai. No Klaim: {no_registrasi}")
    print("="*50)
    print(f"♻️ Menggunakan No Registrasi: {no_registrasi}")
    print(f"♻️ Polis terkait: {polis}")
    print("="*50)

    # ================================
    # 🚀 LANJUT KLAIM PEMBATALAN
    # ================================
    print("🚀 START Case - Klaim Pembatalan sedang berjalan...")
    print("="*50)

    disposisi1 = "Harap di Analisa kembali"
    disposisi2 = "Harap diproses"
    disposisi3 = "Klaim di Approve"
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

            cari_klaim_approve = page.locator(
                "input[type='search'][aria-controls='dt_basic']")
            cari_klaim_approve.wait_for(state="visible", timeout=10000)
            cari_klaim_approve.fill(no_registrasi)
            page.wait_for_timeout(2000)

            page.locator(".input-group-addon .glyphicon-search").click()

            endors_button = page.locator("a[data-action='endorse']")
            endors_button.wait_for(state="visible", timeout=20000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih menu Askred -> Klaim Askred -> Klaim Registration, cari klaim yang telah di setujui untuk di endorsment"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    askred_menu,
                    klaim_askred,
                    registrasi_klaim,
                    endors_button,
                    cari_klaim_approve,
                    ".input-group-addon .glyphicon-search"
                ],
                highlight=True
            ))
            endors_button.click()

            # -----------------------------------------------------------------------------------------3
            # Form Registrasi Klaim
            page.locator(
                "//label[contains(text(),'Tipe Endorsement')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(
                "//li[contains(@class,'select2-results__option') and contains(text(),'Endorsement')]").click()

            page.locator(
                "//label[contains(text(),'Jenis Endorsement')]/following::span[contains(@class,'select2-selection')][1]").click()
            page.wait_for_selector(".select2-container--open")
            page.locator(
                "//li[contains(@class,'select2-results__option') and contains(text(),'Pembatalan')]").click()

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Pilih Tipe Endorsement dan Jenis Endorsement Pembatalan"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    "//label[contains(text(),'Tipe Endorsement')]/following::span[contains(@class,'select2-selection')][1]",
                    "//label[contains(text(),'Jenis Endorsement')]/following::span[contains(@class,'select2-selection')][1]"
                ],
                highlight=True
            ))
            # ----------------------------------------------------------------------------------------------#
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

            status_registered = page.locator(
                "//td[text()='Analisis Pembatalan Claim']")
            status_registered.wait_for(state="visible", timeout=15000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari No Klaim yang masuk ditasklist lalu klik Klaim tersebut")
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
            page.wait_for_timeout(8)

            # Kerugian menurut Askrindo Before
            pembayaran_before = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentPrevId']")
            pembayaran_before.wait_for(state="visible", timeout=8000)
            pembayaran_before.scroll_into_view_if_needed()

            pembayaran_value = pembayaran_before.input_value()
            pembayaran_value1 = float(pembayaran_value.replace(",", ""))
            print(pembayaran_value1)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cek Kerugian before menurut Askrindo"
            )
            screenshots_rendered.append(
                save_screenshot(
                    page=page,
                    selector=[
                        "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentPrevId']"
                    ],
                    highlight=True
                )
            )

            # Kerugian menurut Askrindo After
            pokok = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.pokokId']")
            pokok.wait_for(state="visible", timeout=5000)
            pokok_value = pokok.input_value()

            bunga = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.bungaId']")
            bunga.wait_for(state="visible", timeout=1000)
            bunga_value = bunga.input_value()

            denda = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.dendaId']")
            denda.wait_for(state="visible", timeout=1000)
            denda_value = denda.input_value()

            payment = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentCurrentId']")
            payment.wait_for(state="visible", timeout=1000)
            payment_value = payment.input_value()

            # Validasi
            if pokok_value == "0.00" and bunga_value == "0.00" and denda_value == "0.00" and payment_value == "0.00":
                print("PASS - Karena dibatalkan semua nilai = 0.00")
            else:
                raise Exception(
                    f"FAILED - Nilai tidak 0.00: pokok={pokok_value}, bunga={bunga_value}, denda={denda_value}, payment={payment_value}")

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Kerugian After menurut Askrindo harusnya bernilai 0.00"
            )
            screenshots_rendered.append(
                save_screenshot(
                    page=page,
                    selector=[
                        pokok,
                        bunga,
                        denda,
                        payment
                    ],
                    highlight=True
                )
            )

            # Tunggu hasil perhitungan muncul
            payment_prop = page.locator(
                "//input[@id='sigma.numeric.sigma.currency.amount.amtPaymentPropId']")
            payment_prop.wait_for(state="visible", timeout=5000)
            payment_prop.scroll_into_view_if_needed()
            payment_prop_value = payment_prop.input_value()
            payment_prop_value1 = float(payment_prop_value.replace(",", ""))
            print(payment_prop_value1)

            # Validasi
            if payment_prop_value1 == -pembayaran_value1:
                print("PASS - Pembayaran prop sesuai karena dibatalkan")
            else:
                raise Exception(
                    f"FAILED - payment_prop {payment_prop_value} tidak sama dengan {-pembayaran_value}")

            # Screenshot step
            page.wait_for_timeout(2000)
            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cek selisih pembayaran, harusya bernilai - dan nilainya sama dengan pembayaran before"
            )

            screenshots_rendered.append(
                save_screenshot(
                    page=page,
                    selector=[
                        payment_prop
                    ],
                    highlight=True
                )
            )

            page.fill(
                "textarea[disablelabel='Analisa/Saran/Disposisi/Kesimpulan']", disposisi2)
            procced_button = page.locator(
                "//button[normalize-space()='PROCEED']")
            procced_button.wait_for(state="visible", timeout=2000)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Input Disposisi lalu klik Tombol Procced")
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
                    f"[Test_Step_{stepno}] : Kirim ke User untuk Proceed Pembatalan"
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
                    f"[Test_Step_{stepno}] : Kirim ke User untuk Proceed Pembatalan "
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
            )
            )
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
                f"[Test_Step_{stepno}] : Cari No Klaim yang masuk ditasklist lalu klik Klaim tersebut")
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

            batal_klaim = page.locator(
                "td.class-data", has_text="Batal Klaim")
            batal_klaim.wait_for(state="visible", timeout=10000)

            no_lpk_locator = page.locator(
                '//*[@id="dt_basic"]/tbody/tr[1]/td[11]')
            no_lpk_locator.wait_for(state="visible", timeout=5000)
            no_lpk_endorsement = no_lpk_locator.inner_text()
            print("No LPK:", no_lpk_endorsement)

            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Cari data klaim yang telah disetujui dan status doc Batal Klaim"
            )
            screenshots_rendered.append(save_screenshot(
                page=page,
                selector=[
                    cari_klaim_approve,
                    ".input-group-addon .glyphicon-search",
                    batal_klaim,
                    no_lpk_locator
                ],
                highlight=True
            )
            )
            stepno += 1
            test_steps_rendered.append(
                f"[Test_Step_{stepno}] : Verifikasi data di database, apakah DOC_STATUS = 23 (CANCELL) dan ENDORSE_VALUE_TYPE = 'KUR_JENIS_ENDORSMENT.pB'?"
            )

            screenshots_rendered.append(None)

            query = query_klaim_settlement(no_registrasi)
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

            if row.get("DOC_STATUS") != 23:
                raise Exception(
                    f"DOC_STATUS bernilai "
                    f"{row.get('DOC_STATUS')} "
                    f"({row.get('DOC_STATUS_KLAIM')}), "
                    f"seharusnya 23 (CANCELL)"
                )

            if row.get("ENDORSE_VALUE_TYPE") != "KUR_JENIS_ENDORSMENT.PB":
                raise Exception(
                    f"ENDORSE_VALUE_TYPE bernilai "
                    f"'{row.get('ENDORSE_VALUE_TYPE')}', "
                    f"seharusnya 'KUR_JENIS_ENDORSMENT.PB'"
                )

            if row.get("SETTLE_NOTE_NO") is None:
                raise Exception(
                    "SETTLE_NOTE_NO tidak terisi"
                )

            if row.get("PAYMENT_STATUS") is not None:
                raise Exception(
                    f"PAYMENT_STATUS bernilai "
                    f"'{row.get('PAYMENT_STATUS')}', "
                    f"seharusnya NULL"
                )

            if row.get("PAYMENT_DATE") is not None:
                raise Exception(
                    f"PAYMENT_DATE bernilai "
                    f"'{row.get('PAYMENT_DATE')}', "
                    f"seharusnya NULL"
                )

            if row.get("BANK_NOTE_NUMBER") is not None:
                raise Exception(
                    f"BANK_NOTE_NUMBER bernilai "
                    f"'{row.get('BANK_NOTE_NUMBER')}', "
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
            "database_verifications": database_verifications,
            "screenshots": screenshots_rendered,
            "testdata": {
                "No Polis": polis,
                "No Registrasi Klaim": no_registrasi,
                "No LPK": no_lpk
            }
        })

    finally:
        print("="*50)
        print("✅ END Case - Klaim Pembatalan selesai dieksekusi")

        try:
            final_actual_result = actual_result.format(
                no_registrasi=no_registrasi or "-",
                no_lpk_endorsement=no_lpk_endorsement or "-")
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
                    precondition=precondition,
                    tester_name=tester_name,
                    testdata={
                        "No Polis": polis,
                        "No Registrasi Klaim": no_registrasi,
                        "No LPK": no_lpk
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
        "database_verifications": database_verifications,
        "actual_result": log_error or final_actual_result,
        "testdata": {
            "No Polis": polis,
            "No Registrasi Klaim": no_registrasi,
            "No LPK": no_lpk
        }
    }


if __name__ == "__main__":
    test_klaim_pembatalan_askred()
