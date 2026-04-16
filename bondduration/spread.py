"""Yield spread analytics for fixed income instruments."""


def z_spread(cashflows, benchmark_rates, market_price,
             frequency=2, tol=1e-8, max_iter=200):
    """Compute the Z-spread of a bond over a benchmark spot curve.

    The Z-spread is the constant spread z that, when added to each
    benchmark spot rate, makes the present value of cash flows equal
    to the market price:

        P = Σ CF_t / (1 + (r_t + z)/n)^(n·t)

    Uses Newton-Raphson iteration to solve for z.

    Args:
        cashflows: list of (time, amount) tuples — each cash flow
        benchmark_rates: dict mapping time -> spot rate (annual, decimal)
        market_price: observed market price of the bond
        frequency: compounding frequency (1=annual, 2=semi-annual)
        tol: convergence tolerance for the objective function
        max_iter: maximum Newton-Raphson iterations

    Returns:
        Z-spread as a decimal (e.g., 0.015 = 150 bps)

    Raises:
        ValueError: if Newton-Raphson does not converge
    """
    n = frequency

    def _get_rate(t):
        """Look up or interpolate benchmark rate at time t."""
        if t in benchmark_rates:
            return benchmark_rates[t]
        times = sorted(benchmark_rates.keys())
        if t <= times[0]:
            return benchmark_rates[times[0]]
        if t >= times[-1]:
            return benchmark_rates[times[-1]]
        for i in range(len(times) - 1):
            if times[i] <= t <= times[i + 1]:
                t1, t2 = times[i], times[i + 1]
                w = (t - t1) / (t2 - t1)
                return benchmark_rates[t1] * (1 - w) + benchmark_rates[t2] * w
        return benchmark_rates[times[-1]]

    def _price(z):
        """PV of cash flows at spread z."""
        total = 0.0
        for t, cf in cashflows:
            r = _get_rate(t)
            total += cf / (1 + r + z) ** t
        return total

    def _dprice(z):
        """Derivative of PV with respect to z (dP/dz)."""
        total = 0.0
        for t, cf in cashflows:
            r = _get_rate(t)
            base = 1 + r + z
            total += -t * cf / base ** (t + 1)
        return total

    # Newton-Raphson
    z = 0.01  # initial guess: 100bps
    for _ in range(max_iter):
        f_val = _price(z) - market_price
        if abs(f_val) < tol:
            return round(z, 8)
        df_val = _dprice(z)
        if abs(df_val) < 1e-15:
            raise ValueError("Zero derivative in Newton-Raphson")
        z = z - f_val / df_val

    raise ValueError(
        f"Newton-Raphson did not converge after {max_iter} iterations"
    )
