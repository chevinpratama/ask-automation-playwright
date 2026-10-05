import os
import time
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageOps
from Automation_Report.function_pdf import *
import shutil
import glob
from Automation_DataAccess.testdata_askred import *
from Automation_DataAccess.helper_laporan import detail_project


# ================Cover Judul=========================#
def add_cover_page(pdf, detail_project, report_title="", ba_title=""):
    pdf.add_page()

    page_width = 210  # A4 width
    center_x = page_width / 2

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(
        base_dir, "Automation_Report", "logo_askrindo.png")

    # ===== LOGO KECIL KIRI =====
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=20, y=15, w=40)

    # ===== GARIS =====
    pdf.set_draw_color(150, 150, 150)
    pdf.line(20, 30, 190, 30)

 # ===== LOGO BESAR (KANAN) =====
    if os.path.exists(logo_path):
        logo_width = 80
        x_logo = 190 - logo_width   # 🔥 kanan (210 - margin 20)
        pdf.image(logo_path, x=x_logo, y=80, w=logo_width)

    # ===== AMBIL DATA =====
    judul = report_title or detail_project["judul_laporan"]
    jenis = ba_title
    project_code = detail_project["project_code"]
    # ===== JUDUL =====
    pdf.set_y(140)
    pdf.set_font("Arial", "B", 22)
    pdf.set_x(20)
    pdf.multi_cell(170, 8, judul, align="R")

    # ===== SUBTITLE =====
    pdf.ln(2)
    pdf.set_text_color(64, 64, 64)
    pdf.set_font("Arial", "I", 18)
    pdf.set_x(20)
    pdf.multi_cell(170, 7, jenis, align="R")

    # ===== CODE =====
    pdf.ln(2)  # 🔥 dari 3 → 2 (biar lebih rapat ke BA)
    pdf.set_font("Arial", "", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(20)
    pdf.cell(170, 6, project_code, ln=True, align="R")

    # ===== DATE =====
    pdf.ln(1)  # 🔥 kasih jarak dikit biar nggak nempel banget
    pdf.set_font("Arial", "", 11)
    pdf.set_x(20)
    pdf.cell(
        170,
        5,
        datetime.now().strftime('%d/%m/%Y'),
        ln=True,
        align="R"
    )
    # ---Cofidently---#
    pdf.set_y(260)
    pdf.set_font("Arial", "", 6)

    pdf.set_x(20)
    pdf.multi_cell(
        170,
        3,
        "Confidentiality\n"
        "This document contains proprietary information that is confidential to Askrindo. "
        "Disclosure of this document in full or in part may result in material damage to Askrindo. "
        "Written permission must be obtained from Askrindo prior to the disclosure of this document to a third party.",
        align="L"
    )

# ================================Kontrol Perubahan=======================#


def add_kontrol_perubahan(pdf, detail_project):
    pdf.add_page()
    pdf.set_draw_color(0, 0, 0)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(40)

    # ===== JUDUL =====
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Kontrol Perubahan Dokumen", ln=True, align="C")

    pdf.ln(5)

    headers = ["Versi", "Tanggal", "Penyusun", "Kesimpulan Perubahan"]
    col_widths = [20, 35, 50, 65]

    # HEADER
    pdf.set_fill_color(200, 200, 200)  # 🔥 abu-abu
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 10)

    pdf.set_x(20)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 8, h, border=1, align="C",
                 fill=True)
    pdf.ln()

    # DATA
    pdf.set_font("Arial", "", 10)

    for item in detail_project.get("kontrol_perubahan", []):
        y_start = pdf.get_y()

        values = [
            item.get("versi", ""),
            item.get("tanggal", ""),
            item.get("penyusun", ""),
            item.get("keterangan", "")
        ]

        # ===== HITUNG HEIGHT DINAMIS =====
        temp = FPDF()
        temp.add_page()
        temp.set_font("Arial", "", 10)

        heights = []
        for i, val in enumerate(values):
            temp.set_xy(0, 0)
            temp.multi_cell(col_widths[i], 5, str(val))
            heights.append(temp.get_y())

        row_height = max(heights)

        # ===== DRAW CELL =====
        x_current = 20
        for i, val in enumerate(values):
            pdf.set_xy(x_current, y_start)
            pdf.multi_cell(col_widths[i], 5, str(val), border=1)
            x_current += col_widths[i]

        pdf.set_y(y_start + row_height)

# ==================================Lembar Pengesahan==========================#


def add_lembar_pengesahan(pdf, detail_project):

    pdf.add_page()

    pdf.set_auto_page_break(
        auto=True,
        margin=25
    )

    pdf.set_draw_color(0, 0, 0)
    pdf.set_text_color(0, 0, 0)

    pdf.set_y(40)

    # ==================================================
    # TITLE
    # ==================================================

    pdf.set_font("Arial", "B", 12)

    pdf.set_x(20)

    pdf.cell(
        170,
        6,
        "Lembar Pengesahan",
        ln=True
    )

    pdf.ln(5)

    # ==================================================
    # CONFIG
    # ==================================================

    start_x = 20

    left_w = 40
    right_w = 130

    row_h = 12

    data = detail_project.get(
        "lembar_pengesahan",
        {}
    )

    # ==================================================
    # TABLE
    # ==================================================

    for role_name, people in data.items():

        if not people:
            continue

        group_height = row_h * len(people)

        # ==========================================
        # PAGE BREAK
        # ==========================================

        if pdf.get_y() + group_height > 260:

            pdf.add_page()

            pdf.set_y(40)

            pdf.set_font(
                "Arial",
                "B",
                12
            )

            pdf.set_x(20)

            pdf.cell(
                170,
                6,
                "Lembar Pengesahan",
                ln=True
            )

            pdf.ln(5)

        y_start = pdf.get_y()

        # ==========================================
        # LEFT MERGED CELL
        # ==========================================

        pdf.rect(
            start_x,
            y_start,
            left_w,
            group_height
        )

        pdf.set_xy(
            start_x + 2,
            y_start + 3
        )

        pdf.set_font(
            "Arial",
            "B",
            9
        )

        pdf.multi_cell(
            left_w - 4,
            4,
            role_name
        )

        # ==========================================
        # RIGHT CELL
        # ==========================================

        current_y = y_start

        for person in people:

            pdf.rect(
                start_x + left_w,
                current_y,
                right_w,
                row_h
            )

            # ==========================
            # NAMA
            # ==========================

            pdf.set_xy(
                start_x + left_w + 3,
                current_y + 2
            )

            pdf.set_font(
                "Arial",
                "BU",
                9
            )

            pdf.cell(
                right_w - 6,
                4,
                person.get(
                    "nama",
                    ""
                )
            )

            # ==========================
            # JABATAN
            # ==========================

            pdf.set_xy(
                start_x + left_w + 3,
                current_y + 6.5
            )

            pdf.set_font(
                "Arial",
                "",
                8
            )

            pdf.cell(
                right_w - 6,
                4,
                person.get(
                    "jabatan",
                    ""
                )
            )

            current_y += row_h

        pdf.set_y(
            y_start + group_height
        )

    # ==================================================
    # CATATAN
    # ==================================================

    pdf.ln(6)

    pdf.set_x(20)

    pdf.set_font(
        "Arial",
        "I",
        8
    )

    pdf.multi_cell(
        170,
        4,
        "Catatan : Tanda tangan persetujuan dokumen ini "
        "mengacu pada Dokumen Halaman Approval yang "
        "diterbitkan pada dokumen terpisah dan merupakan "
        "bagian yang tidak terpisahkan dari dokumen ini."
    )

# ======================================Daftar Isi============================================#


