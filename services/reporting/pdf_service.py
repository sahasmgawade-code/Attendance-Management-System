from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from io import BytesIO
import os


class PDFReportService:
    """
    Generates a PDF attendance report with:
    1. College logo and header
    2. Date of generation
    3. Table 1 — Defaulters (below 75%)
    4. Table 2 — Remaining students
    Both tables sorted by attendance % descending.
    """

    def generate(self, students):
        """
        Generates PDF and returns it as bytes.
        students: list of dicts with keys:
            urn, name, present, working, attendance, defaulter
        """

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        styles = getSampleStyleSheet()

        elements = []

        # -----------------------------
        # Logo + Header
        # -----------------------------

        logo_path = os.path.join("static", "images", "ADYPU.png")

        if os.path.exists(logo_path):

            logo = Image(logo_path, width=2 * cm, height=2 * cm)

            header_data = [[
                logo,
                Paragraph(
                    "<b>Ajeenkya DY Patil University</b><br/>Attendance Report",
                    ParagraphStyle(
                        "header",
                        fontSize=14,
                        alignment=TA_CENTER,
                        leading=20
                    )
                )
            ]]

            header_table = Table(
                header_data,
                colWidths=[3 * cm, 14 * cm]
            )

            header_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ]))

            elements.append(header_table)

        else:

            elements.append(Paragraph(
                "<b>Ajeenkya DY Patil University</b>",
                ParagraphStyle(
                    "header",
                    fontSize=16,
                    alignment=TA_CENTER
                )
            ))

        elements.append(Spacer(1, 0.3 * cm))

        # -----------------------------
        # Date of Generation
        # -----------------------------

        date_str = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        elements.append(Paragraph(
            f"Generated on: {date_str}",
            ParagraphStyle(
                "date",
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
        ))

        elements.append(Spacer(1, 0.5 * cm))

        # -----------------------------
        # Split and Sort Students
        # -----------------------------

        defaulters = sorted(
            [s for s in students if s["defaulter"]],
            key=lambda x: x["attendance"],
            reverse=True
        )

        others = sorted(
            [s for s in students if not s["defaulter"]],
            key=lambda x: x["attendance"],
            reverse=True
        )

        # -----------------------------
        # Table 1 — Defaulters
        # -----------------------------

        elements.append(Paragraph(
            "⚠ Defaulters — Attendance Below 75%",
            ParagraphStyle(
                "section",
                fontSize=12,
                textColor=colors.red,
                spaceAfter=6
            )
        ))

        elements.append(Spacer(1, 0.2 * cm))

        if defaulters:

            elements.append(
                self._build_table(defaulters, defaulter=True)
            )

        else:

            elements.append(Paragraph(
                "No defaulters found.",
                styles["Normal"]
            ))

        elements.append(Spacer(1, 0.8 * cm))

        # -----------------------------
        # Table 2 — Remaining Students
        # -----------------------------

        elements.append(Paragraph(
            "✓ Students — Attendance 75% and Above",
            ParagraphStyle(
                "section",
                fontSize=12,
                textColor=colors.green,
                spaceAfter=6
            )
        ))

        elements.append(Spacer(1, 0.2 * cm))

        if others:

            elements.append(
                self._build_table(others, defaulter=False)
            )

        else:

            elements.append(Paragraph(
                "No students found.",
                styles["Normal"]
            ))

        doc.build(elements)

        buffer.seek(0)

        return buffer

    # =====================================================
    # PRIVATE
    # =====================================================

    def _build_table(self, students, defaulter=False):

        # Header row
        data = [[
            "URN",
            "Student Name",
            "Present",
            "Working Days",
            "Attendance %"
        ]]

        # Data rows
        for s in students:
            data.append([
                str(s["urn"]),
                s["name"],
                str(s["present"]),
                str(s["working"]),
                f"{s['attendance']}%"
            ])

        col_widths = [3 * cm, 6 * cm, 2.5 * cm, 3 * cm, 3 * cm]

        table = Table(data, colWidths=col_widths)

        # Header color
        header_bg = colors.HexColor("#dc3545") if defaulter else colors.HexColor("#198754")

        table.setStyle(TableStyle([

            # Header
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),

            # Data rows
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (2, 1), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),

            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        ]))

        return table