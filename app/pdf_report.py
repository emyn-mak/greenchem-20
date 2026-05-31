from datetime import datetime, timezone
from io import BytesIO
from textwrap import shorten

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas import AnalyzeResponse


def build_analysis_pdf(response: AnalyzeResponse, source_text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="GreenChem Navigator Analysis Report",
        author="GreenChem Navigator",
    )

    styles = report_styles()
    data = response.model_dump()
    story = [
        Paragraph("GreenChem Navigator", styles["Title"]),
        Paragraph("Solvent Replacement Analysis Report", styles["Subtitle"]),
        Paragraph(
            f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            styles["Meta"],
        ),
        Spacer(1, 7 * mm),
        summary_table(data, styles),
        section("Important Validation Notice", styles),
        Paragraph(
            "This report is decision-support material only. Recommendations are based on local solvent-guide data, "
            "compatibility rules, and prototype model signals when available. Wet lab validation and human expert "
            "review are required before changing any chemical process. This is an AI-assisted recommendation; "
            "the final decision must be made by the user or a qualified human expert.",
            styles["Body"],
        ),
        section("Submitted Formula Notes", styles),
        code_block(source_text, styles),
    ]

    story.extend(detected_input_section(data, styles))
    story.extend(current_assessment_section(data, styles))
    story.extend(alternatives_section(data, styles))

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
    return buffer.getvalue()


def report_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#101b17"),
            alignment=TA_LEFT,
            spaceAfter=2 * mm,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#168658"),
            alignment=TA_LEFT,
            spaceAfter=1 * mm,
        ),
        "Section": ParagraphStyle(
            "Section",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#101b17"),
            spaceBefore=8 * mm,
            spaceAfter=3 * mm,
        ),
        "CardTitle": ParagraphStyle(
            "CardTitle",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#17211d"),
            spaceAfter=1.5 * mm,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13,
            textColor=colors.HexColor("#344540"),
            spaceAfter=2 * mm,
        ),
        "Meta": ParagraphStyle(
            "Meta",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#60716b"),
        ),
        "Code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.3,
            leading=11,
            backColor=colors.HexColor("#eef3f1"),
            borderColor=colors.HexColor("#d7e1dc"),
            borderWidth=0.5,
            borderPadding=6,
            textColor=colors.HexColor("#17211d"),
        ),
        "Cell": ParagraphStyle(
            "Cell",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#344540"),
        ),
        "CellBold": ParagraphStyle(
            "CellBold",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#17211d"),
        ),
    }


def summary_table(data: dict, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        ["Status", data.get("status") or "Unknown"],
        ["Validation status", data.get("validation_status") or "Unknown"],
        ["Alternatives found", str(data.get("alternatives_found", 0))],
        ["Human validation", "Required" if data.get("human_validation_required") else "Not flagged"],
        ["Message", data.get("message") or ""],
    ]
    return key_value_table(rows, styles, col_widths=[42 * mm, 124 * mm])


def detected_input_section(data: dict, styles: dict[str, ParagraphStyle]) -> list:
    detected = data.get("detected_input") or {}
    compounds = detected.get("compounds") or []
    environment = detected.get("environment") or {}

    story = [section("Detected Input", styles)]
    if compounds:
        rows = [["Amount", "Compound", "Formula", "Role"]]
        for compound in compounds:
            amount = " ".join(part for part in [compound.get("quantity"), compound.get("unit")] if part)
            rows.append(
                [
                    amount or "-",
                    compound.get("name") or "-",
                    compound.get("formula") or "-",
                    compound.get("role") or "compound",
                ]
            )
        story.append(data_table(rows, styles, [28 * mm, 52 * mm, 36 * mm, 40 * mm]))
    else:
        story.append(Paragraph("No compounds were parsed from the submitted notes.", styles["Body"]))

    fields = [(format_key(key), value) for key, value in environment.items() if value]
    if fields:
        story.append(Spacer(1, 3 * mm))
        story.append(key_value_table(fields, styles, col_widths=[42 * mm, 124 * mm]))
    return story


def current_assessment_section(data: dict, styles: dict[str, ParagraphStyle]) -> list:
    current = data.get("current_formula") or {}
    solvent = current.get("solvent") or {}
    story = [section("Current Formula Assessment", styles)]
    rows = [
        ["Current solvent", solvent.get("name") or "Unknown"],
        ["Formula", solvent.get("formula") or "Unknown"],
        ["CHEM21 color", solvent.get("chem21_color") or "Unknown"],
        ["GHS codes", join_items(solvent.get("ghs_codes"))],
        ["Boiling point", format_temperature(solvent.get("boiling_point_c"))],
        ["Catalyst", current.get("catalyst_formula") or "Unknown"],
        ["Catalyst role", current.get("catalyst_role") or "Unknown"],
    ]
    story.append(key_value_table(rows, styles, col_widths=[42 * mm, 124 * mm]))
    story.extend(list_section("Hazard summary", current.get("hazard_summary"), styles))
    story.extend(list_section("Compatibility warnings", current.get("compatibility_warnings"), styles))
    return story


