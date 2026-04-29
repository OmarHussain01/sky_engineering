from django.contrib import admin

from .models import Department, TeamType


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialisation', 'leader')
    search_fields = ('name', 'specialisation')
    list_filter = ('specialisation',)