def add_daftar_isi(pdf, page_tracker):
    pdf.set_font("Arial", "B", 14)
    pdf.set_x(20)
    pdf.cell(170, 8, "Daftar Isi", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "", 11)

    def row(text, page):
        x = 20
        total_width = 170
        page_width = 20  # area khusus nomor kanan

        text_width = pdf.get_string_width(text)
        dot_width = pdf.get_string_width(".")

        # sisa untuk titik
        dots_width = total_width - page_width - text_width - 2
        dots_count = int(dots_width / dot_width)

        dots = "." * max(dots_count, 0)

        # kiri (text + dots)
        pdf.set_x(x)
        pdf.cell(total_width - page_width, 6, f"{text} {dots}", border=0)

        # kanan (page number rata kanan)
        pdf.cell(page_width, 6, str(page), align="R", ln=True)

    # FIXED
    row("Kontrol Perubahan Dokumen", 2)
    row("Lembar Pengesahan", 3)
    row("Daftar Isi", 4)

    # DYNAMIC SECTION
    # =========================
    sections = []

    sections.append(("Testing Information", page_tracker.get("testing_info")))

    # 🔥 kalau SIT ada deskripsi
    if "deskripsi" in page_tracker:
        sections.append(("Deskripsi", page_tracker.get("deskripsi")))

    sections.append(("Rangkuman Hasil Testing", page_tracker.get("rangkuman")))
    sections.append(("Detail Hasil Testing", page_tracker.get("detail")))
    sections.append(("Analisis Hasil Testing", page_tracker.get("analisis")))
    sections.append(("Kesimpulan Hasil Testing",
                    page_tracker.get("kesimpulan")))

    # render dengan nomor otomatis
    for i, (title, page) in enumerate(sections, 1):
        row(f"{i}. {title}", page)
# =========================================Testing Information===============#


def draw_table_auto_wrap(pdf, rows, x_start, left_w=55, cell_height=6):

    page_width = pdf.w
    right_margin = 20

    # ✅ TOTAL LEBAR AREA TABEL = 165mm
    table_width = page_width - x_start - right_margin

    # ✅ SISA UNTUK KOLOM KANAN
    right_w = table_width - left_w

    pdf.set_draw_color(0, 0, 0)

    for key, value in rows:
        y_start = pdf.get_y()

        # ===== HITUNG HEIGHT =====
        pdf.set_font("Arial", "", 10)
        val_lines = pdf.multi_cell(
            right_w - 4, cell_height, str(value), split_only=True)
        val_height = len(val_lines) * cell_height

        pdf.set_font("Arial", "B", 10)
        key_lines = pdf.multi_cell(
            left_w - 4, cell_height, str(key), split_only=True)
        key_height = len(key_lines) * cell_height

        row_height = max(val_height, key_height, cell_height)

        # ===== LEFT =====
        pdf.set_fill_color(12, 44, 99)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)

        pdf.rect(x_start, y_start, left_w, row_height, 'F')
        pdf.rect(x_start, y_start, left_w, row_height)

        text_h = len(key_lines) * cell_height
        y_text = y_start + (row_height - text_h) / 2

        pdf.set_xy(x_start + 2, y_text)
        pdf.multi_cell(left_w - 4, cell_height, str(key))

        # ===== RIGHT =====
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)

        x_right = x_start + left_w
        pdf.rect(x_right, y_start, right_w, row_height)

        text_h = len(val_lines) * cell_height
        y_text = y_start + (row_height - text_h) / 2

        pdf.set_xy(x_right + 2, y_text)
        pdf.multi_cell(right_w - 4, cell_height, str(value))

        # 🔥 RESET POSISI
        pdf.set_xy(x_start, y_start + row_height)


def add_testing_information(pdf, detail_project, tester_name, section_no):
    pdf.add_page()
    pdf.set_y(37)

    LEFT_NUM = 20
    LEFT_TEXT = 25

    # ===== TITLE =====
    pdf.set_font("Arial", "B", 12)

    # angka
    pdf.set_x(LEFT_NUM)
    pdf.cell(5, 6, f"{section_no}.", 0, 0)

    # teks
    pdf.set_x(LEFT_TEXT)
    pdf.cell(0, 6, "Testing Information", ln=True)

    pdf.ln(3)

    info = detail_project.get("testing_information", {})

    rows = [
        ["Project/Bugs/Tuning Code", detail_project.get("project_code", "")],
        ["Project/Bugs/Tuning Name", detail_project.get("project_name", "")],
        ["Waktu Testing", info.get("waktu_testing", "")],
        ["Tester", tester_name],
    ]

    # ===== TABLE =====
    draw_table_auto_wrap(pdf, rows, x_start=LEFT_TEXT)

# ===================Rangkuman Hasil Testing===============#


def draw_rangkuman_header(pdf, x, col_reg, col_tc, col_ts, col_def, col_status):

    pdf.set_fill_color(47, 64, 91)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)

    # ===== ROW 1 =====
    pdf.set_x(x)

    pdf.cell(col_reg, 16, "REG ID", border=1, align="C", fill=True)

    # jumlah total (atas saja)
    pdf.cell(col_tc + col_ts + col_def, 8, "Jumlah Total",
             border=1, align="C", fill=True)

    pdf.cell(col_status, 16, "Status Defect",
             border=1, align="C", fill=True)

    pdf.ln()

    # ===== ROW 2 =====
    pdf.set_x(x + col_reg)

    # 🔥 INI YANG PENTING → nutup area kosong
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(col_tc + col_ts + col_def, 8, "", border=1)

    pdf.ln(-8)  # balik ke posisi row 2

    pdf.set_fill_color(47, 64, 91)
    pdf.set_text_color(255, 255, 255)

    pdf.set_x(x + col_reg)

    pdf.cell(col_tc, 8, "Test Case", border=1, align="C", fill=True)
    pdf.cell(col_ts, 8, "Test Step", border=1, align="C", fill=True)
    pdf.cell(col_def, 8, "Defect", border=1, align="C", fill=True)

    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)

# =========================
# SUMMARY DATA GENERATOR
# =========================


def generate_summary_per_reg(all_cases):
    summary = {}

    for case in all_cases:
        reg_id = case.get("reg_id", "REG-UNKNOWN")

        if reg_id not in summary:
            summary[reg_id] = {
                "testcase": 0,
                "teststep": 0,
                "defect": 0
            }

        summary[reg_id]["testcase"] += 1
        summary[reg_id]["teststep"] += len(case.get("test_steps", []))

        if case.get("status") == "Not Passed":
            summary[reg_id]["defect"] = 1

    # 🔥 FIX: convert ke list
    result = []
    for reg, data in summary.items():
        result.append({
            "reg_id": reg,
            "testcase": data["testcase"],
            "teststep": data["teststep"],
            "defect": data["defect"],
            "status": "OPEN" if data["defect"] == 1 else "CLOSED"
        })

    return result

# =========================
# MAIN TABLE FUNCTION
# =========================


