"""Day count conventions for bond calculations.

Different bond markets use different conventions for counting days
between dates, which affects accrued interest and price calculations.
"""

from datetime import date
import calendar


def actual_actual(start: date, end: date) -> float:
    """ACT/ACT day count fraction (ISDA).

    Used for US Treasury bonds. The actual number of days divided
    by the actual number of days in the year.
    """
    days = (end - start).days
    # Use the average year length across the period
    start_year_days = 366 if calendar.isleap(start.year) else 365
    end_year_days = 366 if calendar.isleap(end.year) else 365

    if start.year == end.year:
        return days / start_year_days

    # Period spans multiple years — weight by portion in each year
    year_end = date(start.year, 12, 31)
    days_in_start_year = (year_end - start).days
    days_in_end_year = (end - date(end.year, 1, 1)).days

    fraction = days_in_start_year / start_year_days
    for year in range(start.year + 1, end.year):
        yr_days = 366 if calendar.isleap(year) else 365
        fraction += 1.0  # full year
    fraction += days_in_end_year / end_year_days

    return fraction


def thirty_360(start: date, end: date) -> float:
    """30/360 day count fraction (US convention).

    Used for US corporate and municipal bonds. Each month is treated
    as having 30 days, and the year as having 360 days.
    """
    d1, m1, y1 = start.day, start.month, start.year
    d2, m2, y2 = end.day, end.month, end.year

    # Adjust day-of-month per 30/360 US convention
    if d1 == 31:
        d1 = 30
    if d2 == 31 and d1 >= 30:
        d2 = 30

    days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
    return days / 360


def actual_360(start: date, end: date) -> float:
    """ACT/360 day count fraction.

    Used for money market instruments. Actual days divided by 360.
    """
    return (end - start).days / 360


def actual_365(start: date, end: date) -> float:
    """ACT/365 Fixed day count fraction.

    Actual days divided by 365 (ignoring leap years).
    """
    return (end - start).days / 365


# Day count convention registry
DAY_COUNT_CONVENTIONS = {
    "ACT/ACT": actual_actual,
    "30/360": thirty_360,
    "ACT/360": actual_360,
    "ACT/365": actual_365,
}


def day_count_fraction(start: date, end: date,
                       convention: str = "ACT/ACT") -> float:
    """Calculate day count fraction using the specified convention."""
    func = DAY_COUNT_CONVENTIONS.get(convention)
    if func is None:
        raise ValueError(
            f"Unknown day count convention: {convention}. "
            f"Supported: {list(DAY_COUNT_CONVENTIONS.keys())}"
        )
    return func(start, end)
