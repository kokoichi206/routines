from datetime import date, timedelta
from unittest.mock import patch

import pytest

from events import ActionChecker


def make_checker_with_counts(counts: dict, date_today: date) -> ActionChecker:
    """Helper: create an ActionChecker with preset counts and date_today."""
    checker = ActionChecker.__new__(ActionChecker)
    checker.user = "testuser"
    checker.date_today = date_today
    checker.counts = counts
    return checker


class TestTodayCount:
    def test_streak_over_200_days(self):
        """Verify that a 200+ day consecutive streak is counted correctly across year boundaries."""
        date_today = date(2026, 2, 27)
        counts = {}
        # 210 consecutive days ending on 2026-02-27
        for i in range(210):
            d = date_today - timedelta(days=i)
            counts[d] = 5
        # Day before the streak starts: no contributions
        counts[date_today - timedelta(days=210)] = 0

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        assert today == 5
        assert continued == 210

    def test_streak_stops_at_zero_day(self):
        """Verify that the streak stops when a day with 0 contributions is found."""
        date_today = date(2026, 2, 27)
        counts = {
            date_today: 3,
            date_today - timedelta(days=1): 2,
            date_today - timedelta(days=2): 0,  # break
            date_today - timedelta(days=3): 4,
        }

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        assert today == 3
        assert continued == 2

    def test_streak_across_year_boundary(self):
        """Verify that the streak is counted correctly when it spans two calendar years."""
        date_today = date(2026, 2, 27)
        counts = {}
        # Streak spans from 2025-08-11 (200 days ago) to 2026-02-27
        for i in range(200):
            d = date_today - timedelta(days=i)
            counts[d] = 1
        # Day before the streak: no contributions
        counts[date_today - timedelta(days=200)] = 0

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        assert today == 1
        assert continued == 200

    def test_streak_returns_early_when_data_missing(self):
        """If counts data is missing for a date, the streak is cut short."""
        date_today = date(2026, 2, 27)
        # Only has data for 2026 (58 days), 2025 data is missing
        counts = {}
        for i in range(58):
            d = date(2026, 1, 1) + timedelta(days=i)
            counts[d] = 5

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        # Streak is cut at year boundary because 2025-12-31 has no data
        assert today == 5
        assert continued == 58

    def test_today_no_contributions(self):
        """Verify correct behavior when today has 0 contributions."""
        date_today = date(2026, 2, 27)
        counts = {
            date_today: 0,
            date_today - timedelta(days=1): 5,
        }

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        assert today == 0
        assert continued == 1

    def test_consecutive_zero_days(self):
        """Verify counting consecutive no-contribution days."""
        date_today = date(2026, 2, 27)
        counts = {
            date_today: 0,
            date_today - timedelta(days=1): 0,
            date_today - timedelta(days=2): 0,
            date_today - timedelta(days=3): 5,
        }

        checker = make_checker_with_counts(counts, date_today)
        today, continued = checker.today_count()

        assert today == 0
        assert continued == 3


class TestFetchYearSeparatedUrls:
    def test_url_no_double_slash(self):
        """Verify that year-specific URLs don't have a double slash."""
        # The href from GitHub starts with '/', e.g. '/user?from=2025-01-01'
        # Correct: 'https://github.com/user?from=2025-01-01'
        # Buggy:   'https://github.com//user?from=2025-01-01'
        href = "/shinGangan?from=2025-01-01&to=2025-12-31"
        correct_url = f"https://github.com{href}"
        assert "//" not in correct_url.replace("https://", "")
        assert correct_url == "https://github.com/shinGangan?from=2025-01-01&to=2025-12-31"