def add_rangkuman_hasil_testing(pdf, summary_data, section_no):

    pdf.ln(5)

    if pdf.get_y() + 40 > pdf.h - 25:
        pdf.add_page()
        pdf.set_y(37)
        pdf.set_auto_page_break(auto=True, margin=15)

    LEFT_NUM = 20
    LEFT_TEXT = 25

    # ===== TITLE =====
    pdf.set_font("Arial", "B", 12)

    # angka section
    pdf.set_x(LEFT_NUM)
    pdf.cell(5, 6, f"{section_no}.", 0, 0)

    # judul
    pdf.set_x(LEFT_TEXT)
    pdf.cell(0, 6, "Rangkuman Hasil Testing", ln=True)

    pdf.ln(3)
    # ===== TABLE POSITION =====
    x = LEFT_TEXT

    col_reg = 35
    col_tc = 30
    col_ts = 30
    col_def = 30
    col_status = 40

    # ===== HEADER =====
    def draw_header():
        pdf.set_fill_color(47, 64, 91)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)

        pdf.set_x(x)

        # ROW 1
        pdf.cell(col_reg, 16, "REG ID", 1, 0, "C", True)
        pdf.cell(col_tc + col_ts + col_def, 8, "Jumlah Total", 1, 0, "C", True)
        pdf.cell(col_status, 16, "Status Defect", 1, 0, "C", True)

        pdf.ln(8)

        # ROW 2
        pdf.set_x(x + col_reg)
        pdf.cell(col_tc, 8, "Test Case", 1, 0, "C", True)
        pdf.cell(col_ts, 8, "Test Step", 1, 0, "C", True)
        pdf.cell(col_def, 8, "Defect", 1, 0, "C", True)

        pdf.ln(8)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)

    draw_header()

    # ===== DATA =====
    row_height = 8
    bottom_limit = pdf.h - 25

    for row in summary_data:

        if pdf.get_y() + row_height > bottom_limit:
            pdf.add_page()
            pdf.ln(10)
            draw_header()

        pdf.set_x(x)

        pdf.cell(col_reg, row_height, row["reg_id"], 1, 0, "C")
        pdf.cell(col_tc, row_height, str(row["testcase"]), 1, 0, "C")
        pdf.cell(col_ts, row_height, str(row["teststep"]), 1, 0, "C")
        pdf.cell(col_def, row_height, str(row["defect"]), 1, 0, "C")

        # warna status
        if row["status"] == "OPEN":
            pdf.set_text_color(255, 0, 0)
        else:
            pdf.set_text_color(0, 128, 0)

        pdf.cell(col_status, row_height, row["status"], 1, 0, "C")

        pdf.set_text_color(0, 0, 0)
        pdf.ln()
# =================================Detail Hasil Testing======================#


def count_lines(pdf, text, col_width):
    words = text.split(' ')
    lines = 1
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if pdf.get_string_width(test_line) < col_width:
            current_line = test_line
        else:
            lines += 1
            current_line = word

    return lines


def generate_summary_per_fitur(all_cases):
    summary = {}

    for case in all_cases:
        reg = case.get("reg_id")
        fitur = case.get("fitur", "").strip().lower()

        key = (reg, fitur)

        if key not in summary:
            summary[key] = {
                "testcase": 0,
                "passed": 0,
                "failed": 0
            }

        summary[key]["testcase"] += 1

        status = case.get("status", "").upper()

        if status in ["FAILED", "NOT PASSED"]:
            summary[key]["failed"] += 1
        else:
            summary[key]["passed"] += 1

    return summary


def add_detail_hasil_testing(pdf, all_cases, section_no):

    pdf.add_page(orientation='L')
    pdf.set_y(37)

    LEFT_NUM = 20
    LEFT_TEXT = 25

    # ===== TITLE =====
    pdf.set_font("Arial", "B", 14)
    pdf.set_x(LEFT_NUM)
    pdf.cell(5, 8, f"{section_no}.", 0, 0)

    pdf.set_x(LEFT_TEXT)
    pdf.cell(0, 8, "Detail Hasil Testing", ln=True)
    pdf.ln(3)

    x = LEFT_TEXT

    col = [25, 40, 0, 25, 25, 20, 20, 30]

    page_width = pdf.w
    right_margin = 20

    fixed_width = col[0] + col[1] + col[3] + col[4] + col[5] + col[6] + col[7]
    col[2] = page_width - x - fixed_width - right_margin

    # ================= HEADER =================
    def draw_header():
        pdf.set_fill_color(47, 64, 91)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)

        start_x = x
        start_y = pdf.get_y()

        pdf.set_xy(start_x, start_y)

        pdf.cell(col[0], 16, "REG ID", 1, 0, "C", True)
        pdf.cell(col[1], 16, "Modul", 1, 0, "C", True)
        pdf.cell(col[2], 16, "Fitur", 1, 0, "C", True)

        pdf.cell(col[3] + col[4], 8, "Jumlah Test Case", 1, 0, "C", True)
        pdf.cell(col[5] + col[6], 8, "Result", 1, 0, "C", True)

        pdf.cell(col[7], 16, "Tester", 1, 0, "C", True)

        pdf.set_xy(start_x + col[0] + col[1] + col[2], start_y + 8)

        pdf.cell(col[3], 8, "Planned", 1, 0, "C", True)
        pdf.cell(col[4], 8, "Actual", 1, 0, "C", True)
        pdf.cell(col[5], 8, "Passed", 1, 0, "C", True)
        pdf.cell(col[6], 8, "Failed", 1, 0, "C", True)

        pdf.set_y(start_y + 16)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 9)

    draw_header()

    # ================= GROUPING =================
    grouped = {}

    for case in all_cases:
        reg = case.get("reg_id", "-")
        modul = case.get("module_name", "-")
        fitur = case.get("fitur", "").strip()

        key = (reg, modul, fitur)

        if key not in grouped:
            grouped[key] = {
                "testcase": 0,
                "passed": 0,
                "failed": 0,
                "testers": set()
            }

        grouped[key]["testcase"] += 1

        if case.get("tester_name"):
            grouped[key]["testers"].add(str(case.get("tester_name")).strip())

        status = case.get("status", "").upper()

        if status in ["FAILED", "NOT PASSED"]:
            grouped[key]["failed"] += 1
        else:
            grouped[key]["passed"] += 1

    sorted_keys = sorted(grouped.keys())
    bottom_limit = pdf.h - 25
    # ================= GROUP ROWSPAN =================
    rowspan_info = {}

    for key in sorted_keys:
        reg, modul, fitur = key

        group_key = (reg, modul)

        rowspan_info[group_key] = (
            rowspan_info.get(group_key, 0) + 1
        )
    # ================= RENDER =================
    processed_group = set()

    for (reg, modul, fitur) in sorted_keys:

        data = grouped[(reg, modul, fitur)]

        tester_text = ", ".join(
            sorted(data["testers"])) if data["testers"] else "-"

        planned = data["testcase"]
        actual = planned
        passed = data["passed"]
        failed = data["failed"]

        # ===== HITUNG SEMUA HEIGHT =====
        modul_lines = pdf.multi_cell(col[1] - 2, 5, modul, split_only=True)
        modul_h = len(modul_lines) * 5

        fitur_lines = pdf.multi_cell(col[2] - 2, 5, fitur, split_only=True)
        fitur_h = len(fitur_lines) * 5

        tester_lines = pdf.multi_cell(
            col[7] - 2, 5, tester_text, split_only=True)
        tester_h = len(tester_lines) * 5

        row_h = max(modul_h, fitur_h, tester_h, 8)

        # ===== PAGE BREAK =====
        if pdf.get_y() + row_h > bottom_limit:
            pdf.add_page(orientation='L')
            pdf.ln(10)
            draw_header()

        y_start = pdf.get_y()
        pdf.set_xy(x, y_start)

        group_key = (reg, modul)

        # ===== REG + MODUL ROWSPAN =====
        if group_key not in processed_group:

            rowspan = rowspan_info[group_key]
            total_height = row_h * rowspan

            # ===== REG =====
            pdf.cell(col[0], total_height, str(reg), 1, 0, "C")

            # ===== MODUL =====
            x_current = pdf.get_x()
            y_current = pdf.get_y()

            pdf.rect(x_current, y_current, col[1], total_height)

            y_text = y_current + (total_height / 2) - 3

            pdf.set_xy(x_current, y_text)
            pdf.multi_cell(col[1], 6, modul, align="C")

            # 🔥 reset posisi setelah multicell
            pdf.set_xy(x_current + col[1], y_current)

            processed_group.add(group_key)

        else:
            pdf.set_x(x + col[0] + col[1])

        # ===== FITUR (WRAP) =====
        x_current = pdf.get_x()
        y_current = pdf.get_y()

        pdf.rect(x_current, y_current, col[2], row_h)

        y_text = y_current + (row_h - fitur_h) / 2

        pdf.set_xy(x_current, y_text)
        pdf.multi_cell(col[2] - 2, 5, fitur)

        pdf.set_xy(x_current + col[2], y_current)

        # ===== ANGKA =====
        pdf.cell(col[3], row_h, str(planned), 1, 0, "C")
        pdf.cell(col[4], row_h, str(actual), 1, 0, "C")
        pdf.cell(col[5], row_h, str(passed), 1, 0, "C")
        pdf.cell(col[6], row_h, str(failed), 1, 0, "C")

        # ===== TESTER (WRAP) =====
        x_current = pdf.get_x()
        y_current = pdf.get_y()

        pdf.rect(x_current, y_current, col[7], row_h)

        y_text = y_current + (row_h - tester_h) / 2

        pdf.set_xy(x_current, y_text)
        pdf.multi_cell(col[7] - 2, 5, tester_text, align="C")

        pdf.set_xy(x_current + col[7], y_current)

        pdf.ln(row_h)
