from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from organization.models import Department

from .models import Team, TeamDependency

# Test cases still need updting, some will fail currently

class TeamModelTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Platform', specialisation='Infra')

    def test_str_returns_name(self):
        team = Team.objects.create(name='Edge', mission='Run the edge', department=self.dept)
        self.assertEqual(str(team), 'Edge')

    def test_dependency_clean_rejects_self_loop(self):
        team = Team.objects.create(name='Edge', mission='Run the edge', department=self.dept)
        dep = TeamDependency(upstream=team, downstream=team)
        with self.assertRaises(ValidationError):
            dep.clean()


class TeamViewTests(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Platform', specialisation='Infra')
        self.team = Team.objects.create(
            name='Edge', mission='Run the edge CDN', department=self.dept,
        )

    def test_team_list_returns_200_and_lists_team(self):
        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edge')

    def test_team_detail_404_for_missing(self):
        response = self.client.get(reverse('team_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_email_team_redirects_when_anonymous(self):
        response = self.client.get(reverse('email_team', args=[self.team.pk]))
        self.assertEqual(response.status_code, 302)

    def test_search_finds_team_by_mission(self):
        response = self.client.get(reverse('team_list'), {'q': 'CDN'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edge')
