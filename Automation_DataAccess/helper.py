from datetime import datetime, timedelta
import re
import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
import random


def get_request_number(text):
    match = re.search(r'[\d\.\-]+', text)
    return match.group() if match else None


def get_request_number_from_notif(page):
    notif = page.locator('[id^="smallbox"]')
    notif.wait_for(state="visible")

    text = notif.inner_text()
    return get_request_number(text)


def get_No_AN(text):
    match = re.search(r'AN[-\s]?[\d\-]+', text)
    return match.group() if match else None


def fill_kode_produk_external(page):
    value = f"{datetime.now().strftime('%H%M%S')}"
    page.locator("input[placeholder='Kode Produk External']").fill(value)
    return value


def daftar_risiko(page):
    next_btn = page.locator("button.btn-next")
    step = page.locator("li[data-name='daftar-risiko']")

    for _ in range(10):
        cls = step.get_attribute("class") or ""

        # HANYA stop kalau active
        if "active" in cls:
            return

        next_btn.click()

    expect(step).to_have_class(re.compile("active"))

    raise Exception("Tidak sampai ke daftar risiko")
    
    

def ketentuan_pertanggungan(page):
    next_btn = page.locator("button.btn-next")
    step = page.locator("li[data-name='pertanggungan']")

    for _ in range(10):
        cls = step.get_attribute("class") or ""

        # HANYA stop kalau active
        if "active" in cls:
            return

        next_btn.click()

    expect(step).to_have_class(re.compile("active"))

    raise Exception("Tidak sampai ke ketentuan pertanggungan")

def biaya_pertanggungan(page):
    next_btn = page.locator("button.btn-next")
    step = page.locator("li[data-name='biaya-pertanggungan']")

    for _ in range(10):
        cls = step.get_attribute("class") or ""

        # HANYA stop kalau active
        if "active" in cls:
            return

        next_btn.click()

    expect(step).to_have_class(re.compile("active"))

    raise Exception("Tidak sampai ke biaya pertanggungan")

def biaya_lain(page):
    next_btn = page.locator("button.btn-next")
    step = page.locator("li[data-name='biaya-lain-lain']")

    for _ in range(10):
        cls = step.get_attribute("class") or ""

        # HANYA stop kalau active
        if "active" in cls:
            return

        next_btn.click()

    expect(step).to_have_class(re.compile("active"))

    raise Exception("Tidak sampai ke biaya lain")

def ensure_toggle_on(page, checkbox_id):
    toggle = page.locator(f"label[for='{checkbox_id}']")
    toggle.scroll_into_view_if_needed()
    toggle.click(force=True)

def get_no_polis(page):
    xpath = "//td[count(//th[normalize-space()='NO POLIS']/preceding-sibling::th)+1]"

    return page.locator(xpath).first.inner_text()


def select_combobox(page, label_text, option_text):
    
    combo = page.locator(f"//label[normalize-space()='{label_text}']/parent::*//span[@role='combobox']").first

    combo.click()

    option = page.locator(".select2-results__option",
                          has_text=option_text).first
    option.wait_for(state="visible", timeout=10000)

    option.click()


def select_combo(page, label_text, option_text):
    combo = (
        page.locator(f"label:has-text('{label_text}')")
        .locator("..")
        .get_by_role("textbox")
    )

    combo.click()
    
    option = page.locator(".select2-results__option")
    option.first.wait_for()
     # klik option spesifik
    page.locator(".select2-results__option", has_text=option_text).first.click()

def to_roman(month):
    romans = [
        "", "I", "II", "III", "IV", "V",
        "VI", "VII", "VIII", "IX", "X", "XI", "XII"
    ]
    return romans[month]

def generate_no_nota(seq=None, unit="KCU-UW"):
    now = datetime.now()

    if seq is None:
        seq = int(time.time())  # unik

    return f"{seq}/{unit}/{to_roman(now.month)}/{now.year}"
