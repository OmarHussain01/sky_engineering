"""
Shared test fixtures.

Author: Danyal Khan
Module: 5COSC021W - CW2 Individual Element

A single helper that creates a small but representative organisation
hierarchy using the group's actual models. Used by every test module
to keep setup consistent.
"""

from django.contrib.auth import get_user_model

from organization.models import Department
from teams.models import Team, TeamMember, ContactChannel


def create_test_user(username='reporter', password='Strong-Pass-1!'):
    """Return a logged-in test user."""
    User = get_user_model()
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f'{username}@example.com',
    )
    return user, password


def create_sample_organisation():
    """Build a small but realistic organisation tree for tests.

    Returns a dict with the created entities for assertion convenience.
    """
    User = get_user_model()

    # Two department leaders + two team managers
    alice = User.objects.create_user(
        username='alice', password='X1234567!',
        first_name='Alice', last_name='Khan',
    )
    bob = User.objects.create_user(
        username='bob', password='X1234567!',
        first_name='Bob', last_name='Singh',
    )
    carol = User.objects.create_user(
        username='carol', password='X1234567!',
        first_name='Carol', last_name='Lee',
    )

    # Two departments
    platform = Department.objects.create(
        name='Platform Engineering Test',
        specialisation='Cloud, observability, CI/CD',
        leader=alice,
    )
    streaming = Department.objects.create(
        name='Streaming Test',
        specialisation='Video delivery, encoding',
        leader=bob,
    )

    # Three teams: two managed, one unmanaged
    observability = Team.objects.create(
        name='Test Observability',
        mission='Logs and metrics',
        department=platform,
        manager=alice,
    )
    ContactChannel.objects.create(
        team=observability, kind='slack', value='#test-observability',
    )
    TeamMember.objects.create(team=observability, user=alice, role='Lead')
    TeamMember.objects.create(team=observability, user=bob, role='Engineer')
    TeamMember.objects.create(team=observability, user=carol, role='Engineer')

    ci_cd = Team.objects.create(
        name='Test CI/CD',
        mission='Build pipelines',
        department=platform,
        manager=alice,
    )
    TeamMember.objects.create(team=ci_cd, user=bob, role='Engineer')

    encoding = Team.objects.create(
        name='Test Encoding',
        mission='Video encoding',
        department=streaming,
        manager=None,  # deliberately unmanaged
    )
    TeamMember.objects.create(team=encoding, user=carol, role='Engineer')

    return {
        'platform': platform,
        'streaming': streaming,
        'users': [alice, bob, carol],
        'teams': [observability, ci_cd, encoding],
    }