# =================================Analisis Hasil Tesing===================#


def get_failed_cases(all_cases):
    return [
        case for case in all_cases
        if case.get("status") == "Not Passed"
    ]


def group_by_severity(failed_cases):
    result = {"High": [], "Medium": [], "Low": []}

    for case in failed_cases:
        sev = case.get("severity", "Medium")
        result.setdefault(sev, []).append(case)

    return result


# ========================= HELPER =========================
def auto_break(pdf, needed=30, bottom=25):
    if pdf.get_y() + needed > pdf.h - bottom:
        pdf.add_page()
        pdf.ln(10)


# ========================= ANALISIS =========================
def add_analisis_hasil_testing(pdf, all_cases, section_no):

    pdf.add_page()
    pdf.set_y(37)
    pdf.set_auto_page_break(auto=True, margin=15)

    LEFT_NUM = 20
    LEFT_TEXT = 25

    # ===== TITLE =====
    pdf.set_font("Arial", "B", 12)

    pdf.set_x(LEFT_NUM)
    pdf.cell(5, 6, f"{section_no}.", 0, 0)

    pdf.set_x(LEFT_TEXT)
    pdf.cell(0, 6, "Analisis Hasil Testing", ln=True)

    pdf.ln(3)

    failed_cases = get_failed_cases(all_cases)

    # ================= ADA DEFECT =================
    if failed_cases:
        pdf.set_font("Arial", "", 10)

        total_failed = len(failed_cases)

        pdf.set_x(LEFT_TEXT)
        pdf.multi_cell(
            pdf.w - LEFT_TEXT - 20,
            6,
            f"Berdasarkan dari hasil Regresi yang telah dilakukan, terdapat {total_failed} test case yang failed, dengan detail sebagai berikut:"
        )

        pdf.ln(3)

        x = LEFT_TEXT
        col = [30, 35, 70, 30]  # width kolom

        # ===== HEADER =====
        auto_break(pdf, 20)

        pdf.set_fill_color(47, 64, 91)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)

        pdf.set_x(x)
        headers = ["Severity", "TestCase-ID",
                   "Deskripsi Defect/Bugs", "Status"]

        for i, h in enumerate(headers):
            pdf.cell(col[i], 8, h, border=1, align="C", fill=True)
        pdf.ln()

        # ===== DATA =====
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 9)

        grouped = group_by_severity(failed_cases)

        for severity in ["High", "Medium", "Low"]:
            cases = grouped.get(severity, [])

            if not cases:
                continue

            # ===== HITUNG HEIGHT PER ROW =====
            row_heights = []

            for case in cases:

                desc = case.get("actual_result") or "-"

                # ===== LIMIT DESKRIPSI =====
                if len(desc) > 250:
                    desc = desc[:250] + "..."

                lines = pdf.multi_cell(
                    col[2] - 2,
                    5,
                    desc,
                    split_only=True
                )

                text_h = len(lines) * 5

                row_heights.append(max(text_h, 6))

            total_height = sum(row_heights)

            # ===== AUTO PAGE BREAK UNTUK GROUP =====
            if pdf.get_y() + total_height > pdf.page_break_trigger:

                pdf.add_page()
                pdf.set_y(30)

                # ===== REDRAW HEADER =====
                pdf.set_fill_color(47, 64, 91)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Arial", "B", 10)

                pdf.set_x(x)

                headers = [
                    "Severity",
                    "TestCase-ID",
                    "Deskripsi Defect/Bugs",
                    "Status"
                ]

                for idx, h in enumerate(headers):
                    pdf.cell(col[idx], 8, h, border=1, align="C", fill=True)

                pdf.ln()

                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", "", 9)

            # ===== PRINT ROW =====
            for i, case in enumerate(cases):

                row_h = row_heights[i]

                auto_break(pdf, row_h)

                pdf.set_x(x)

                y_start = pdf.get_y()

                # ===== SEVERITY (MERGED CELL) =====
                if i == 0:

                    pdf.rect(x, y_start, col[0], total_height)

                    pdf.set_xy(
                        x,
                        y_start + total_height / 2 - 3
                    )

                    pdf.cell(
                        col[0],
                        6,
                        severity,
                        align="C"
                    )

                # ===== TESTCASE =====
                x_tc = x + col[0]

                pdf.rect(
                    x_tc,
                    y_start,
                    col[1],
                    row_h
                )

                tc_text = case.get("testcase_id", "-")

                lines = pdf.multi_cell(
                    col[1] - 2,
                    5,
                    tc_text,
                    split_only=True
                )

                text_h = len(lines) * 5

                y_text = y_start + (row_h - text_h) / 2

                pdf.set_xy(
                    x_tc + 1,
                    y_text
                )

                pdf.multi_cell(
                    col[1] - 2,
                    5,
                    tc_text,
                    align="C"
                )

                # ===== DESKRIPSI =====
                x_desc = x_tc + col[1]

                desc = case.get("actual_result") or "-"

                # ===== LIMIT DESKRIPSI =====
                if len(desc) > 250:
                    desc = desc[:250] + "..."

                pdf.rect(
                    x_desc,
                    y_start,
                    col[2],
                    row_h
                )

                lines = pdf.multi_cell(
                    col[2] - 2,
                    5,
                    desc,
                    split_only=True
                )

                text_h = len(lines) * 5

                y_text = y_start + (row_h - text_h) / 2

                pdf.set_xy(
                    x_desc + 1,
                    y_text
                )

                pdf.multi_cell(
                    col[2] - 2,
                    5,
                    desc
                )

                # ===== STATUS =====
                x_status = x_desc + col[2]

                pdf.rect(
                    x_status,
                    y_start,
                    col[3],
                    row_h
                )

                pdf.set_xy(
                    x_status,
                    y_start + (row_h - 6) / 2
                )

                pdf.cell(
                    col[3],
                    6,
                    "Failed",
                    align="C"
                )

                pdf.set_y(y_start + row_h)

        pdf.ln(3)

    # ================= TIDAK ADA DEFECT =================
    else:
        pdf.set_font("Arial", "", 10)

        pdf.set_x(LEFT_TEXT)
        pdf.multi_cell(
            pdf.w - LEFT_TEXT - 25,
            6,
            "Berdasarkan dari hasil Testing yang telah dilakukan, tidak ditemukan test case yang failed, dengan detail sebagai berikut:"
        )

        pdf.ln(3)

        x = LEFT_TEXT
        col = [80, 80]

        auto_break(pdf, 20)

        pdf.set_fill_color(47, 64, 91)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)

        pdf.set_x(x)
        pdf.cell(col[0], 8, "Severity", border=1, align="C", fill=True)
        pdf.cell(col[1], 8, "Jumlah Temuan",
                 border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 10)

        for sev in ["High", "Medium", "Low"]:
            auto_break(pdf, 10)

            pdf.set_x(x)
            pdf.cell(col[0], 8, sev, border=1)
            pdf.cell(col[1], 8, "0", border=1, align="C")
            pdf.ln()

