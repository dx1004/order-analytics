### Bug: Incorrect expected total revenue in test

**Context**
- Module: `order_analytics.py`
- Test suite: `test_order_analytics.py`
- Failing test: `test_calculate_total_revenue_basic`

**Symptom**
- Running `pytest -q` produced a failure in `test_calculate_total_revenue_basic`.
- Actual total revenue returned by `calculate_total_revenue` was `3660.0`.
- The test expected `3760` and failed with:
  - `assert 3660.0 == 3760 ± 0.00376`

**Root cause**
- The implementation of `calculate_total_revenue` was correct; the error was in the test’s manual calculation of the expected total.
- Specifically, Alice’s revenue was miscomputed in the test comments and `expected_total`:
  - The test assumed: `Alice = 1200*1 + 25*2 + 100*1 = 1450`
  - Correct math is: `Alice = 1200*1 + 25*2 + 100*1 = 1350`
- Because Alice’s revenue was overstated by 100, the test’s `expected_total` was also overstated by 100 (3760 instead of the correct 3660).

**Fix**
- File: `test_order_analytics.py`
- Test: `test_calculate_total_revenue_basic`
- Changes:
  - Corrected the comment explaining Alice’s revenue from `1450` to `1350`.
  - Updated the `expected_total` computation to use `1350` instead of `1450`:
    - Before: `expected_total = 1450 + 950 + 460 + 500 + 400`
    - After:  `expected_total = 1350 + 950 + 460 + 500 + 400`

**Verification**
- Re-ran the test suite with:
  - `pytest -q`
- Result:
  - All tests now pass.
  - `calculate_total_revenue` returns `3660.0`, which matches the corrected `expected_total`.