def alternatives_section(data: dict, styles: dict[str, ParagraphStyle]) -> list:
    alternatives = data.get("alternatives") or []
    story = [section("Recommended Alternatives And Solution Details", styles)]

    if not alternatives:
        story.append(
            Paragraph(
                "No compatible alternatives were returned by the local knowledge-base and compatibility filters.",
                styles["Body"],
            )
        )
        return story

    for alternative in alternatives:
        solvent = alternative.get("replacement_solvent") or {}
        title = f"#{alternative.get('rank', '-')} {solvent.get('name', 'Unknown solvent')}"
        story.extend(
            [
                Paragraph(title, styles["CardTitle"]),
                key_value_table(
                    [
                        ["Status", alternative.get("status") or "Unknown"],
                        ["Validation status", alternative.get("validation_status") or "Unknown"],
                        ["Formula", solvent.get("formula") or "Unknown"],
                        ["CHEM21 color", solvent.get("chem21_color") or "Unknown"],
                        ["GHS codes", join_items(solvent.get("ghs_codes"))],
                        ["Boiling point", format_temperature(solvent.get("boiling_point_c"))],
                    ],
                    styles,
                    col_widths=[38 * mm, 128 * mm],
                ),
                Paragraph("Proposed formula adjustment", styles["CardTitle"]),
                code_block("\n".join(alternative.get("formula") or ["No formula lines returned."]), styles),
                Spacer(1, 3 * mm),
            ]
        )
        story.extend(list_section("Compatibility notes", alternative.get("compatibility_notes"), styles))
        story.extend(list_section("Qualitative benefits", alternative.get("qualitative_benefits"), styles))
        story.extend(evidence_section(alternative.get("evidence"), styles))
        story.append(Spacer(1, 3 * mm))
    return story


def section(title: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(title, styles["Section"])


def code_block(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    safe_text = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe_text.replace("\n", "<br/>"), styles["Code"])


def list_section(title: str, items: list[str] | None, styles: dict[str, ParagraphStyle]):
    values = [item for item in (items or []) if item]
    if not values:
        return [Paragraph(f"<b>{title}:</b> None returned.", styles["Body"])]

    return [
        Paragraph(title, styles["CardTitle"]),
        ListFlowable(
            [ListItem(Paragraph(item, styles["Body"])) for item in values],
            bulletType="bullet",
            leftIndent=5 * mm,
        ),
    ]


def evidence_section(items: list[dict] | None, styles: dict[str, ParagraphStyle]):
    values = []
    for item in items or []:
        source = item.get("source") or "Source"
        statement = item.get("statement") or ""
        values.append(f"<b>{source}:</b> {statement}")
    return list_section("Evidence", values, styles)


def key_value_table(
    rows: list[tuple[str, object] | list[object]],
    styles: dict[str, ParagraphStyle],
    col_widths: list[float],
) -> Table:
    table_data = [
        [Paragraph(str(key), styles["CellBold"]), Paragraph(str(value or "-"), styles["Cell"])]
        for key, value in rows
    ]
    table = Table(table_data, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(base_table_style())
    return table


def data_table(rows: list[list[object]], styles: dict[str, ParagraphStyle], col_widths: list[float]) -> Table:
    table_data = []
    for row_index, row in enumerate(rows):
        style = styles["CellBold"] if row_index == 0 else styles["Cell"]
        table_data.append([Paragraph(str(value or "-"), style) for value in row])
    table = Table(table_data, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(base_table_style(header=True))
    return table


def base_table_style(header: bool = False) -> TableStyle:
    commands = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d7e1dc")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d7e1dc")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfcfb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5f5ee")))
    return TableStyle(commands)


def draw_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#60716b"))
    canvas.drawString(16 * mm, 9 * mm, "GreenChem Navigator - wet lab validation required")
    canvas.drawRightString(194 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def join_items(items: list[str] | None) -> str:
    return ", ".join(items or ["None in local knowledge base"])


def format_temperature(value: object) -> str:
    if value is None:
        return "Unknown"
    return f"{value} C"


def format_key(value: str) -> str:
    return shorten(value.replace("_", " ").title(), width=34, placeholder="...")
