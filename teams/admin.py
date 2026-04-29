from django.contrib import admin

from .models import (
    AuditLog,
    CodeRepository,
    ContactChannel,
    Skill,
    Team,
    TeamDependency,
    TeamMember,
    TeamSkill,
)


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1


class TeamSkillInline(admin.TabularInline):
    model = TeamSkill
    extra = 1


class ContactChannelInline(admin.TabularInline):
    model = ContactChannel
    extra = 1


class CodeRepositoryInline(admin.TabularInline):
    model = CodeRepository
    extra = 1


class UpstreamDependencyInline(admin.TabularInline):
    model = TeamDependency
    fk_name = 'downstream'
    verbose_name = 'Upstream dependency (this team depends on...)'
    verbose_name_plural = 'Upstream dependencies (this team depends on...)'
    extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'team_type', 'manager')
    list_filter = ('department', 'team_type')
    search_fields = ('name', 'mission', 'description')
    inlines = [
        TeamMemberInline,
        TeamSkillInline,
        ContactChannelInline,
        CodeRepositoryInline,
        UpstreamDependencyInline,
    ]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TeamDependency)
class TeamDependencyAdmin(admin.ModelAdmin):
    list_display = ('downstream', 'upstream', 'description')
    search_fields = ('downstream__name', 'upstream__name')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'team', 'user')
    list_filter = ('action',)
    readonly_fields = ('timestamp',)
