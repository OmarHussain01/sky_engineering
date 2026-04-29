"""
Data queries used to build reports.

Author: Danyal Khan
Module: 5COSC021W - CW2 Individual Element

This module is the single point of contact between the reports app and
the rest of the project's data. Keeping all the ORM queries here means:

  1. If the schema evolves, only one place needs to change.
  2. Tests can mock or replace these functions easily.
  3. The PDF and Excel generators don't need to know anything about Django.

Each function returns a plain Python list of dicts so that the
generators (PDF/Excel) don't need to know anything about Django.
"""

from datetime import datetime

from django.db.models import Count, Q

from organization.models import Department
from teams.models import Team, TeamMember, ContactChannel


def _format_user(user):
    """Return a friendly display name for a User, or an unassigned marker."""
    if user is None:
        return '— Unassigned —'
    full = user.get_full_name() if hasattr(user, 'get_full_name') else ''
    return full or user.username


def _primary_contact(team):
    """Return the team's first contact channel as a printable string.

    Teams have many contact channels (Slack, Teams, email, etc.); for
    report rows we just want one short representative value.
    """
    channel = ContactChannel.objects.filter(team=team).first()
    if not channel:
        return 'N/A'
    return f'{channel.get_kind_display()}: {channel.value}'


def teams_summary():
    """Return a list of every team with summary information.

    Used by the 'All Teams' report. Each row contains the team name,
    department, manager, member count and contact channel.
    """
    teams = (
        Team.objects
        .select_related('department', 'manager')
        .annotate(num_members=Count('teammember', distinct=True))
        .order_by('department__name', 'name')
    )

    rows = []
    for team in teams:
        rows.append({
            'team': team.name,
            'department': team.department.name,
            'manager': _format_user(team.manager),
            'members': team.num_members,
            'contact': _primary_contact(team),
            'repository': team.coderepository_set.first().url
                          if team.coderepository_set.exists() else 'N/A',
        })
    return rows


def teams_without_managers():
    """Return teams that have no manager assigned.

    The brief specifically calls this report out by name. It is critical
    operational data - a team without a manager is a gap in accountability.
    """
    teams = (
        Team.objects
        .filter(manager__isnull=True)
        .select_related('department')
        .annotate(num_members=Count('teammember', distinct=True))
        .order_by('department__name', 'name')
    )

    rows = []
    for team in teams:
        rows.append({
            'team': team.name,
            'department': team.department.name,
            'members': team.num_members,
            'contact': _primary_contact(team),
            'created': team.created_at.strftime('%d %b %Y'),
        })
    return rows


def department_summary():
    """Return totals grouped by department.

    For each department, count the number of teams and the total
    headcount across those teams. Useful for senior leadership briefs.
    """
    departments = (
        Department.objects
        .select_related('leader')
        .annotate(
            num_teams=Count('team', distinct=True),
            num_unmanaged=Count(
                'team',
                filter=Q(team__manager__isnull=True),
                distinct=True,
            ),
        )
        .order_by('name')
    )

    rows = []
    for dept in departments:
        # Count distinct engineers across all teams in this department.
        # Done in Python to keep the ORM query simple and avoid double-
        # counting people who belong to multiple teams.
        member_user_ids = set(
            TeamMember.objects
            .filter(team__department=dept)
            .values_list('user_id', flat=True)
        )

        rows.append({
            'department': dept.name,
            'leader': _format_user(dept.leader),
            'specialisation': dept.specialisation or 'N/A',
            'num_teams': dept.num_teams,
            'unmanaged_teams': dept.num_unmanaged,
            'unique_engineers': len(member_user_ids),
        })
    return rows


def overall_totals():
    """Return a small dict of headline numbers for the cover page."""
    total_teams = Team.objects.count()
    total_unmanaged = Team.objects.filter(manager__isnull=True).count()
    total_departments = Department.objects.count()

    return {
        'generated_at': datetime.now().strftime('%d %B %Y, %H:%M'),
        'total_teams': total_teams,
        'total_unmanaged': total_unmanaged,
        'total_departments': total_departments,
    }
