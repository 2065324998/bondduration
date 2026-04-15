"""Tests for cash flow generation."""

import pytest
from bondduration.cashflows import generate_coupon_schedule, discount_factor


class TestCouponSchedule:
    def test_semiannual_10yr(self):
        cfs = generate_coupon_schedule(1000, 0.06, 10, frequency=2)
        assert len(cfs) == 20
        assert cfs[0].amount == pytest.approx(30.0)
        assert cfs[0].time == pytest.approx(0.5)
        assert cfs[-1].amount == pytest.approx(1030.0)
        assert cfs[-1].cf_type == "coupon+principal"

    def test_annual_5yr(self):
        cfs = generate_coupon_schedule(1000, 0.05, 5, frequency=1)
        assert len(cfs) == 5
        assert cfs[0].amount == pytest.approx(50.0)
        assert cfs[-1].amount == pytest.approx(1050.0)

    def test_quarterly(self):
        cfs = generate_coupon_schedule(1000, 0.08, 2, frequency=4)
        assert len(cfs) == 8
        assert cfs[0].amount == pytest.approx(20.0)

    def test_invalid_frequency(self):
        with pytest.raises(ValueError):
            generate_coupon_schedule(1000, 0.05, 10, frequency=0)

    def test_invalid_maturity(self):
        with pytest.raises(ValueError):
            generate_coupon_schedule(1000, 0.05, 0, frequency=2)


class TestDiscountFactor:
    def test_zero_yield(self):
        assert discount_factor(0.0, 5.0, 2) == pytest.approx(1.0)

    def test_positive_yield(self):
        # (1 + 0.03)^-10 = 0.7441
        df = discount_factor(0.06, 5.0, 2)
        assert df == pytest.approx(0.7441, abs=0.001)

    def test_longer_time_lower_factor(self):
        df_short = discount_factor(0.05, 2.0, 2)
        df_long = discount_factor(0.05, 10.0, 2)
        assert df_long < df_short
