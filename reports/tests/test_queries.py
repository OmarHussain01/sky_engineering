"""
Tests for the queries module.

Author: Danyal Khan
Module: 5COSC021W - CW2 Individual Element

These tests verify the data layer in isolation - if a generator
produces wrong numbers, this is the first place to look.

Test plan covered:
    Q-01  Empty database returns sensible defaults
    Q-02  Teams summary lists every team in the registry
    Q-03  Unmanaged report only includes teams with no manager
    Q-04  Department summary aggregates team and engineer counts
    Q-05  Overall totals match the underlying counts
"""

from django.test import TestCase

from reports import queries
from .fixtures import create_sample_organisation


class EmptyDatabaseTests(TestCase):
    """Q-01 - boundary case: nothing in the registry yet."""

    def test_teams_summary_is_empty_list(self):
        self.assertEqual(queries.teams_summary(), [])

    def test_unmanaged_teams_is_empty_list(self):
        self.assertEqual(queries.teams_without_managers(), [])

    def test_department_summary_is_empty_list(self):
        self.assertEqual(queries.department_summary(), [])

    def test_overall_totals_are_zero(self):
        totals = queries.overall_totals()
        self.assertEqual(totals['total_teams'], 0)
        self.assertEqual(totals['total_unmanaged'], 0)
        self.assertEqual(totals['total_departments'], 0)


class PopulatedDatabaseTests(TestCase):
    """Q-02 to Q-05 - all the happy-path checks."""

    def setUp(self):
        self.sample = create_sample_organisation()

    def test_teams_summary_lists_every_team(self):
        rows = queries.teams_summary()
        self.assertEqual(len(rows), 3)
        team_names = {row['team'] for row in rows}
        self.assertEqual(team_names,
                         {'Test Observability', 'Test CI/CD', 'Test Encoding'})

    def test_teams_summary_marks_unassigned_managers(self):
        rows = queries.teams_summary()
        encoding = next(r for r in rows if r['team'] == 'Test Encoding')
        self.assertIn('Unassigned', encoding['manager'])

    def test_teams_summary_member_counts_are_correct(self):
        rows = queries.teams_summary()
        by_name = {r['team']: r['members'] for r in rows}
        self.assertEqual(by_name['Test Observability'], 3)
        self.assertEqual(by_name['Test CI/CD'], 1)
        self.assertEqual(by_name['Test Encoding'], 1)

    def test_unmanaged_report_only_returns_unmanaged_teams(self):
        rows = queries.teams_without_managers()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['team'], 'Test Encoding')

    def test_department_summary_counts_teams_correctly(self):
        rows = queries.department_summary()
        by_name = {r['department']: r for r in rows}
        self.assertEqual(by_name['Platform Engineering Test']['num_teams'], 2)
        self.assertEqual(by_name['Streaming Test']['num_teams'], 1)

    def test_department_summary_counts_unique_engineers(self):
        # Bob is in two Platform teams but should only be counted once.
        rows = queries.department_summary()
        platform_row = next(
            r for r in rows if r['department'] == 'Platform Engineering Test'
        )
        self.assertEqual(platform_row['unique_engineers'], 3)

    def test_department_summary_flags_unmanaged_count(self):
        rows = queries.department_summary()
        by_name = {r['department']: r for r in rows}
        self.assertEqual(by_name['Streaming Test']['unmanaged_teams'], 1)
        self.assertEqual(
            by_name['Platform Engineering Test']['unmanaged_teams'], 0,
        )

    def test_overall_totals_match_database(self):
        totals = queries.overall_totals()
        self.assertEqual(totals['total_teams'], 3)
        self.assertEqual(totals['total_unmanaged'], 1)
        self.assertEqual(totals['total_departments'], 2)
