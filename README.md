### Order Analytics Service

This project is a small, production-style Python service for analyzing e‑commerce order data using pandas.  
It loads orders from a CSV file and exposes a simple analytics API for revenue and customer insights.

### Features

- **Load orders from CSV**
  - Reads `orders.csv` into a pandas `DataFrame`.
  - Validates required columns:
    - `order_id`, `customer_name`, `product`, `category`, `price`, `quantity`, `order_date`
  - Coerces:
    - `price`, `quantity` → numeric (invalid/missing values become `0`).
    - `order_date` → `datetime` (rows with invalid dates are dropped; if all are invalid, an error is raised).

- **Revenue analytics**
  - **`calculate_total_revenue(orders)`**: total revenue across all orders.
  - **`revenue_by_product(orders)`**: revenue aggregated per product (pandas `Series`).
  - **`revenue_by_category(orders)`**: revenue aggregated per category (pandas `Series`).
  - **`top_customers(orders, n=3)`**: top _n_ customers by total revenue (pandas `DataFrame`).
  - **`monthly_revenue(orders)`**: revenue aggregated by calendar month (pandas `Series` indexed by month start).
  - Revenue is defined as `price * quantity` and stored in a derived `revenue` column.

### Project structure

- `order_analytics.py` – main library module with the analytics functions.
- `orders.csv` – sample order dataset used by the module.
- `test_order_analytics.py` – pytest test suite covering core and edge cases.
- `debug.md` – notes on identified bugs and their fixes.
- `summary.md` – high-level summary of the implementation and tests.

### Requirements

- Python 3.10+
- `pandas`
- `pytest` (for running tests)

If you are using a virtual environment, install dependencies with:

```bash
pip install pandas pytest
```

### Usage

Basic example of using the analytics API:

```python
import order_analytics as oa

orders = oa.load_orders("orders.csv")

total = oa.calculate_total_revenue(orders)
print("Total revenue:", total)

print("Revenue by product:")
print(oa.revenue_by_product(orders))

print("Revenue by category:")
print(oa.revenue_by_category(orders))

print("Top 3 customers:")
print(oa.top_customers(orders, n=3))

print("Monthly revenue:")
print(oa.monthly_revenue(orders))
```

### Running tests

From the project root (where `test_order_analytics.py` lives), run:

```bash
python -m pytest -q
```

All tests should pass and validate both normal behavior and edge cases (missing values, empty datasets, invalid inputs).
