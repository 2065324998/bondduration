"""Treasury Inflation-Protected Securities (TIPS) bond implementation.

TIPS are US Treasury securities whose principal is adjusted for changes
in the Consumer Price Index (CPI). Coupons are paid on the adjusted
principal, providing protection against inflation.
"""

from bondduration.cashflows import CashFlow


class TIPSBond:
    """A Treasury Inflation-Protected Security.

    Args:
        face_value: Original par value
        coupon_rate: Real coupon rate (annual, decimal)
        years_to_maturity: Years from settlement to maturity
        frequency: Coupon payments per year (typically 2)
        real_yield: Real yield to maturity (decimal)
        cpi_base: CPI index value at the bond's issue/base date
        cpi_schedule: dict mapping time (years) -> CPI value
                      for projected or observed CPI levels
    """

    def __init__(self, face_value: float = 1000,
                 coupon_rate: float = 0.02,
                 years_to_maturity: float = 5,
                 frequency: int = 2,
                 real_yield: float = 0.01,
                 cpi_base: float = 250.0,
                 cpi_schedule: dict = None):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.years_to_maturity = years_to_maturity
        self.frequency = frequency
        self.real_yield = real_yield
        self.cpi_base = cpi_base
        self.cpi_schedule = cpi_schedule or {}

    def index_ratio(self, time: float) -> float:
        """Get the CPI index ratio at a given time.

        The index ratio is CPI(time) / CPI(base). For dates not in
        the CPI schedule, returns the ratio for the nearest earlier
        observation (flat forward assumption).
        """
        if not self.cpi_schedule:
            return 1.0

        if time in self.cpi_schedule:
            return self.cpi_schedule[time] / self.cpi_base

        # Find nearest earlier observation
        earlier = [t for t in self.cpi_schedule if t <= time]
        if earlier:
            return self.cpi_schedule[max(earlier)] / self.cpi_base

        return 1.0

    def cashflows(self) -> list[CashFlow]:
        """Generate the inflation-adjusted cash flow schedule.

        Each coupon is computed on the face value at the real coupon
        rate. At maturity, the principal is the face value.
        """
        n = self.frequency
        coupon_per_period = self.face_value * self.coupon_rate / n
        num_periods = int(self.years_to_maturity * n)

        flows = []
        for i in range(1, num_periods + 1):
            t = i / n
            if i == num_periods:
                flows.append(CashFlow(
                    time=t,
                    amount=coupon_per_period + self.face_value,
                    cf_type="coupon+principal",
                ))
            else:
                flows.append(CashFlow(
                    time=t,
                    amount=coupon_per_period,
                    cf_type="coupon",
                ))
        return flows

    def price(self) -> float:
        """Dirty price of the TIPS bond.

        Discounts each cash flow at the real yield.
        """
        total = 0.0
        for cf in self.cashflows():
            df = 1.0 / (1 + self.real_yield / self.frequency) ** (
                self.frequency * cf.time
            )
            total += cf.amount * df
        return round(total, 6)

    def macaulay_duration(self) -> float:
        """Macaulay duration using real yield."""
        p = self.price()
        if p == 0:
            return 0.0
        weighted = 0.0
        for cf in self.cashflows():
            df = 1.0 / (1 + self.real_yield / self.frequency) ** (
                self.frequency * cf.time
            )
            weighted += cf.time * cf.amount * df
        return round(weighted / p, 6)

    def modified_duration(self) -> float:
        """Modified duration using real yield."""
        return round(
            self.macaulay_duration() / (1 + self.real_yield / self.frequency),
            6,
        )

    def convexity(self) -> float:
        """Convexity using real yield."""
        p = self.price()
        if p == 0:
            return 0.0
        n = self.frequency
        y = self.real_yield
        factor = (1 + y / n) ** 2
        weighted = 0.0
        for cf in self.cashflows():
            df = 1.0 / (1 + y / n) ** (n * cf.time)
            weighted += cf.time * (cf.time + 1.0 / n) * cf.amount * df
        return round(weighted / (p * factor), 6)

    @staticmethod
    def breakeven_inflation(nominal_yield: float,
                            real_yield: float) -> float:
        """Compute the breakeven inflation rate.

        The breakeven is the implied inflation rate at which a nominal
        bond and a TIPS bond offer equal returns.
        """
        return round(nominal_yield - real_yield, 6)
