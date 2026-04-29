from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Department


# Lists every department with a count of its teams.
@login_required
def department_list(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'organization/department_list.html', {
        'departments': departments,
    })


# Shows one department: leader, specialisation, and the teams it owns.
@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    teams = department.team_set.all().order_by('name')
    return render(request, 'organization/department_detail.html', {
        'department': department,
        'teams': teams,
    })


# Cross-department view of how teams depend on each other (sourced from TeamDependency).
@login_required
def org_relationships(request):
    departments = Department.objects.all().prefetch_related('team_set').order_by('name')
    return render(request, 'organization/org_relationships.html', {
        'departments': departments,
    })