# ========================= KESIMPULAN =========================


def generate_kesimpulan(all_cases):
    total = len(all_cases)
    failed = sum(1 for c in all_cases if c.get("status") == "Not Passed")

    if failed == 0:
        return {
            "status": "PASSED",
            "text": (
                f"Pelaksanaan Testing untuk aplikasi/sistem telah dilakukan dengan total {total} test case, "
                "dan seluruh test case dinyatakan PASSED. "
                "Dengan demikian, sistem dinyatakan stabil dan dapat dilanjutkan ke tahap berikutnya."
            )
        }
    else:
        return {
            "status": "NOT PASSED",
            "text": (
                f"Pelaksanaan Testing untuk aplikasi/sistem telah dilakukan dengan total {total} test case, "
                f"dimana terdapat {failed} test case yang tidak sesuai (Not Passed). "
                "Diperlukan perbaikan terhadap defect yang ditemukan sebelum sistem dapat dilanjutkan ke tahap berikutnya."
            )
        }


def add_kesimpulan_hasil_testing(pdf, all_cases, section_no):

    pdf.ln(5)

    auto_break(pdf, 20)

    LEFT_NUM = 20
    LEFT_TEXT = 25
    RIGHT_MARGIN = 20

    # ===== TITLE =====
    pdf.set_font("Arial", "B", 12)

    pdf.set_x(LEFT_NUM)
    pdf.cell(5, 6, f"{section_no}.", 0, 0)

    pdf.set_x(LEFT_TEXT)
    pdf.cell(0, 6, "Kesimpulan Hasil Testing", ln=True)

    pdf.ln(3)

    # ===== CONTENT =====
    result = generate_kesimpulan(all_cases)

    pdf.set_font("Arial", "", 10)

    # 🔥 hitung width aman
    usable_width = pdf.w - LEFT_TEXT - RIGHT_MARGIN

    pdf.set_x(LEFT_TEXT)
    pdf.multi_cell(
        usable_width,
        6,  # 🔥 line height ideal
        result["text"]
    )
    pdf.set_x(LEFT_TEXT)
# ========== Simpan Screenshoot ========== #


def save_screenshot(
        page,
        selector=None,
        base_name="screenshot",
        highlight=False,
        testcase_id=None,
        testcase_name=None):

    if testcase_name is None:
        testcase_name = "Unknown"

    # ===== Buat folder =====
    folder = os.path.join(
        f"{testcase_id}_{testcase_name.replace(' ', '_')}",
        "Screenshots"
    )
    os.makedirs(folder, exist_ok=True)

    waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{waktu}.png"
    path = os.path.join(folder, filename)

    # ===== Highlight multiple selector =====
    if highlight and selector:
        if isinstance(selector, list):
            for sel in selector:
                if hasattr(sel, "evaluate"):  # kalau ini Locator
                    sel.evaluate("el => el.style.border='3px solid red'")
                else:  # kalau ini selector string
                    page.eval_on_selector(
                        sel, "el => el.style.border='3px solid red'")
        else:
            sel = selector
            if hasattr(sel, "evaluate"):  # Locator
                sel.evaluate("el => el.style.border='3px solid red'")
            else:  # selector string
                page.eval_on_selector(
                    sel, "el => el.style.border='3px solid red'")
        page.wait_for_timeout(200)

    page.screenshot(path=path)

    # ===== Tambah border hitam =====
    img = Image.open(path)
    suffix = "_highlight" if highlight else "_border"
    bordered_path = f"{os.path.splitext(path)[0]}{suffix}.png"

    bordered_img = ImageOps.expand(img, border=2, fill='black')
    bordered_img.save(bordered_path)

    os.remove(path)

    print(f"Screenshot disimpan di: {bordered_path}")
    return bordered_path

# ============Class PDF ============ #


class CustomPDF(FPDF):
    def __init__(
        self,
        show_page_number=False,
        ba_title="BA Regression Testing",
        use_cover=True
    ):
        super().__init__()
        # Daftarkan font Arial Regular dan Bold agar mendukung Unicode
        self.add_font("Arial", "", "Automation_Report/arial.ttf", uni=True)
        self.add_font("Arial", "B", "Automation_Report/arialbd.ttf", uni=True)
        # -------------------------
        self.show_page_number = show_page_number
        self.ba_title = ba_title
        self.use_cover = use_cover
        self.header_mode = "NORMAL"

    # =========================
    # HEADER (HALAMAN 2+)
    # =========================
    def header(self):

        if self.use_cover and self.page_no() == 1:
            return

        if self.header_mode == "TABLE":
            self.draw_table_header()
        else:
            self.draw_normal_header()

    def draw_normal_header(self):
        # skip header hanya jika pakai cover
        if self.use_cover and self.page_no() == 1:
            return

        page_margin = 20
        page_width = self.w
        logo_width = 40
        logo_height_max = 20
        top_y = 15

        try:
            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(
                base_dir, "Automation_Report", "logo_askrindo.png")

            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img_w, img_h = img.size
                aspect_ratio = img_h / img_w

                draw_w = logo_width
                draw_h = draw_w * aspect_ratio

                if draw_h > logo_height_max:
                    draw_h = logo_height_max
                    draw_w = draw_h / aspect_ratio

                # LOGO
                img_x = page_width - page_margin - draw_w
                self.image(logo_path, x=img_x, y=top_y, w=draw_w, h=draw_h)

                # TITLE
                self.set_xy(page_margin, top_y + (draw_h / 2) - 5)
                self.set_font("Arial", 'B', 14)
                self.cell(
                    img_x - page_margin - 5,
                    10,
                    self.ba_title,
                    align='L'
                )

        except Exception as e:
            print(f"[ERROR] Header gagal: {e}")

        self.ln(30)

    def draw_table_header(self):

        self.set_draw_color(0, 0, 0)

        # =========================
        # HEADER SIZE
        # =========================
        x = 20
        y = 10

        logo_w = 40
        center_w = 100
        right_w = 30

        row_h = 7

        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        logo_path = os.path.join(
            base_dir,
            "Automation_Report",
            "logo_askrindo.png"
        )

        # =========================
        # LOGO
        # =========================
        self.rect(x, y, logo_w, row_h * 3)

        if os.path.exists(logo_path):

            logo_img_w = 36

            logo_x = x + ((logo_w - logo_img_w) / 2)

            self.image(
                logo_path,
                x=logo_x,
                y=y + 2,
                w=logo_img_w
            )

        # =========================
        # CENTER
        # =========================
        self.rect(x + logo_w, y, center_w, row_h)
        self.rect(x + logo_w, y + row_h, center_w, row_h)
        self.rect(x + logo_w, y + (row_h * 2), center_w, row_h)

        self.set_font("Arial", "", 10)

        self.set_xy(x + logo_w, y + 0.5)
        self.cell(center_w, row_h, "ASKRINDO", align="C")

        self.set_xy(x + logo_w, y + row_h + 0.5)
        self.cell(center_w, row_h, "LAPORAN HASIL PENGUJIAN", align="C")

        self.set_xy(x + logo_w, y + (row_h * 2) + 0.5)
        self.cell(center_w, row_h, "AUTOMATION ACS", align="C")

        # =========================
        # RIGHT
        # =========================
        self.rect(
            x + logo_w + center_w,
            y,
            right_w,
            row_h * 3
        )

        jenis = "REGRESSION"

        if "SIT" in self.ba_title.upper():
            jenis = "SIT"
        elif "UAT" in self.ba_title.upper():
            jenis = "UAT"
        elif "SMOKE" in self.ba_title.upper():
            jenis = "SMOKE"

        self.set_font("Arial", "", 10)

        self.set_xy(
            x + logo_w + center_w,
            y + ((row_h * 3) - row_h) / 2
        )

        self.cell(
            right_w,
            row_h,
            jenis,
            align="C"
        )

        self.ln(26)
    # =========================
    # FOOTER (OPTIONAL)
    # =========================

    def footer(self):

        # skip cover page
        if self.use_cover and self.page_no() == 1:
            return

        box_width = 12
        box_height = 10
        right_margin = 15
        page_margin = 20

        x_box = self.w - right_margin - box_width
        y_box = self.h - 16

        # ===== GARIS =====
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)

        y_line = y_box + 0.2

        self.line(page_margin, y_line, x_box + box_width, y_line)

        # ===== KOTAK =====
        self.set_xy(x_box, y_box)
        self.set_fill_color(12, 44, 99)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 9)

        # dengan nomor halaman
        if self.show_page_number:
            text = str(self.page_no())

        # tanpa nomor halaman
        else:
            text = ""

        self.cell(
            box_width,
            box_height,
            text,
            border=0,
            align='C',
            fill=True
        )


