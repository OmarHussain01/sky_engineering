from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from organization.models import Department, TeamType


class Team(models.Model):
    # An engineering team. FKs across to organisation for Department + TeamType.
    name = models.CharField(max_length=150, unique=True)
    mission = models.TextField()
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    team_type = models.ForeignKey(TeamType, null=True, blank=True, on_delete=models.SET_NULL)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_teams',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    # Through model linking Django's auth User to a Team with a role.
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.team.name}"


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TeamSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES)

    def __str__(self):
        return f"{self.team.name} - {self.skill.name} ({self.proficiency})"


class TeamDependency(models.Model):
    upstream = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='downstream_links')
    downstream = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='upstream_links')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('upstream', 'downstream')

    def clean(self):
        if self.upstream_id and self.downstream_id and self.upstream_id == self.downstream_id:
            raise ValidationError("A team cannot depend on itself.")

    def __str__(self):
        return f"{self.downstream.name} depends on {self.upstream.name}"


class ContactChannel(models.Model):
    KIND_CHOICES = [
        ('slack', 'Slack'),
        ('teams', 'Teams'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.team.name} {self.kind}: {self.value}"


class CodeRepository(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    url = models.URLField()

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    # Records emails sent and meetings scheduled, this satisfies the audit trail requirement.
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.action}"
