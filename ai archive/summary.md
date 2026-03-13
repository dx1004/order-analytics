### Project summary

- **order_analytics module**
  - Implemented `order_analytics.py` using pandas to analyze e-commerce orders loaded from CSV.
  - Added functions: `load_orders`, `calculate_total_revenue`, `revenue_by_product`, `revenue_by_category`, `top_customers`, and `monthly_revenue`.
  - Included type hints, docstrings, schema validation, and normalization:
    - Validates required columns and types.
    - Coerces `price` and `quantity` to numeric (invalid values → 0).
    - Parses `order_date` as datetime, dropping rows with invalid dates and raising an error if all dates are invalid.
  - Ensures a derived `revenue` column (`price * quantity`) is available for all analytics.

- **Test suite**
  - Created `test_order_analytics.py` using pytest.
  - Covered loading orders, total revenue, revenue by product/category, top customers, and monthly revenue.
  - Added edge case tests for:
    - Missing files and missing required columns.
    - Invalid and missing `order_date` values.
    - Empty datasets for each public function.
    - Invalid argument types/values (e.g., non-DataFrame inputs, invalid `n` for `top_customers`).
    - Missing or invalid numeric values (treated as 0) and missing text fields.

- **Debugging**
  - Investigated a failing test in `test_calculate_total_revenue_basic`.
  - Identified that the failure was due to an incorrect manual expected total (miscomputed Alice’s revenue).
  - Corrected the expected total and documented the issue and fix in `debug.md`.

