"""
PDF report generation using ReportLab.

Author: Danyal
Module: 5COSC021W - CW2 Individual Element

The BasePDFReport class handles all the common chrome - branded header,
footer with page numbers, generation timestamp - so each individual
report only needs to provide its title and the body content.

This is deliberately a class-based design rather than a single function:
when a new report type is added, the developer only writes a build_body
method and the styling stays consistent across the whole portal.
"""

import io
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph,
    Spacer, Table, TableStyle,
)

from . import branding
from . import queries


# ---------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------

class BasePDFReport:
    """Common scaffolding for every Sky Engineering Portal PDF report.

    Subclasses override `title`, `subtitle`, and `build_body()`.
    """

    title = 'Sky Engineering Report'
    subtitle = ''
    filename = 'sky_report.pdf'

    def __init__(self):
        self._styles = self._build_paragraph_styles()

    # -- Public API -----------------------------------------------------

    def render(self) -> bytes:
        """Render the report and return the PDF as bytes."""
        buffer = io.BytesIO()

        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=branding.PAGE_MARGIN_MM * mm,
            rightMargin=branding.PAGE_MARGIN_MM * mm,
            topMargin=(branding.PAGE_MARGIN_MM + branding.HEADER_HEIGHT_MM) * mm,
            bottomMargin=(branding.PAGE_MARGIN_MM + branding.FOOTER_HEIGHT_MM) * mm,
            title=self.title,
            author='Sky Engineering Portal',
        )

        # Single frame covering the printable area. Header and footer
        # are drawn separately by _draw_chrome() so they don't compete
        # with the flowable content for space.
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id='content',
        )
        doc.addPageTemplates([
            PageTemplate(id='main', frames=[frame], onPage=self._draw_chrome)
        ])

        story = self.build_body()
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def build_body(self) -> list:
        """Override in subclasses to produce the flowable content."""
        raise NotImplementedError

    # -- Helpers exposed to subclasses ---------------------------------

    def heading(self, text: str) -> Paragraph:
        return Paragraph(text, self._styles['heading'])

    def body(self, text: str) -> Paragraph:
        return Paragraph(text, self._styles['body'])

    def warning(self, text: str) -> Paragraph:
        return Paragraph(text, self._styles['warning'])

    def make_table(self, header: Iterable[str], rows: list[list],
                   col_weights: list[float] | None = None) -> Table:
        """Return a styled table with Sky branding applied.

        col_weights, if given, are relative widths (e.g. [2, 1, 1, 3])
        and the printable area is split in proportion. If omitted, the
        table is split evenly.

        Cells are wrapped in Paragraph objects so long text wraps
        cleanly inside the column rather than overflowing.
        """
        header_list = list(header)
        col_count = len(header_list)

        printable_width = A4[0] - 2 * branding.PAGE_MARGIN_MM * mm

        if col_weights is None:
            col_widths = [printable_width / col_count] * col_count
        else:
            if len(col_weights) != col_count:
                raise ValueError(
                    'col_weights must have one entry per column'
                )
            total = sum(col_weights)
            col_widths = [printable_width * w / total for w in col_weights]

        cell_style = ParagraphStyle(
            'TableCell',
            fontName=branding.FONT_REGULAR,
            fontSize=8,
            textColor=colors.HexColor(branding.TEXT_DARK),
            leading=11,
        )

        # Header cells stay as plain strings - the Table styling handles
        # their colour and font. Body cells become Paragraphs so text
        # wraps inside the column width.
        data: list = [header_list]
        for row in rows:
            data.append([
                Paragraph(str(value), cell_style) for value in row
            ])

        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(branding.SKY_NAVY)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(branding.WHITE)),
            ('FONTNAME', (0, 0), (-1, 0), branding.FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Body rows - padding only, text styling handled by the
            # Paragraph cell style above.
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),

            # Alternating row colours (zebra striping)
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.HexColor(branding.WHITE),
              colors.HexColor(branding.SKY_LIGHT_BLUE)]),

            # Subtle grid
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(branding.SKY_BLUE)),
            ('GRID', (0, 1), (-1, -1), 0.25,
             colors.HexColor(branding.BORDER_GREY)),
        ]))
        return table

    # -- Internal helpers -----------------------------------------------

    def _build_paragraph_styles(self) -> dict:
        base = getSampleStyleSheet()['Normal']
        return {
            'heading': ParagraphStyle(
                'Heading',
                parent=base,
                fontName=branding.FONT_BOLD,
                fontSize=14,
                textColor=colors.HexColor(branding.SKY_NAVY),
                spaceAfter=6,
            ),
            'body': ParagraphStyle(
                'Body',
                parent=base,
                fontName=branding.FONT_REGULAR,
                fontSize=10,
                textColor=colors.HexColor(branding.TEXT_DARK),
                leading=14,
                spaceAfter=6,
            ),
            'warning': ParagraphStyle(
                'Warning',
                parent=base,
                fontName=branding.FONT_BOLD,
                fontSize=10,
                textColor=colors.HexColor(branding.SKY_RED),
                spaceAfter=6,
            ),
        }

    def _draw_chrome(self, canvas, doc):
        """Draw the header band and footer for every page."""
        canvas.saveState()

        page_width, page_height = A4

        # Header band - a solid navy block across the top
        header_height = branding.HEADER_HEIGHT_MM * mm
        canvas.setFillColor(colors.HexColor(branding.SKY_NAVY))
        canvas.rect(
            0,
            page_height - header_height,
            page_width,
            header_height,
            stroke=0,
            fill=1,
        )

        # Logo / wordmark - the word "sky" in lowercase. Sky's actual
        # logo is trademarked so we use a typographic stand-in here;
        # in production the group would replace this with a licensed
        # SVG/PNG asset placed under static/.
        canvas.setFillColor(colors.HexColor(branding.WHITE))
        canvas.setFont(branding.FONT_BOLD, 22)
        canvas.drawString(
            branding.PAGE_MARGIN_MM * mm,
            page_height - header_height + 7 * mm,
            'sky'
        )
        canvas.setFont(branding.FONT_REGULAR, 9)
        canvas.drawString(
            branding.PAGE_MARGIN_MM * mm + 22 * mm,
            page_height - header_height + 9 * mm,
            'engineering portal'
        )

        # Report title on the right side of the header
        canvas.setFont(branding.FONT_BOLD, 11)
        canvas.drawRightString(
            page_width - branding.PAGE_MARGIN_MM * mm,
            page_height - header_height + 11 * mm,
            self.title,
        )
        if self.subtitle:
            canvas.setFont(branding.FONT_REGULAR, 8)
            canvas.drawRightString(
                page_width - branding.PAGE_MARGIN_MM * mm,
                page_height - header_height + 6 * mm,
                self.subtitle,
            )

        # Footer - timestamp on the left, page number on the right
        canvas.setFillColor(colors.HexColor(branding.TEXT_MUTED))
        canvas.setFont(branding.FONT_REGULAR, 8)
        totals = queries.overall_totals()
        canvas.drawString(
            branding.PAGE_MARGIN_MM * mm,
            12 * mm,
            f'Generated {totals["generated_at"]}',
        )
        canvas.drawRightString(
            page_width - branding.PAGE_MARGIN_MM * mm,
            12 * mm,
            f'Page {doc.page}',
        )

        # Hairline above the footer
        canvas.setStrokeColor(colors.HexColor(branding.BORDER_GREY))
        canvas.setLineWidth(0.4)
        canvas.line(
            branding.PAGE_MARGIN_MM * mm,
            16 * mm,
            page_width - branding.PAGE_MARGIN_MM * mm,
            16 * mm,
        )

        canvas.restoreState()


