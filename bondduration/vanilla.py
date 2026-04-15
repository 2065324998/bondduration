"""Vanilla coupon bond implementation."""

from bondduration.cashflows import generate_coupon_schedule, discount_factor, CashFlow


class VanillaBond:
    """A standard fixed-rate coupon bond (e.g., US Treasury note/bond).

    Supports semi-annual and annual coupon frequencies. All duration
    measures are expressed in years.
    """

    def __init__(self, face_value: float = 1000, coupon_rate: float = 0.05,
                 years_to_maturity: float = 10, frequency: int = 2,
                 yield_to_maturity: float = 0.05):
        """
        Args:
            face_value: Par value of the bond (typically 1000)
            coupon_rate: Annual coupon rate (decimal, e.g., 0.05 = 5%)
            years_to_maturity: Years from settlement to maturity
            frequency: Coupon payments per year (2 = semi-annual)
            yield_to_maturity: Annual yield to maturity (decimal)
        """
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years_to_maturity = years_to_maturity
        self.frequency = frequency
        self.yield_to_maturity = yield_to_maturity

        self._cashflows = generate_coupon_schedule(
            face_value, coupon_rate, years_to_maturity, frequency
        )

    def cashflows(self) -> list[CashFlow]:
        """Get the bond's cash flow schedule."""
        return list(self._cashflows)

    def price(self) -> float:
        """Calculate the dirty price (sum of PV of all cash flows).

        Price = Σ CF_t / (1 + y/n)^(t*n)

        where y = YTM, n = frequency, t = time in years.
        """
        total = 0.0
        for cf in self._cashflows:
            df = discount_factor(self.yield_to_maturity, cf.time,
                                 self.frequency)
            total += cf.amount * df
        return round(total, 6)

    def macaulay_duration(self) -> float:
        """Calculate Macaulay duration in years.

        D_mac = Σ (t * PV(CF_t)) / Price

        The weighted average time to receive cash flows, weighted
        by their present value as a proportion of the bond price.
        """
        price = self.price()
        if price == 0:
            return 0.0

        weighted_sum = 0.0
        for cf in self._cashflows:
            df = discount_factor(self.yield_to_maturity, cf.time,
                                 self.frequency)
            pv = cf.amount * df
            weighted_sum += cf.time * pv

        return round(weighted_sum / price, 6)

    def modified_duration(self) -> float:
        """Calculate modified duration.

        D_mod = D_mac / (1 + y/n)

        Measures the percentage change in price for a 1% change
        in yield (approximately).
        """
        mac = self.macaulay_duration()
        return round(mac / (1 + self.yield_to_maturity / self.frequency), 6)

    def convexity(self) -> float:
        """Calculate convexity.

        C = Σ (t * (t + 1/n) * PV(CF_t)) / (Price * (1 + y/n)^2)

        Second-order measure of price sensitivity to yield changes.
        """
        price = self.price()
        if price == 0:
            return 0.0

        y = self.yield_to_maturity
        n = self.frequency
        factor = (1 + y / n) ** 2

        weighted_sum = 0.0
        for cf in self._cashflows:
            df = discount_factor(y, cf.time, n)
            pv = cf.amount * df
            weighted_sum += cf.time * (cf.time + 1.0 / n) * pv

        return round(weighted_sum / (price * factor), 6)

    def dollar_duration(self) -> float:
        """DV01 — dollar value of a basis point.

        The approximate dollar change in price for a 1 basis point
        (0.01%) change in yield.
        """
        return round(self.modified_duration() * self.price() / 10000, 6)

    def yield_change_price(self, yield_change: float) -> float:
        """Estimate new price for a given yield change using duration + convexity.

        ΔP/P ≈ -D_mod * Δy + 0.5 * C * (Δy)^2
        """
        price = self.price()
        mod_dur = self.modified_duration()
        conv = self.convexity()

        pct_change = -mod_dur * yield_change + 0.5 * conv * yield_change ** 2
        return round(price * (1 + pct_change), 2)
