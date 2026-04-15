"""Cash flow generation and discounting utilities."""

from dataclasses import dataclass


@dataclass
class CashFlow:
    """A single cash flow at a point in time."""
    time: float       # time in years from settlement
    amount: float     # cash flow amount
    cf_type: str      # "coupon", "principal", "coupon+principal"


def generate_coupon_schedule(face_value: float, coupon_rate: float,
                             years_to_maturity: float,
                             frequency: int = 2) -> list[CashFlow]:
    """Generate the cash flow schedule for a vanilla coupon bond.

    Args:
        face_value: Par/face value of the bond
        coupon_rate: Annual coupon rate (e.g., 0.05 for 5%)
        years_to_maturity: Years until maturity
        frequency: Coupon payments per year (1=annual, 2=semi-annual, 4=quarterly)

    Returns:
        List of CashFlow objects in chronological order
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    if years_to_maturity <= 0:
        raise ValueError("Years to maturity must be positive")

    coupon_per_period = face_value * coupon_rate / frequency
    num_periods = int(years_to_maturity * frequency)
    period_length = 1.0 / frequency

    cashflows = []
    for i in range(1, num_periods + 1):
        t = i * period_length
        if i == num_periods:
            # Last period: coupon + principal
            cashflows.append(CashFlow(
                time=t,
                amount=coupon_per_period + face_value,
                cf_type="coupon+principal",
            ))
        else:
            cashflows.append(CashFlow(
                time=t,
                amount=coupon_per_period,
                cf_type="coupon",
            ))

    return cashflows


def discount_factor(ytm: float, time: float,
                    frequency: int = 2) -> float:
    """Calculate the discount factor for a cash flow.

    Uses the standard bond pricing convention where the periodic
    yield is ytm/frequency and periods = time * frequency.

    Args:
        ytm: Annual yield to maturity
        time: Time in years
        frequency: Compounding frequency per year
    """
    periodic_rate = ytm / frequency
    periods = time * frequency
    return 1.0 / (1 + periodic_rate) ** periods
