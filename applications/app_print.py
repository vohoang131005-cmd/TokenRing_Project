
# applications/app_print.py
import os
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Preformatted
)
from xml.sax.saxutils import escape
from utils.logger import log


def dang_ky_font():
    """Dang ky font ho tro tieng Viet."""

    if "ArialVN" in pdfmetrics.getRegisteredFontNames():
        return "ArialVN"

    cac_font = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for duong_dan in cac_font:
        if os.path.exists(duong_dan):
            pdfmetrics.registerFont(TTFont("ArialVN", duong_dan))
            return "ArialVN"

    return "Helvetica"


def tao_pdf(node_id, tieu_de, noi_dung, ten_file):
    """Tao file PDF cho Node."""

    os.makedirs("output", exist_ok=True)

    duong_dan = os.path.join("output", ten_file)

    font = dang_ky_font()

    tai_lieu = SimpleDocTemplate(
        duong_dan,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        "TieuDe",
        parent=styles["Title"],
        fontName=font,
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    style_normal = ParagraphStyle(
        "NoiDung",
        parent=styles["Normal"],
        fontName=font,
        fontSize=11,
        leading=17
    )

    story = []

    story.append(Paragraph(escape(tieu_de), style_title))
    story.append(
        Paragraph(f"Node ID: {node_id}", style_normal)
    )
    story.append(Spacer(1, 15))

    if noi_dung.strip():
        story.append(
            Preformatted(
                noi_dung,
                style_normal,
                maxLineLength=100
            )
        )
    else:
        story.append(
            Paragraph("Chua co du lieu de in.", style_normal)
        )

    tai_lieu.build(story)

    return duong_dan


def print_document(node_id, document_name="DATA"):
    """
    PRINT: In du lieu rieng cua Node.
    PRINT VOTE: In lich su vote rieng cua Node.
    """

    document_name = document_name.strip().upper()

    os.makedirs("output", exist_ok=True)

    log(node_id, "DANG CHUAN BI TAI LIEU PDF...", "WARNING")

    time.sleep(1)

    # In lich su vote rieng
    if document_name == "VOTE":

        file_path = os.path.join(
            "shared_data",
            "vote_history",
            f"node_{node_id}.json"
        )

        ten_pdf = f"VOTE_NODE_{node_id}.pdf"

        tieu_de = f"LICH SU BO PHIEU - NODE {node_id}"

        noi_dung = ""

        if os.path.exists(file_path):
            try:
                import json

                with open(file_path, "r", encoding="utf-8") as f:
                    lich_su = json.load(f)

                for i, lan_vote in enumerate(lich_su, start=1):
                    noi_dung += (
                        f"Lan {i}: "
                        f"Vote {lan_vote['candidate']} "
                        f"- Thoi gian: {lan_vote['time']}\n"
                    )

            except Exception as e:
                log(node_id, f"Loi doc lich su vote: {e}", "ERROR")
                return None

    # In du lieu rieng cua Node
    else:

        file_path = os.path.join(
            "shared_data",
            "node_data",
            f"node_{node_id}.txt"
        )

        ten_pdf = f"NODE_{node_id}.pdf"

        tieu_de = f"DU LIEU RIENG CUA NODE {node_id}"

        noi_dung = ""

        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    noi_dung = f.read()

            except OSError as e:
                log(node_id, f"Loi doc file du lieu: {e}", "ERROR")
                return None

    try:
        duong_dan = tao_pdf(
            node_id,
            tieu_de,
            noi_dung,
            ten_pdf
        )

        log(
            node_id,
            f"DA IN PDF THANH CONG: {duong_dan}",
            "SUCCESS"
        )

        return duong_dan

    except Exception as e:
        log(node_id, f"Loi tao PDF: {e}", "ERROR")
        return None
