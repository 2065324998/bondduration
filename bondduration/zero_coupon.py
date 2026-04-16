"""Zero coupon bond implementation.

Zero coupon bonds pay no periodic coupons. They are issued at a discount
to face value and redeemed at par at maturity.
"""

from bondduration.cashflows import CashFlow


class ZeroCouponBond:
    """A zero coupon (discount) bond.

    Args:
        face_value: Par value redeemed at maturity
        years_to_maturity: Years from settlement to maturity
        yield_to_maturity: Annual yield (decimal)
        compounding: Compounding periods per year (0 = continuous,
                     1 = annual, 2 = semi-annual, 4 = quarterly)
    """

    def __init__(self, face_value: float = 1000,
                 years_to_maturity: float = 10,
                 yield_to_maturity: float = 0.05,
                 compounding: int = 2):
        self.face_value = face_value
        self.years_to_maturity = years_to_maturity
        self.yield_to_maturity = yield_to_maturity
        self.compounding = compounding

    # ------------------------------------------------------------------
    # Cash flows
    # ------------------------------------------------------------------

    def cashflows(self) -> list[CashFlow]:
        """Return the single cash flow at maturity."""
        return [CashFlow(
            time=self.years_to_maturity,
            amount=self.face_value,
            cf_type="principal",
        )]

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    def price(self) -> float:
        """Present value of the face-value payment.

        P = F / (1 + y)^T
        """
        y = self.yield_to_maturity
        T = self.years_to_maturity
        return round(self.face_value / (1 + y) ** T, 6)

    # ------------------------------------------------------------------
    # Duration measures
    # ------------------------------------------------------------------

    def macaulay_duration(self) -> float:
        """Macaulay duration — always equals years to maturity."""
        return self.years_to_maturity

    def modified_duration(self) -> float:
        """Modified duration.

        D_mod = D_mac / (1 + y) = T / (1 + y)
        """
        return round(self.years_to_maturity / (1 + self.yield_to_maturity), 6)

    # ------------------------------------------------------------------
    # Convexity
    # ------------------------------------------------------------------

    def convexity(self) -> float:
        """Convexity of the zero coupon bond.

        C = T^2
        """
        return self.years_to_maturity ** 2

    # ------------------------------------------------------------------
    # Risk measures
    # ------------------------------------------------------------------

    def dollar_duration(self) -> float:
        """DV01 — dollar value of a basis point."""
        return round(self.modified_duration() * self.price() / 10000, 6)

    def yield_change_price(self, yield_change: float) -> float:
        """Estimated price after a parallel yield shift.

        Uses the duration + convexity approximation:
        ΔP/P ≈ −D_mod · Δy + ½ · C · (Δy)²
        """
        p = self.price()
        d = self.modified_duration()
        c = self.convexity()
        pct = -d * yield_change + 0.5 * c * yield_change ** 2
        return round(p * (1 + pct), 2)

    # ------------------------------------------------------------------
    # YTM solver
    # ------------------------------------------------------------------

    @staticmethod
    def ytm_from_price(price: float, face_value: float = 1000,
                       years_to_maturity: float = 10,
                       compounding: int = 2) -> float:
        """Solve for the yield to maturity given a market price.

        y = (F/P)^{1/T} − 1
        """
        T = years_to_maturity
        return round((face_value / price) ** (1.0 / T) - 1, 6)
