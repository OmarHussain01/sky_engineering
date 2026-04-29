"""
HTTP views for the reports app.

Author: Danyal Khan
Module: 5COSC021W - CW2 Individual Element

The views are deliberately thin - they pick the right generator class,
call render(), and return a properly-typed HttpResponse. All of the
PDF and Excel logic lives in the generator modules.

Authentication: every view requires the user to be logged in. The
brief specifies that users must register and log in to access the
system, so it would be a security failure to expose the reports
without auth.
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from . import excel_generator, pdf_generator, queries


CONTENT_TYPE_PDF = 'application/pdf'
CONTENT_TYPE_XLSX = (
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)


# ---------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------

@login_required
def index(request):
    """Landing page listing every available report."""
    totals = queries.overall_totals()
    available_reports = [
        {
            'key': 'teams_summary',
            'title': 'All Teams',
            'description': (
                'Every team in the registry with manager, member count '
                'and contact details.'
            ),
        },
        {
            'key': 'teams_without_managers',
            'title': 'Teams Without Managers',
            'description': (
                'Operational gap report - teams that need a manager '
                'assigned by department leadership.'
            ),
        },
        {
            'key': 'department_summary',
            'title': 'Department Summary',
            'description': (
                'Department-level totals, suitable for senior leadership '
                'briefs and quarterly reviews.'
            ),
        },
    ]

    context = {
        'totals': totals,
        'reports': available_reports,
    }
    return render(request, 'reports/index.html', context)


# ---------------------------------------------------------------------
# Generator dispatch
# ---------------------------------------------------------------------
#
# A small lookup keeps the URL configuration short and means a new
# report only needs an entry here plus a generator class - no new view
# function required.

PDF_GENERATORS = {
    'teams_summary': pdf_generator.TeamsSummaryReport,
    'teams_without_managers': pdf_generator.TeamsWithoutManagersReport,
    'department_summary': pdf_generator.DepartmentSummaryReport,
}

EXCEL_GENERATORS = {
    'teams_summary': excel_generator.TeamsSummaryReport,
    'teams_without_managers': excel_generator.TeamsWithoutManagersReport,
    'department_summary': excel_generator.DepartmentSummaryReport,
}


@login_required
def download_pdf(request, report_key: str):
    """Render the requested PDF report and return it as a download."""
    generator_cls = PDF_GENERATORS.get(report_key)
    if generator_cls is None:
        return HttpResponse('Unknown report.', status=404)

    generator = generator_cls()
    pdf_bytes = generator.render()

    response = HttpResponse(pdf_bytes, content_type=CONTENT_TYPE_PDF)
    response['Content-Disposition'] = (
        f'attachment; filename="{generator.filename}"'
    )
    return response


@login_required
def download_excel(request, report_key: str):
    """Render the requested Excel report and return it as a download."""
    generator_cls = EXCEL_GENERATORS.get(report_key)
    if generator_cls is None:
        return HttpResponse('Unknown report.', status=404)

    generator = generator_cls()
    xlsx_bytes = generator.render()

    response = HttpResponse(xlsx_bytes, content_type=CONTENT_TYPE_XLSX)
    response['Content-Disposition'] = (
        f'attachment; filename="{generator.filename}"'
    )
    return response
