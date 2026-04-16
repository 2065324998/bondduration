"""Portfolio immunization — duration-matching allocation.

Immunization is a fixed-income strategy that structures a bond portfolio
so that its value is protected against parallel shifts in interest rates.
The portfolio's modified duration is matched to the liability duration.
"""


def portfolio_duration(bonds, amounts):
    """Compute the modified duration of a portfolio.

    Args:
        bonds: list of bond objects (must have price() and modified_duration())
        amounts: list of dollar amounts invested in each bond

    Returns:
        Market-value-weighted modified duration of the portfolio.
    """
    total_value = sum(amounts)
    if total_value == 0:
        return 0.0

    weighted_dur = 0.0
    for bond, amt in zip(bonds, amounts):
        weight = amt / total_value
        weighted_dur += weight * bond.macaulay_duration()

    return round(weighted_dur, 6)


def portfolio_convexity(bonds, amounts):
    """Compute the convexity of a portfolio.

    Args:
        bonds: list of bond objects (must have price() and convexity())
        amounts: list of dollar amounts invested in each bond

    Returns:
        Market-value-weighted convexity of the portfolio.
    """
    total_value = sum(amounts)
    if total_value == 0:
        return 0.0

    weighted_conv = 0.0
    for bond, amt in zip(bonds, amounts):
        weight = amt / total_value
        weighted_conv += weight * bond.convexity()

    return round(weighted_conv, 6)


def immunize_two_bonds(target_duration, target_value, bond_short, bond_long):
    """Allocate between two bonds to match a target modified duration.

    Uses the duration-matching equation:
        w_s · D_s + w_l · D_l = D_target
        w_s + w_l = 1

    where w_s and w_l are the portfolio weight fractions.

    Args:
        target_duration: desired portfolio modified duration
        target_value: total dollar amount to invest
        bond_short: the shorter-duration bond
        bond_long: the longer-duration bond

    Returns:
        (amount_short, amount_long) — dollar amounts to invest

    Raises:
        ValueError: if the target duration is outside the range
                    [D_short, D_long]
    """
    d_short = bond_short.macaulay_duration()
    d_long = bond_long.macaulay_duration()

    if d_short > d_long:
        d_short, d_long = d_long, d_short
        bond_short, bond_long = bond_long, bond_short

    if target_duration < d_short or target_duration > d_long:
        raise ValueError(
            f"Target duration {target_duration} is outside the range "
            f"[{d_short}, {d_long}]"
        )

    if d_long == d_short:
        return (target_value / 2, target_value / 2)

    w_short = (d_long - target_duration) / (d_long - d_short)
    w_long = 1.0 - w_short

    return (round(w_short * target_value, 2),
            round(w_long * target_value, 2))


def immunize_three_bonds(target_duration, target_convexity, target_value,
                         bond_a, bond_b, bond_c):
    """Allocate among three bonds to match both duration and convexity.

    Solves the system:
        w_a · D_a + w_b · D_b + w_c · D_c = D_target
        w_a · C_a + w_b · C_b + w_c · C_c = C_target
        w_a + w_b + w_c = 1

    Substituting w_c = 1 - w_a - w_b:
        w_a · (D_a - D_c) + w_b · (D_b - D_c) = D_target - D_c
        w_a · (C_a - C_c) + w_b · (C_b - C_c) = C_target - C_c

    Uses Cramer's rule to solve the 2×2 system.

    Args:
        target_duration: desired modified duration
        target_convexity: desired convexity
        target_value: total dollar amount
        bond_a, bond_b, bond_c: three bond objects

    Returns:
        (amount_a, amount_b, amount_c) — dollar amounts

    Raises:
        ValueError: if no valid allocation exists
    """
    d_a = bond_a.macaulay_duration()
    d_b = bond_b.macaulay_duration()
    d_c = bond_c.macaulay_duration()

    c_a = bond_a.convexity()
    c_b = bond_b.convexity()
    c_c = bond_c.convexity()

    # Coefficients for the 2x2 system after substituting w_c = 1 - w_a - w_b
    a11 = d_a - d_c
    a12 = d_b - d_c
    a21 = c_a - c_c
    a22 = c_b - c_c

    b1 = target_duration - d_c
    b2 = target_convexity - c_c

    det = a11 * a22 - a12 * a21
    if abs(det) < 1e-12:
        raise ValueError("Bonds are linearly dependent — no unique solution")

    w_a = (b1 * a22 - b2 * a12) / det
    w_b = (a11 * b2 - a21 * b1) / det
    w_c = 1.0 - w_a - w_b

    if w_a < -1e-9 or w_b < -1e-9 or w_c < -1e-9:
        raise ValueError(
            f"No valid non-negative allocation: "
            f"w_a={w_a:.4f}, w_b={w_b:.4f}, w_c={w_c:.4f}"
        )

    w_a = max(w_a, 0.0)
    w_b = max(w_b, 0.0)
    w_c = max(w_c, 0.0)
    total_w = w_a + w_b + w_c
    w_a /= total_w
    w_b /= total_w
    w_c /= total_w

    return (round(w_a * target_value, 2),
            round(w_b * target_value, 2),
            round(w_c * target_value, 2))
