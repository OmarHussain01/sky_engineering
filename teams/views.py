from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from organization.models import Department

from .forms import EmailTeamForm, ScheduleMeetingForm, TeamSearchForm
from .models import AuditLog, Team


# Lists every team. Supports a search box (?q=) and a department filter (?department=<id>).
@login_required
def team_list(request):
    form = TeamSearchForm(request.GET or None)
    teams = Team.objects.all().select_related('department', 'team_type').order_by('name')

    query = request.GET.get('q', '').strip()
    if query:
        teams = teams.filter(
            Q(name__icontains=query)
            | Q(mission__icontains=query)
            | Q(description__icontains=query)
            | Q(department__name__icontains=query)
        )

    department_id = request.GET.get('department')
    if department_id:
        teams = teams.filter(department_id=department_id)

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'form': form,
        'query': query,
        'departments': Department.objects.all().order_by('name'),
        'selected_department': department_id or '',
    })


# Shows a single team's overview: mission, manager, members, contact channels, code repos.
@login_required
def team_detail(request, pk):
    team = get_object_or_404(
        Team.objects.select_related('department', 'team_type', 'manager'),
        pk=pk,
    )
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': team.teammember_set.select_related('user').all(),
        'channels': team.contactchannel_set.all(),
        'repos': team.coderepository_set.all(),
    })


# Lists a team's skills, grouped by proficiency level, beginner, intermdeiate and advanced.
@login_required
def team_skills(request, pk):
    team = get_object_or_404(Team, pk=pk)
    grouped = {'advanced': [], 'intermediate': [], 'beginner': []}
    for ts in team.teamskill_set.select_related('skill').all():
        grouped.setdefault(ts.proficiency, []).append(ts)
    return render(request, 'teams/team_skills.html', {
        'team': team,
        'grouped': grouped,
    })


# Shows upstream and downstream dependencies for a team.
@login_required
def team_dependencies(request, pk):
    team = get_object_or_404(Team, pk=pk)
    return render(request, 'teams/team_dependencies.html', {
        'team': team,
        'upstreams': team.upstream_links.select_related('upstream').all(),
        'downstreams': team.downstream_links.select_related('downstream').all(),
    })


# Sends an email to every team member.
@login_required
def email_team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = EmailTeamForm(request.POST)
        if form.is_valid():
            recipients = list({
                m.user.email for m in team.teammember_set.select_related('user').all()
                if m.user.email
            })
            for ch in team.contactchannel_set.filter(kind='email'):
                if ch.value:
                    recipients.append(ch.value)

            send_mail(
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['body'],
                from_email=request.user.email or None,
                recipient_list=recipients,
                fail_silently=False,
            )
            AuditLog.objects.create(
                team=team,
                user=request.user,
                action='email_team',
                details=f"To {len(recipients)} recipients. Subject: {form.cleaned_data['subject']}",
            )
            messages.success(request, f"Email sent to {len(recipients)} recipient(s).")
            return redirect('team_detail', pk=team.pk)
    else:
        form = EmailTeamForm()
    return render(request, 'teams/email_team.html', {'team': team, 'form': form})


# Records a meeting request and emails the team. 
@login_required
def schedule_meeting(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = ScheduleMeetingForm(request.POST)
        if form.is_valid():
            recipients = list({
                m.user.email for m in team.teammember_set.select_related('user').all()
                if m.user.email
            })
            details = (
                f"Date/time: {form.cleaned_data['date_time']}\n"
                f"Platform: {form.cleaned_data['platform']}\n\n"
                f"{form.cleaned_data['message']}"
            )
            send_mail(
                subject=f"Meeting request: {team.name}",
                message=details,
                from_email=request.user.email or None,
                recipient_list=recipients,
                fail_silently=False,
            )
            AuditLog.objects.create(
                team=team,
                user=request.user,
                action='schedule_meeting',
                details=details,
            )
            messages.success(request, "Meeting request sent.")
            return redirect('team_detail', pk=team.pk)
    else:
        form = ScheduleMeetingForm()
    return render(request, 'teams/schedule_meeting.html', {'team': team, 'form': form})
