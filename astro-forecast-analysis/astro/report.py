"""
Generates the bilingual (EN/EL) PDF forecast report using reportlab.
DejaVu Sans is registered explicitly so Greek glyphs render correctly
regardless of what fonts happen to be installed on the host (Railway's
build image is not guaranteed to ship Greek-capable fonts).
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .i18n import get_translations

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")
_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVuSans", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
    _FONTS_REGISTERED = True


def _styles():
    _register_fonts()
    ss = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("title", parent=ss["Title"], fontName="DejaVuSans-Bold",
                                 fontSize=20, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", parent=ss["Normal"], fontName="DejaVuSans",
                                    fontSize=10, textColor=colors.HexColor("#555555"),
                                    spaceAfter=14),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="DejaVuSans-Bold",
                              fontSize=13, spaceBefore=14, spaceAfter=6,
                              textColor=colors.HexColor("#8a6a1a")),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontName="DejaVuSans", fontSize=9,
                                leading=13),
        "disclaimer": ParagraphStyle("disclaimer", parent=ss["Normal"], fontName="DejaVuSans",
                                      fontSize=8, textColor=colors.HexColor("#666666"),
                                      leading=11, spaceBefore=10),
    }
    return styles


def _table_style(header_bg="#1b2436"):
    return TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f3ee")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ])


def build_pdf_report(output_path, lang, birth_params, chart, dasha_info, monthly_scores,
                      house_events, start_month, end_month):
    t = get_translations(lang)
    st = _styles()
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
    )
    story = []

    story.append(Paragraph(t["report_title"], st["title"]))
    story.append(Paragraph(
        f'{t["report_subtitle_prefix"]}: {start_month} – {end_month} &nbsp;|&nbsp; '
        f'{t["ascendant"]}: {t["signs"].get(chart["ascendant"]["sign"], chart["ascendant"]["sign"])} '
        f'{chart["ascendant"]["sign_deg"]:.2f}°',
        st["subtitle"],
    ))

    # Birth particulars
    story.append(Paragraph(t["birth_particulars"], st["h2"]))
    bp_rows = [
        [t["date"], f'{birth_params["year"]:04d}-{birth_params["month"]:02d}-{birth_params["day"]:02d}'],
        [t["time_local"], f'{birth_params["hour"]:02d}:{birth_params["minute"]:02d}'],
        [t["utc_offset"], str(birth_params["utc_offset"])],
        [t["latitude"], str(birth_params["latitude"])],
        [t["longitude"], str(birth_params["longitude"])],
    ]
    bp_table = Table(bp_rows, colWidths=[45 * mm, 60 * mm])
    bp_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTNAME", (0, 0), (0, -1), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(bp_table)

    # Planet positions
    story.append(Paragraph(t["planet_positions"], st["h2"]))
    header = [t["planet_col"], t["sign"], "°", t["house"], t["nakshatra"]]
    rows = [header]
    for name, p in chart["planets"].items():
        pname = t["planets"].get(name, name)
        if p["retrograde"]:
            pname += f' ({t["retrograde_short"]})'
        rows.append([
            pname,
            t["signs"].get(p["sign"], p["sign"]),
            f'{p["sign_deg"]:.2f}',
            str(p["house"]),
            p["nakshatra"],
        ])
    ptable = Table(rows, colWidths=[35 * mm, 28 * mm, 15 * mm, 15 * mm, 35 * mm], repeatRows=1)
    ptable.setStyle(_table_style())
    story.append(ptable)

    # Current dasha
    story.append(Paragraph(t["current_dasha"], st["h2"]))
    dasha_rows = [
        [t["mahadasha"], t["planets"].get(dasha_info["current_mahadasha"], dasha_info["current_mahadasha"] or "-")],
        [t["antardasha"], t["planets"].get(dasha_info["current_antardasha"], dasha_info["current_antardasha"] or "-")],
    ]
    dtable = Table(dasha_rows, colWidths=[45 * mm, 60 * mm])
    dtable.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTNAME", (0, 0), (0, -1), "DejaVuSans-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(dtable)

    story.append(PageBreak())

    # Monthly activation scores -- chunk months into groups of 6 columns per table
    story.append(Paragraph(t["monthly_scores"], st["h2"]))
    months = list(monthly_scores.keys())
    area_keys = list(next(iter(monthly_scores.values())).keys())
    chunk_size = 6
    cell_style = ParagraphStyle("cell", fontName="DejaVuSans", fontSize=7.5, leading=9)
    for i in range(0, len(months), chunk_size):
        chunk = months[i:i + chunk_size]
        header = [t["area"]] + chunk
        rows = [header]
        for area in area_keys:
            label = t["areas"].get(area, area)
            row = [Paragraph(label, cell_style)] + [str(monthly_scores[m][area]) for m in chunk]
            rows.append(row)
        col_widths = [42 * mm] + [(174 - 42) / len(chunk) * mm for _ in chunk]
        table = Table(rows, colWidths=col_widths, repeatRows=1)
        table.setStyle(_table_style())
        story.append(table)
        story.append(Spacer(1, 8))

    # House-change calendar
    if house_events:
        story.append(Paragraph(t["house_change_calendar"], st["h2"]))
        header = [t["date_col"], t["planet_col"], t["change_col"]]
        rows = [header]
        for ev in house_events:
            planet_label = t["planets"].get(ev["planet"], ev["planet"])
            from_sign = t["signs"].get(ev["from_sign"], ev["from_sign"])
            to_sign = t["signs"].get(ev["to_sign"], ev["to_sign"])
            retro = f' ({t["retrograde_short"]})' if ev["retrograde"] else ""
            rows.append([ev["date"], planet_label, f"{from_sign} → {to_sign}{retro}"])
        htable = Table(rows, colWidths=[28 * mm, 30 * mm, 90 * mm], repeatRows=1)
        htable.setStyle(_table_style())
        story.append(htable)

    story.append(Paragraph(t["disclaimer"], st["disclaimer"]))

    doc.build(story)
    return output_path
