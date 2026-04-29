from django.conf import settings
from django.db import models


class TeamType(models.Model):
    # Lookup table classifying a team's broad category (e.g. Platform, Product).
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    # A department in Sky's Engineering org. Contains many teams.
    name = models.CharField(max_length=150, unique=True)
    specialisation = models.CharField(max_length=200)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='led_departments',
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