# ---------------------------------------------------------------------
# Concrete reports
# ---------------------------------------------------------------------

class TeamsSummaryReport(BasePDFReport):
    """Full list of every team with key metadata."""

    title = 'All Teams'
    subtitle = 'Engineering team registry'
    filename = 'sky_teams_summary.pdf'

    def build_body(self) -> list:
        story: list = []
        totals = queries.overall_totals()

        story.append(self.heading('Summary'))
        story.append(self.body(
            f'This report lists every engineering team in the registry. '
            f'There are currently <b>{totals["total_teams"]}</b> teams '
            f'across <b>{totals["total_departments"]}</b> departments.'
        ))
        if totals['total_unmanaged']:
            story.append(self.warning(
                f'Warning: {totals["total_unmanaged"]} team(s) currently have '
                f'no manager assigned. See the dedicated report for details.'
            ))
        story.append(Spacer(1, 6 * mm))

        rows = queries.teams_summary()
        if not rows:
            story.append(self.body(
                'No teams are currently recorded in the registry.'
            ))
            return story

        table_rows = [
            [r['team'], r['department'], r['manager'],
             str(r['members']), r['contact']]
            for r in rows
        ]
        story.append(self.make_table(
            ['Team', 'Department', 'Manager', 'Members', 'Contact'],
            table_rows,
            col_weights=[2, 2.5, 2, 1, 2],
        ))
        return story


class TeamsWithoutManagersReport(BasePDFReport):
    """Highlight teams missing a manager - operational priority."""

    title = 'Teams Without Managers'
    subtitle = 'Operational gap report'
    filename = 'sky_teams_without_managers.pdf'

    def build_body(self) -> list:
        story: list = []
        rows = queries.teams_without_managers()

        story.append(self.heading('Why this report exists'))
        story.append(self.body(
            'A team without an assigned manager is an accountability gap. '
            'During an incident, on-call escalation paths assume a single '
            'point of contact. This report identifies teams that need '
            'attention from department leadership.'
        ))
        story.append(Spacer(1, 4 * mm))

        if not rows:
            story.append(self.heading('Result'))
            story.append(self.body(
                'Every team currently has a manager assigned. No action '
                'is required.'
            ))
            return story

        story.append(self.warning(
            f'{len(rows)} team(s) have no manager assigned.'
        ))
        story.append(Spacer(1, 2 * mm))

        table_rows = [
            [r['team'], r['department'], str(r['members']),
             r['contact'], r['created']]
            for r in rows
        ]
        story.append(self.make_table(
            ['Team', 'Department', 'Members', 'Contact', 'Created'],
            table_rows,
            col_weights=[2.5, 2.5, 1, 2, 1.5],
        ))
        return story


class DepartmentSummaryReport(BasePDFReport):
    """Department-level totals for senior leadership briefs."""

    title = 'Department Summary'
    subtitle = 'Department-level view'
    filename = 'sky_department_summary.pdf'

    def build_body(self) -> list:
        story: list = []
        rows = queries.department_summary()

        story.append(self.heading('Departments at a glance'))
        story.append(self.body(
            'For each department, this view shows the number of teams, '
            'how many of those teams currently have no manager, and the '
            'unique engineer headcount across the department.'
        ))
        story.append(Spacer(1, 4 * mm))

        if not rows:
            story.append(self.body('No departments are currently recorded.'))
            return story

        table_rows = [
            [r['department'], r['leader'], r['specialisation'],
             str(r['num_teams']), str(r['unmanaged_teams']),
             str(r['unique_engineers'])]
            for r in rows
        ]
        story.append(self.make_table(
            ['Department', 'Leader', 'Specialisation',
             'Teams', 'Unmanaged', 'Engineers'],
            table_rows,
            col_weights=[2.2, 1.8, 3, 1, 1.3, 1.3],
        ))
        return story