def safe_add_images(
    pdf,
    image_paths,
    top_margin=35,
    bottom_margin=20,
    border=True,
    border_width=0.2
):
    if not image_paths:
        return

    if isinstance(image_paths, str):
        image_paths = [image_paths]

    FIXED_WIDTH = 170        # 🔥 Lebar fix 170mm
    left_margin = 20         # 🔥 Hardcode margin kiri 20mm

    for path in image_paths:
        if not path or not os.path.exists(path):
            continue

        try:
            with Image.open(path) as img:
                img_w, img_h = img.size

                # Scale proporsional
                ratio = FIXED_WIDTH / img_w
                display_w = FIXED_WIDTH
                display_h = img_h * ratio

                y_now = pdf.get_y()
                space_left = pdf.h - y_now - bottom_margin

                # Page break jika tidak muat
                if display_h > space_left:
                    pdf.add_page()
                    pdf.set_y(top_margin)
                    y_now = pdf.get_y()

                # Border
                if border:
                    pdf.set_line_width(border_width)
                    pdf.rect(
                        left_margin,
                        y_now,
                        display_w,
                        display_h
                    )

                # Insert image
                pdf.image(
                    path,
                    x=left_margin,
                    y=y_now,
                    w=display_w,
                    h=display_h
                )

                pdf.set_y(y_now + display_h + 5)

        except Exception as e:
            print(f"[Warning] Gagal tampilkan gambar {path}: {e}")


def cleanup_screenshots(screenshot_paths):
    """
    Hapus semua screenshot beserta foldernya jika sudah kosong.
    Mendukung list maupun nested list.
    """

    if not screenshot_paths:
        return

    all_paths = []

    # Flatten list
    for item in screenshot_paths:
        if isinstance(item, list):
            all_paths.extend(item)
        else:
            all_paths.append(item)

    # Hapus file
    for img in all_paths:
        try:
            if img and os.path.exists(img):
                os.remove(img)
                print(f"[INFO] File dihapus: {img}")
        except Exception as e:
            print(f"[WARNING] Gagal hapus file {img}: {e}")

    # Hapus folder kosong
    folders = {
        os.path.dirname(p)
        for p in all_paths
        if p
    }

    for folder in folders:
        try:
            if os.path.exists(folder) and not os.listdir(folder):
                shutil.rmtree(folder)
                print(f"[INFO] Folder dibersihkan: {folder}")
        except Exception as e:
            print(f"[WARNING] Gagal hapus folder {folder}: {e}")


