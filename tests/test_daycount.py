"""Tests for day count conventions."""

import pytest
from datetime import date
from bondduration.daycount import actual_actual, thirty_360, actual_360, actual_365


class TestDayCount:
    def test_actual_actual_same_year(self):
        frac = actual_actual(date(2024, 1, 1), date(2024, 7, 1))
        # 182 days / 366 (leap year) = 0.4973
        assert frac == pytest.approx(0.4973, abs=0.01)

    def test_thirty_360_basic(self):
        frac = thirty_360(date(2024, 1, 15), date(2024, 7, 15))
        assert frac == pytest.approx(0.5, abs=0.001)

    def test_actual_360(self):
        frac = actual_360(date(2024, 1, 1), date(2024, 4, 1))
        assert frac == pytest.approx(91 / 360, abs=0.001)

    def test_actual_365(self):
        frac = actual_365(date(2024, 1, 1), date(2025, 1, 1))
        # 366 days (leap year) / 365
        assert frac == pytest.approx(366 / 365, abs=0.001)
