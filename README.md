# Bond Duration Calculator

A fixed income analytics library for calculating bond duration measures.

## Supported Instruments

- **Vanilla coupon bonds** (e.g., US Treasuries, fixed-rate corporates)

## Metrics

- **Macaulay Duration**: Weighted average time to receive cash flows,
  weighted by present value
- **Modified Duration**: Sensitivity of bond price to yield changes
- **Convexity**: Second-order price sensitivity to yield changes
- **Price**: Dirty price (sum of discounted cash flows)
- **Accrued Interest**: Interest accrued since last coupon date
- **Clean Price**: Dirty price minus accrued interest

## Usage

```python
from bondduration import VanillaBond

bond = VanillaBond(
    face_value=1000,
    coupon_rate=0.05,      # 5% annual coupon
    years_to_maturity=10,
    frequency=2,           # semi-annual
    yield_to_maturity=0.06 # 6% YTM
)

print(f"Price: ${bond.price():.2f}")
print(f"Macaulay Duration: {bond.macaulay_duration():.4f} years")
print(f"Modified Duration: {bond.modified_duration():.4f}")
print(f"Convexity: {bond.convexity():.4f}")
```

## Installation

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest -v
```