def generate_pdf_report(
        test_steps_rendered=None,
        testcase_id=None,
        testcase_name=None,
        expected_result=None,
        actual_result=None,
        tester_name=None,
        status=None,
        screenshot_paths=None,
        database_verifications=None,
        failed_step_index=None,
        jenis_test=None,
        testdata=None,
        keterangan=None,
        precondition=None,
        show_page_number=False,
        all_cases=None,
        use_cover=False,
        ba_title="BA System Integration Testing (SIT)",
        deskripsi=None,
        test_script_link=None,
        report_title=""):

    # =========================
    # MODE MULTI CASE (BATCH)
    # =========================
    if all_cases:
        pdf = CustomPDF(
            show_page_number=show_page_number,
            ba_title=ba_title,
            use_cover=use_cover
        )
        pdf.header_mode = "NORMAL"
        pdf.set_auto_page_break(auto=True, margin=25)

        page_tracker = {}
        section_no = 1

        # ===== COVER =====
        if use_cover:
            add_cover_page(pdf, detail_project, report_title, ba_title)

            add_kontrol_perubahan(pdf, detail_project)
            add_lembar_pengesahan(pdf, detail_project)

            pdf.add_page()
            toc_page = pdf.page_no()

            testers = list(set(
                str(c.get("tester_name") or "").strip()
                for c in all_cases
                if c.get("tester_name")
            ))

            tester_text = ", ".join(sorted(testers)) if testers else "-"

            section_no = 1
            page_tracker = {}

            # =========================
            # 1. TESTING INFORMATION
            # =========================
            add_testing_information(
                pdf, detail_project, tester_text, section_no)
            page_tracker["testing_info"] = pdf.page_no()
            section_no += 1

            # =========================
            # 2. DESKRIPSI (SIT ONLY)
            # =========================
            if "SIT" in ba_title.upper() and deskripsi:

                pdf.ln(5)

                # optional page break
                if pdf.get_y() + 40 > pdf.h - 25:
                    pdf.add_page()
                    pdf.set_y(37)

                pdf.set_font("Arial", "B", 12)

                pdf.set_x(20)
                pdf.cell(5, 6, f"{section_no}.", 0, 0)

                pdf.set_x(25)
                pdf.cell(0, 6, "Deskripsi", ln=True)

                pdf.ln(4)

                pdf.set_font("Arial", "", 11)
                pdf.set_x(25)
                usable_width = pdf.w - pdf.get_x() - 20
                pdf.multi_cell(usable_width, 6, deskripsi)
                pdf.ln(3)
                page_tracker["deskripsi"] = pdf.page_no()
                section_no += 1
            # =========================
            # 3. RANGKUMAN
            # =========================
            summary_data = generate_summary_per_reg(all_cases)

            add_rangkuman_hasil_testing(pdf, summary_data, section_no)
            page_tracker["rangkuman"] = pdf.page_no()
            section_no += 1

            # =========================
            # 4. DETAIL
            # =========================
            add_detail_hasil_testing(pdf, all_cases, section_no)
            page_tracker["detail"] = pdf.page_no()
            section_no += 1

            # =========================
            # 5. ANALISIS
            # =========================
            add_analisis_hasil_testing(pdf, all_cases, section_no)
            page_tracker["analisis"] = pdf.page_no()
            section_no += 1

            # =========================
            # 6. KESIMPULAN
            # =========================
            add_kesimpulan_hasil_testing(pdf, all_cases, section_no)
            page_tracker["kesimpulan"] = pdf.page_no()
            section_no += 1

            # =========================
            # 7. DOKUMEN HASIL TESTING
            # =========================
            pdf.ln(3)

            LEFT_NUM = 20
            LEFT_TEXT = 25

            pdf.set_font("Arial", "B", 12)

            pdf.set_x(LEFT_NUM)
            pdf.cell(5, 6, f"{section_no}.", 0, 0)

            pdf.set_x(LEFT_TEXT)
            pdf.cell(0, 6, "Dokumen Hasil Testing", ln=True)

            pdf.ln(3)

            pdf.set_font("Arial", "", 10)

            pdf.set_x(LEFT_TEXT)
            pdf.multi_cell(
                165,
                6,
                "Berikut ini link dokumen-dokumen pendukung atas pengujian yang telah dilaksanakan :"
            )

            pdf.ln(3)

            # =========================
            # 1. TEST SCRIPT
            # =========================
            pdf.set_font("Arial", "B", 11)

            pdf.set_x(LEFT_TEXT)
            pdf.cell(
                165,
                6,
                "1. Test Script :",
                ln=True
            )

            pdf.ln(1)

            pdf.set_font("Arial", "U", 11)
            pdf.set_text_color(0, 0, 255)

            pdf.set_x(LEFT_TEXT + 5)

            pdf.multi_cell(
                160,
                6,
                test_script_link,
                link=test_script_link
            )

            pdf.set_text_color(0, 0, 0)

            pdf.ln(3)
            # =========================
            # 2. LAPORAN HASIL PENGUJIAN
            # =========================
            pdf.set_font("Arial", "B", 11)

            pdf.set_x(LEFT_TEXT)
            pdf.cell(
                165,
                6,
                "2. Laporan Hasil Pengujian",
                ln=True
            )

            page_tracker["dokumen_hasil_testing"] = pdf.page_no()
            section_no += 1

            last_page = pdf.page_no()

            pdf.page = toc_page
            pdf.set_xy(20, 40)
            add_daftar_isi(pdf, page_tracker)

            pdf.page = last_page

            pdf.header_mode = "TABLE"

        for case in all_cases:
            pdf.add_page()
            pdf.set_y(37)

            # =========================
            # SUMMARY TABLE
            # =========================
            summary_data1 = [
                ["Test Case Id", case.get("testcase_id")],
                ["Test Case Name", case.get("testcase_name")],
                ["Jenis Test", case.get("jenis_test")],
                ["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Tester", str(case.get("tester_name") or "Automation")],
                ["Status", case.get("status")],
                ["Expected Result", case.get("expected_result")]
            ]

            cell_height = 6
            left_col_width = 40
            right_col_width = 130
            x_start = 20

            for key, value in summary_data1:
                y_start = pdf.get_y()

                if key in ["Test Case Name", "Expected Result"]:
                    def get_text_height(text, width):
                        temp = FPDF()
                        temp.add_page()
                        temp.set_font("Arial", size=10)
                        temp.set_xy(0, 0)
                        temp.multi_cell(width, cell_height, str(text))
                        return temp.get_y()

                    value_height = get_text_height(value, right_col_width)
                    row_height = max(value_height, cell_height)

                    pdf.set_fill_color(12, 44, 99)
                    pdf.rect(x_start, y_start, left_col_width, row_height, 'F')
                    pdf.rect(x_start, y_start, left_col_width, row_height)
                    pdf.rect(x_start + left_col_width, y_start,
                             right_col_width, row_height)

                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font("Arial", "B", 10)
                    pdf.set_xy(x_start, y_start)
                    pdf.multi_cell(left_col_width, cell_height,
                                   str(key), border=0)

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.set_xy(x_start + left_col_width, y_start)
                    pdf.multi_cell(right_col_width, cell_height,
                                   str(value), border=0)

                    pdf.set_y(y_start + row_height)

                else:
                    pdf.set_x(x_start)
                    pdf.set_fill_color(12, 44, 99)

                    pdf.set_text_color(255, 255, 255)
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(left_col_width, cell_height,
                             str(key), border=1, fill=True)

                    pdf.set_text_color(0, 0, 0)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(right_col_width, cell_height,
                             str(value), border=1)
                    pdf.ln()

            pdf.ln(4)

            # =========================
            # PRECONDITION
            # =========================
            if case.get("precondition"):
                pdf.set_font("Arial", "B", 11)
                pdf.set_x(20)
                pdf.cell(170, 6, "Precondition:", ln=True)

                pdf.set_font("Arial", "", 11)
                pdf.set_x(20)
                pdf.multi_cell(170, 5, case.get("precondition"))
                pdf.ln(2)

            if case.get("testdata"):
                pdf.set_font("Arial", "B", 11)
                pdf.set_x(20)
                pdf.cell(170, 6, "Data:", ln=True)

                pdf.set_font("Arial", "", 11)

                label_width = 45
                colon_width = 5
                value_width = 120

                for key, value in case.get("testdata", {}).items():
                    pdf.set_x(20)
                    pdf.cell(label_width, 5, str(key))
                    pdf.cell(colon_width, 5, ":")
                    pdf.multi_cell(value_width, 5, str(value))

                pdf.ln(5)

            # =========================
            # TEST STEPS + IMAGE (ANTI SPLIT)
            # =========================
            steps = case.get("test_steps", [])
            screenshots = case.get("screenshots", [])
            database_verifications = case.get("database_verifications", [])

            for i, step in enumerate(steps):

                # ===== ESTIMASI HEIGHT =====
                step_height = 10
                image_height = 0

                if i < len(screenshots):
                    img_list = screenshots[i] if isinstance(
                        screenshots[i], list) else [screenshots[i]]
                    for img in img_list:
                        if img:
                            image_height += 100

                total_needed = step_height + image_height

                current_y = pdf.get_y()
                max_y = pdf.h - 25

                # ===== PAGE BREAK CHECK =====
                if current_y + total_needed > max_y:
                    pdf.add_page()
                    pdf.set_y(35)

                # ===== PRINT STEP =====
                pdf.set_font("Arial", "", 11)
                pdf.set_x(20)
                pdf.multi_cell(170, 5, step)
                pdf.ln(1)

                # ===== PRINT IMAGE =====
                if i < len(screenshots):
                    safe_add_images(pdf, screenshots[i])
                # ===== DATABASE VERIFICATION =====
                current_step = i + 1
                if database_verifications:
                    db_matches = [
                        db for db in database_verifications
                        if db["step"] == current_step
                    ]

                    for db in db_matches:
                        write_verifikasi_database_flexible(
                            pdf=pdf,
                            query=db["query"],
                            db_result=db["result"]
                        )

                        pdf.ln(3)
            # =========================
            # ACTUAL RESULT (PALING BAWAH)
            # =========================
            pdf.ln(5)

            pdf.set_font("Arial", "B", 11)
            pdf.set_x(20)
            pdf.cell(170, 6, "Actual Result:", ln=True)

            pdf.set_font("Arial", "", 11)
            pdf.set_x(20)
            pdf.multi_cell(170, 5, case.get("actual_result", ""))

            pdf.ln(3)

        # =========================
        # SAVE PDF
        # =========================
        waktu = datetime.now().strftime("%Y%m%d_%H%M%S")

        folder = os.path.join("Automation_Report", "Batch_Report")
        os.makedirs(folder, exist_ok=True)

        filename = f"Automation_Report_Batch_{waktu}.pdf"
        pdf_path = os.path.join(folder, filename)

        pdf.output(pdf_path)

        print(f"[INFO] Batch PDF berhasil disimpan: {pdf_path}")

        # =========================
        # CLEANUP SCREENSHOT BATCH
        # =========================
        all_screenshot_paths = []

        for case in all_cases:
            screenshots = case.get("screenshots", [])
            if screenshots:
                all_screenshot_paths.extend(screenshots)

        cleanup_screenshots(all_screenshot_paths)

        return pdf_path

    # SINGLE - MODE#
    # === Tentukan path logo secara otomatis ===
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(
        base_dir, "Automation_Report", "logo_askrindo.png")
    # -------Simpan Folder PDF-----------#
    waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_base = f"{testcase_id}_{testcase_name.replace(' ', '_')}"
    if status == "Passed":
        folder = os.path.join(
            "Automation_Report", folder_base, "Laporan_Passed")
        nama_file = f"Laporan_Passed_{testcase_name.replace(' ', '_')}_{waktu}.pdf"
    else:
        folder = os.path.join(
            "Automation_Report", folder_base, "Laporan_Failed")
        nama_file = f"Laporan_Failed_{testcase_name.replace(' ', '_')}_{waktu}.pdf"

    os.makedirs(folder, exist_ok=True)  # pastikan folder dibuat
    # Buat nama file PDF
    pdf_path = os.path.join(folder, nama_file)
    print(f"[DEBUG] Folder final: {folder}")
    print(f"[DEBUG] File path: {pdf_path}")
    print(f"[DEBUG] Total path length: {len(pdf_path)}")

    print(f"PDF akan disimpan di: {pdf_path}")
    pdf = CustomPDF(
        show_page_number=show_page_number,
        ba_title=ba_title,
        use_cover=use_cover
    )
    pdf.set_auto_page_break(auto=False)

