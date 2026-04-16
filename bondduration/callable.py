"""Callable bond pricing via binomial interest rate tree.

A callable bond gives the issuer the right to redeem the bond early
at a predetermined call price. This embedded call option reduces the
bond's value relative to an otherwise identical non-callable bond.

Pricing uses backward induction through a recombining binomial tree
of short rates, checking at each node whether the issuer would
exercise the call.
"""

import math


def build_rate_tree(r0, sigma, n_steps, dt=1.0):
    """Build a recombining binomial tree of short interest rates.

    Uses a log-normal model where rates at each node are:
        rate(i, j) = r0 * exp((2j - i) * sigma * sqrt(dt))

    where i is the time step and j is the number of up-moves.

    Args:
        r0: initial short rate (annual, decimal)
        sigma: volatility of the short rate
        n_steps: number of time steps
        dt: length of each time step in years

    Returns:
        List of lists: tree[i][j] = rate at step i, state j
    """
    tree = []
    for i in range(n_steps + 1):
        level = []
        for j in range(i + 1):
            rate = r0 * math.exp((2 * j - i) * sigma * math.sqrt(dt))
            level.append(rate)
        tree.append(level)
    return tree


def price_bond_on_tree(face_value, coupon_rate, n_steps, rate_tree,
                       call_price=None, call_start=0, dt=1.0):
    """Price a bond (optionally callable) via backward induction.

    At each node, the hold value is the discounted expected value of
    the next period's prices plus coupon. For callable bonds, the
    price at each callable node is capped at the call price.

    Args:
        face_value: par value of the bond
        coupon_rate: annual coupon rate
        n_steps: number of periods in the tree
        rate_tree: rate tree from build_rate_tree
        call_price: call price (None for non-callable)
        call_start: first period when the call is exercisable
        dt: time step in years

    Returns:
        Clean price at the root node (time 0)
    """
    coupon = face_value * coupon_rate * dt

    # Terminal values: principal only (no final coupon)
    prices = [face_value] * (n_steps + 1)

    # Backward induction
    for i in range(n_steps - 1, -1, -1):
        new_prices = []
        for j in range(i + 1):
            r = rate_tree[i][j]
            # Discounted expected value
            pv = 0.5 * (prices[j] + prices[j + 1]) / (1 + r * dt)
            hold_value = pv

            # Call decision
            if call_price is not None and i >= call_start:
                node_price = max(hold_value, call_price)
            else:
                node_price = hold_value

            new_prices.append(node_price)
        prices = new_prices

    return round(prices[0], 6)


def option_adjusted_duration(face_value, coupon_rate, n_steps,
                             r0, sigma, call_price=None,
                             call_start=0, dt=1.0, dy=0.0001):
    """Compute the option-adjusted duration via finite differences.

    OAD = (P(r0 - dy) - P(r0 + dy)) / (2 * P(r0) * dy)
    """
    tree = build_rate_tree(r0, sigma, n_steps, dt)
    p = price_bond_on_tree(face_value, coupon_rate, n_steps, tree,
                           call_price, call_start, dt)

    tree_up = build_rate_tree(r0 + dy, sigma, n_steps, dt)
    p_up = price_bond_on_tree(face_value, coupon_rate, n_steps, tree_up,
                              call_price, call_start, dt)

    tree_down = build_rate_tree(r0 - dy, sigma, n_steps, dt)
    p_down = price_bond_on_tree(face_value, coupon_rate, n_steps, tree_down,
                                call_price, call_start, dt)

    oad = (p_down - p_up) / (2 * p * dy)
    return round(oad, 4)


def option_adjusted_convexity(face_value, coupon_rate, n_steps,
                              r0, sigma, call_price=None,
                              call_start=0, dt=1.0, dy=0.0001):
    """Compute option-adjusted convexity via finite differences.

    OAC = (P(r0 + dy) + P(r0 - dy) - 2*P(r0)) / (P(r0) * dy^2)
    """
    tree = build_rate_tree(r0, sigma, n_steps, dt)
    p = price_bond_on_tree(face_value, coupon_rate, n_steps, tree,
                           call_price, call_start, dt)

    tree_up = build_rate_tree(r0 + dy, sigma, n_steps, dt)
    p_up = price_bond_on_tree(face_value, coupon_rate, n_steps, tree_up,
                              call_price, call_start, dt)

    tree_down = build_rate_tree(r0 - dy, sigma, n_steps, dt)
    p_down = price_bond_on_tree(face_value, coupon_rate, n_steps, tree_down,
                                call_price, call_start, dt)

    oac = (p_up + p_down - 2 * p) / (p * dy ** 2)
    return round(oac, 4)
