from django.test import TestCase
from django.urls import reverse

from .models import Department, TeamType


class DepartmentModelTests(TestCase):
    def test_str_returns_name(self):
        d = Department.objects.create(name='Platform', specialisation='Infra')
        self.assertEqual(str(d), 'Platform')


class TeamTypeModelTests(TestCase):
    def test_str_returns_name(self):
        t = TeamType.objects.create(name='Product')
        self.assertEqual(str(t), 'Product')


class DepartmentViewTests(TestCase):
    def test_department_list_returns_200(self):
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)

    def test_department_detail_404_for_missing(self):
        response = self.client.get(reverse('department_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)