# ===== Halaman 3: Header, Logo, Ringkasan ===== #
    pdf.add_page()
    # Turunkan cursor setelah header
    pdf.set_y(37)
    summary_data1 = [
        ["Test Case Id", testcase_id],
        ["Test Case Name", testcase_name],
        ["Jenis Test", jenis_test],
        ["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Tester", tester_name],
        ["Status", status],
        ["Expected Result", expected_result]
    ]

    # Ukuran dan posisi
    cell_height = 6
    left_col_width = 40
    right_col_width = 130
    x_start = 20
    for key, value in summary_data1:
        y_start = pdf.get_y()
        if key in ["Test Case Name", "Expected Result"]:
            # Hitung tinggi value saja
            def get_text_height(text, width):
                temp = FPDF()
                temp.add_page()
                temp.set_font("Arial", size=10)
                temp.set_xy(0, 0)
                temp.multi_cell(width, cell_height, str(text))
                return temp.get_y()
            value_height = get_text_height(value, right_col_width)
            row_height = max(value_height, cell_height)
            # Draw background & border untuk key
            pdf.set_fill_color(12, 44, 99)
            pdf.rect(x_start, y_start, left_col_width, row_height, 'F')
            pdf.rect(x_start, y_start, left_col_width, row_height)
            # Draw border untuk value
            pdf.rect(x_start + left_col_width, y_start,
                     right_col_width, row_height)

            # Isi key (PUTIH) tabel biru
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 10)  # Bold
            pdf.set_xy(x_start, y_start)
            pdf.multi_cell(left_col_width, cell_height, str(key), border=0)
            # Balikin ke hitam sebelum isi value
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 10)  # Bold
            # Isi value (HITAM) tabel putih
            pdf.set_xy(x_start + left_col_width, y_start)
            pdf.multi_cell(right_col_width, cell_height, str(value), border=0)
            pdf.set_y(y_start + row_height)
        else:
            pdf.set_x(x_start)
            pdf.set_fill_color(12, 44, 99)
            # Key (PUTIH)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 10)  # Bold
            pdf.cell(left_col_width, cell_height,
                     str(key), border=1, fill=True)
            # Balikin ke hitam
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 10)  # Bold
            # Value (HITAM)
            pdf.cell(right_col_width, cell_height,
                     str(value), border=1)
            pdf.ln()

    # Test Data
    pdf.ln(3)

    if precondition:
        pdf.set_font("Arial", style="B", size=11)

        pdf.set_x(20)
        pdf.cell(170, 6, "Preconditions :", ln=True)

        pdf.set_font("Arial", size=11)
        pdf.set_x(20)
        pdf.multi_cell(170, 5, precondition)

        pdf.ln(3)

    if testdata:
        pdf.set_font("Arial", style="B", size=11)

        pdf.set_x(20)
        pdf.cell(170, 6, "Data :", ln=True)

        pdf.set_font("Arial", size=11)

        label_width = 45
        colon_width = 5
        value_width = 110

        for key, value in testdata.items():
            pdf.set_x(20)
            pdf.cell(label_width, 5, str(key))
            pdf.cell(colon_width, 5, ":")
            pdf.multi_cell(value_width, 5, str(value))

        pdf.ln(3)
# ===== Halaman 4 Content: Test Steps, Screenshot, Payload/Response, DB Query/Data, Verifikasi ===== #
    y_start = 35
    max_y = pdf.h - 25  # bottom margin aman
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.set_font("Arial", size=11)

    # Tentukan index STEP 4
    step4_index = 3  # sesuaikan dengan posisi STEP 4 di test_steps_rendered

    for i, step in enumerate(test_steps_rendered):
        pdf.set_font("Arial", size=11)
        current_y = pdf.get_y()

        # ===== Estimasi tinggi konten =====
        estimated_height = 0

        # 1. Judul step
        estimated_height += 8 + (pdf.get_string_width(step) / 170 * 8)

        # 2. STEP 4 panjang
        if i == step4_index:
            step4_lines = step.count('\n') + 1
            step4_height = step4_lines * 5
            # lebih kecil dari 6 supaya tidak terlalu “mengembang”
            if current_y + step4_height > max_y:
                pdf.add_page()
                pdf.set_y(y_start)
                current_y = y_start

        # 3. Gambar
        image_height = 0
        image_paths = []
        if i < len(screenshot_paths):
            img_list = screenshot_paths[i] if isinstance(
                screenshot_paths[i], list) else [screenshot_paths[i]]
            for img in img_list:
                if img and os.path.exists(img):
                    image_paths.append(img)
                    image_height += 100 + 3  # tinggi + margin bawah
        estimated_height += image_height

        # ===== Cek page break sebelum render =====
        if current_y + estimated_height > max_y:
            pdf.add_page()
            pdf.set_y(y_start)
            current_y = pdf.get_y()

        # ===== Cetak teks step =====
        if failed_step_index is not None and i == failed_step_index:
            pdf.set_text_color(0, 0, 0)  # merah untuk step gagal
        else:
            pdf.set_text_color(0, 0, 0)    # hitam normal

        pdf.set_x(20)
        pdf.multi_cell(170, 8, step, border=0)
        pdf.ln(2)

        # ===== Cetak gambar (pakai safe_add_images) =====
        if image_paths:
            safe_add_images(
                pdf,
                image_paths,
            )
        # ===== ACTUAL RESULT =====
        pdf.ln(5)
        pdf.set_font("Arial", '', 11)

    if status == "Passed":
        pdf.set_text_color(0, 0, 0)
        label = "Actual Result"
    else:
        pdf.set_text_color(200, 0, 0)
        label = "Error Detail"

    full_text = f"{label} : {actual_result}"

    pdf.set_x(20)
    pdf.multi_cell(170, 6, full_text, align='J')

    pdf.set_text_color(0, 0, 0)

    # ===== KETERANGAN =====
    if keterangan:
        pdf.ln(5)

        # margin kiri kanan 20
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)
        pdf.set_x(20)

        # Judul
        pdf.set_font("Arial", 'B', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, "Keterangan :", align='L')

        pdf.ln(1)

        # Cek kalau sudah dekat bawah page → pindah halaman
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.set_x(20)

        # Isi
        pdf.set_font("Arial", '', 10)

        try:
            safe_keterangan = str(keterangan).strip().encode(
                'latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, safe_keterangan, align='L')
        except Exception as e:
            print("[ERROR KETERANGAN]", e)

    # Simpan PDF
    pdf.output(pdf_path)
    # tunggu file image selesai diproses FPDF/PIL
    time.sleep(7)
    print(f"PDF berhasil disimpan ke: {pdf_path}")
    cleanup_screenshots(screenshot_paths)

    return pdf_path
