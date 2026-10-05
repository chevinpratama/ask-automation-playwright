from fpdf import FPDF
import textwrap


def write_verifikasi_database_flexible(
    pdf: FPDF,
    query: str,
    db_result,
    bottom_margin=25
):
    pdf.set_auto_page_break(True, bottom_margin)

    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_x(pdf.l_margin)

    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    cell_height = 6

    # ==========================================================
    # QUERY
    # ==========================================================

    pdf.set_font("Courier", "I", 9)

    query_str = str(query).strip() if query else "(kosong)"

    pdf.cell(0, cell_height, "Query:", ln=True)

    pdf.multi_cell(
        usable_width,
        cell_height,
        query_str
    )

    pdf.ln(2)

    # ==========================================================
    # DATA CHECK
    # ==========================================================

    if not db_result:
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 8, "Tidak ada hasil dari query.", ln=True)
        return

    rows = [db_result] if isinstance(db_result, dict) else db_result
    row_count = len(rows)
    fields = list(rows[0].keys())
    column_count = len(fields)

    # ==========================================================
    # SINGLE ROW -> VERTICAL
    # ==========================================================

    if row_count == 1 and column_count > 6:

        SAFE_MARGIN = 12  # sisakan ruang di atas footer

        row = rows[0]

        label_width = 60
        value_width = usable_width - label_width

        for field, value in row.items():

            val_str = "-" if value is None else str(value)

            if field.lower() in [
                "json_request",
                "json_response",
                "response_desc"
            ]:
                if len(val_str) > 20:
                    val_str = val_str[:20] + "..."

            max_chars = max(
                20,
                int(value_width / pdf.get_string_width("M"))
            )

            wrapped_lines = (
                textwrap.wrap(
                    val_str,
                    width=max_chars
                ) or ["-"]
            )

            row_height = len(wrapped_lines) * cell_height

            # ===== PAGE BREAK =====
            if pdf.get_y() + row_height > pdf.h - bottom_margin - SAFE_MARGIN:
                pdf.add_page()
                pdf.set_x(pdf.l_margin)

            x_start = pdf.get_x()
            y_start = pdf.get_y()

            # ===== LABEL =====
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(230, 230, 230)

            pdf.cell(
                label_width,
                row_height,
                str(field),
                border=1,
                fill=True
            )

            # ===== VALUE =====
            pdf.set_xy(
                x_start + label_width,
                y_start
            )

            pdf.set_font("Arial", "", 9)

            pdf.multi_cell(
                value_width,
                cell_height,
                "\n".join(wrapped_lines),
                border=1
            )

            pdf.set_xy(
                x_start,
                y_start + row_height
            )
    # ==========================================================
    # MULTI ROW -> HORIZONTAL
    # ==========================================================

    else:

        SAFE_MARGIN = 12  # sisakan ruang di atas footer

        fields = list(rows[0].keys())

        max_cols_per_table = 6

        table_chunks = [
            fields[i:i + max_cols_per_table]
            for i in range(0, len(fields), max_cols_per_table)
        ]

        for field_group in table_chunks:

            # ================= WIDTH =================

            header_lengths = [
                max(len(str(f)), 10)
                for f in field_group
            ]

            total_length = sum(header_lengths)

            col_widths = [
                usable_width * (l / total_length)
                for l in header_lengths
            ]

            # ================= HEADER =================

            pdf.set_font("Arial", "B", 8)
            pdf.set_fill_color(230, 230, 230)

            for i, field in enumerate(field_group):
                pdf.cell(
                    col_widths[i],
                    cell_height,
                    str(field)[:30],
                    border=1,
                    fill=True,
                    align="C"
                )

            pdf.ln(cell_height)

            # ================= DATA =================

            pdf.set_font("Arial", "", 8)

            for row in rows:

                row_values = []

                for f in field_group:

                    value = "-" if row.get(f) is None else str(row.get(f))

                    if f.lower() in [
                        "json_request",
                        "json_response",
                        "response_desc"
                    ]:
                        if len(value) > 20:
                            value = value[:20] + "..."

                    row_values.append(value)

                wrapped_lines = []

                for width, value in zip(col_widths, row_values):

                    max_chars = max(
                        5,
                        int(width / pdf.get_string_width("M"))
                    )

                    wrapped_lines.append(
                        textwrap.wrap(value, width=max_chars) or ["-"]
                    )

                num_lines = max(len(w) for w in wrapped_lines)

                row_height = num_lines * cell_height

                # ================= PAGE BREAK =================

                if pdf.get_y() + row_height > pdf.h - bottom_margin - SAFE_MARGIN:

                    pdf.add_page()
                    pdf.set_x(pdf.l_margin)

                    # redraw header
                    pdf.set_font("Arial", "B", 8)
                    pdf.set_fill_color(230, 230, 230)

                    for i, field in enumerate(field_group):
                        pdf.cell(
                            col_widths[i],
                            cell_height,
                            str(field)[:30],
                            border=1,
                            fill=True,
                            align="C"
                        )

                    pdf.ln(cell_height)

                    pdf.set_font("Arial", "", 8)

                x_start = pdf.get_x()
                y_start = pdf.get_y()

                for width, lines in zip(col_widths, wrapped_lines):

                    text = "\n".join(lines)

                    x = pdf.get_x()
                    y = pdf.get_y()

                    pdf.multi_cell(
                        width,
                        cell_height,
                        text,
                        border=0
                    )

                    pdf.set_xy(
                        x + width,
                        y
                    )

                    pdf.rect(
                        x,
                        y,
                        width,
                        row_height
                    )

                pdf.set_xy(
                    x_start,
                    y_start + row_height
                )

            pdf.ln(3)
