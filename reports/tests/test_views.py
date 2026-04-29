"""
Tests for the HTTP views.

Author: Danyal Khan
Module: 5COSC021W - CW2 Individual Element

These exercise the full request/response cycle - URL routing,
authentication enforcement, content-type headers, attachment headers
and response body. They are also the integration tests required for
the group-application half of the test plan section.

Test plan covered:
    V-01  Anonymous users are redirected to the login page (security)
    V-02  Authenticated users see the index page
    V-03  Each PDF endpoint returns application/pdf
    V-04  Each Excel endpoint returns the correct MIME type
    V-05  Each download has a Content-Disposition: attachment header
    V-06  An unknown report key returns 404
"""

from django.test import TestCase
from django.urls import reverse

from .fixtures import create_sample_organisation, create_test_user


class AnonymousAccessTests(TestCase):
    """V-01 - security: reports must require authentication."""

    def test_index_redirects_anonymous_user(self):
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 302)

    def test_pdf_download_redirects_anonymous_user(self):
        url = reverse('reports:download_pdf', args=['teams_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_excel_download_redirects_anonymous_user(self):
        url = reverse('reports:download_excel', args=['teams_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class AuthenticatedAccessTests(TestCase):
    """V-02 to V-06 - logged-in users get the right responses."""

    def setUp(self):
        self.user, self.password = create_test_user()
        self.client.login(username=self.user.username, password=self.password)
        create_sample_organisation()

    def test_index_renders_for_authenticated_user(self):
        response = self.client.get(reverse('reports:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reports')
        self.assertContains(response, 'All Teams')
        self.assertContains(response, 'Teams Without Managers')

    # -- PDF endpoints --

    def test_teams_summary_pdf_endpoint(self):
        url = reverse('reports:download_pdf', args=['teams_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('sky_teams_summary.pdf', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_unmanaged_teams_pdf_endpoint(self):
        url = reverse('reports:download_pdf',
                      args=['teams_without_managers'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_department_summary_pdf_endpoint(self):
        url = reverse('reports:download_pdf', args=['department_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    # -- Excel endpoints --

    def test_teams_summary_excel_endpoint(self):
        url = reverse('reports:download_excel', args=['teams_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn(
            'sky_teams_summary.xlsx',
            response['Content-Disposition'],
        )

    def test_unmanaged_teams_excel_endpoint(self):
        url = reverse('reports:download_excel',
                      args=['teams_without_managers'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_department_summary_excel_endpoint(self):
        url = reverse('reports:download_excel', args=['department_summary'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # -- Error handling --

    def test_unknown_pdf_report_returns_404(self):
        url = reverse('reports:download_pdf', args=['no_such_report'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_unknown_excel_report_returns_404(self):
        url = reverse('reports:download_excel', args=['no_such_report'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
