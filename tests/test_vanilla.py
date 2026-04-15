"""Tests for vanilla coupon bond calculations."""

import pytest
from bondduration import VanillaBond


class TestVanillaBondPrice:
    def test_par_bond(self):
        """When coupon rate = YTM, price = face value."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.06,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.price() == pytest.approx(1000.0, abs=0.01)

    def test_premium_bond(self):
        """When coupon rate > YTM, price > face value."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.08,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.price() > 1000.0

    def test_discount_bond(self):
        """When coupon rate < YTM, price < face value."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.04,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.price() < 1000.0

    def test_known_price(self):
        """Verify against a known price calculation.
        5% coupon, 10yr, semi-annual, 6% YTM.
        Price = 25 * [1-(1.03)^-20]/0.03 + 1000/(1.03)^20
              = 25 * 14.8775 + 1000 * 0.5537
              = 371.94 + 553.68 = 925.61
        """
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.price() == pytest.approx(925.61, abs=0.5)

    def test_annual_coupon(self):
        """Annual coupon bond pricing."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=5, frequency=1,
                           yield_to_maturity=0.05)
        assert bond.price() == pytest.approx(1000.0, abs=0.01)


class TestVanillaBondDuration:
    def test_macaulay_duration_positive(self):
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.macaulay_duration() > 0

    def test_macaulay_less_than_maturity(self):
        """Macaulay duration of a coupon bond < maturity."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.macaulay_duration() < 10.0

    def test_modified_less_than_macaulay(self):
        """Modified duration < Macaulay duration."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.modified_duration() < bond.macaulay_duration()

    def test_known_duration(self):
        """Verify against known Macaulay duration.
        5% coupon, 10yr, semi-annual, 6% YTM -> Mac duration ≈ 7.80 years."""
        bond = VanillaBond(face_value=1000, coupon_rate=0.05,
                           years_to_maturity=10, frequency=2,
                           yield_to_maturity=0.06)
        assert bond.macaulay_duration() == pytest.approx(7.80, abs=0.1)

    def test_higher_coupon_lower_duration(self):
        """Higher coupon -> lower duration."""
        bond_low = VanillaBond(coupon_rate=0.02, years_to_maturity=10,
                               yield_to_maturity=0.05)
        bond_high = VanillaBond(coupon_rate=0.08, years_to_maturity=10,
                                yield_to_maturity=0.05)
        assert bond_high.macaulay_duration() < bond_low.macaulay_duration()

    def test_higher_yield_lower_duration(self):
        """Higher yield -> lower duration."""
        bond_low_y = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                                  yield_to_maturity=0.03)
        bond_high_y = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                                   yield_to_maturity=0.08)
        assert bond_high_y.macaulay_duration() < bond_low_y.macaulay_duration()


class TestConvexity:
    def test_convexity_positive(self):
        bond = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                           yield_to_maturity=0.06)
        assert bond.convexity() > 0

    def test_longer_maturity_higher_convexity(self):
        bond_5y = VanillaBond(coupon_rate=0.05, years_to_maturity=5,
                              yield_to_maturity=0.06)
        bond_30y = VanillaBond(coupon_rate=0.05, years_to_maturity=30,
                               yield_to_maturity=0.06)
        assert bond_30y.convexity() > bond_5y.convexity()


class TestDollarDuration:
    def test_dv01_positive(self):
        bond = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                           yield_to_maturity=0.06)
        assert bond.dollar_duration() > 0

    def test_yield_change_price_down(self):
        """Yield increase -> price decrease."""
        bond = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                           yield_to_maturity=0.06)
        new_price = bond.yield_change_price(0.01)  # +100bps
        assert new_price < bond.price()

    def test_yield_change_price_up(self):
        """Yield decrease -> price increase."""
        bond = VanillaBond(coupon_rate=0.05, years_to_maturity=10,
                           yield_to_maturity=0.06)
        new_price = bond.yield_change_price(-0.01)  # -100bps
        assert new_price > bond.price()
