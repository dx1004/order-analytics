"""
Pytest test suite for the ``order_analytics`` module.

These tests cover:
- Loading orders from CSV.
- Total revenue calculation.
- Revenue by product.
- Revenue by category.
- Top customers.
- Monthly revenue.

The suite also exercises edge cases, including:
- Missing values and invalid types.
- Empty datasets.
- Invalid arguments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import pytest

import order_analytics as oa


def _write_csv(tmp_path: Path, name: str, rows: Iterable[str]) -> Path:
    """
    Helper to write a CSV file under ``tmp_path``.

    Parameters
    ----------
    tmp_path:
        Temporary directory provided by pytest.
    name:
        File name to create.
    rows:
        Iterable of CSV lines (already comma-separated).
    """
    path = tmp_path / name
    content = "\n".join(rows)
    path.write_text(content, encoding="utf-8")
    return path


@pytest.fixture
def sample_orders_df() -> pd.DataFrame:
    """Return a small, in-memory DataFrame matching the sample orders.csv."""
    data = {
        "order_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
        "customer_name": [
            "Alice",
            "Bob",
            "Charlie",
            "Alice",
            "Bob",
            "Diana",
            "Evan",
            "Alice",
            "Charlie",
            "Diana",
        ],
        "product": [
            "Laptop",
            "Phone",
            "Desk",
            "Mouse",
            "Chair",
            "Headphones",
            "Monitor",
            "Keyboard",
            "Lamp",
            "Desk",
        ],
        "category": [
            "Electronics",
            "Electronics",
            "Furniture",
            "Electronics",
            "Furniture",
            "Electronics",
            "Electronics",
            "Electronics",
            "Furniture",
            "Furniture",
        ],
        "price": [1200, 800, 300, 25, 150, 200, 400, 100, 80, 300],
        "quantity": [1, 1, 1, 2, 1, 1, 1, 1, 2, 1],
        "order_date": [
            "1/5/2024",
            "1/6/2024",
            "1/7/2024",
            "2/10/2024",
            "2/12/2024",
            "2/15/2024",
            "3/2/2024",
            "3/5/2024",
            "3/7/2024",
            "3/9/2024",
        ],
    }
    df = pd.DataFrame(data)
    # Apply the same validation logic as load_orders would.
    oa._validate_orders_df(df)  # type: ignore[attr-defined]
    oa._ensure_revenue_column(df)  # type: ignore[attr-defined]
    return df


### load_orders tests ###


def test_load_orders_success(tmp_path: Path) -> None:
    """load_orders should correctly load and validate a well-formed CSV."""
    rows = [
        "order_id,customer_name,product,category,price,quantity,order_date",
        "1,Alice,Laptop,Electronics,1000,1,2024-01-01",
        "2,Bob,Phone,Electronics,800,2,2024-01-02",
    ]
    csv_path = _write_csv(tmp_path, "orders.csv", rows)

    df = oa.load_orders(csv_path)

    assert isinstance(df, pd.DataFrame)
    assert set(df.columns) >= {
        "order_id",
        "customer_name",
        "product",
        "category",
        "price",
        "quantity",
        "order_date",
        "revenue",
    }
    # Revenue = price * quantity
    assert df.loc[0, "revenue"] == 1000 * 1
    assert df.loc[1, "revenue"] == 800 * 2


def test_load_orders_missing_file_raises() -> None:
    """load_orders should raise FileNotFoundError for a missing path."""
    with pytest.raises(FileNotFoundError):
        oa.load_orders("non_existent_orders.csv")


def test_load_orders_invalid_date_rows_dropped(tmp_path: Path) -> None:
    """Rows with invalid order_date values should be dropped."""
    rows = [
        "order_id,customer_name,product,category,price,quantity,order_date",
        "1,Alice,Laptop,Electronics,1000,1,NOT_A_DATE",
        "2,Bob,Phone,Electronics,800,2,2024-01-02",
    ]
    csv_path = _write_csv(tmp_path, "orders_invalid_date.csv", rows)

    df = oa.load_orders(csv_path)

    # Only the valid row should remain.
    assert len(df) == 1
    assert df.iloc[0]["order_id"] == 2


def test_load_orders_all_invalid_dates_raises(tmp_path: Path) -> None:
    """If all order_date values are invalid, load_orders should raise ValueError."""
    rows = [
        "order_id,customer_name,product,category,price,quantity,order_date",
        "1,Alice,Laptop,Electronics,1000,1,NOT_A_DATE",
        "2,Bob,Phone,Electronics,800,2,INVALID",
    ]
    csv_path = _write_csv(tmp_path, "orders_all_invalid_dates.csv", rows)

    with pytest.raises(ValueError):
        oa.load_orders(csv_path)


def test_load_orders_missing_required_column_raises(tmp_path: Path) -> None:
    """If a required column is missing, load_orders should raise ValueError."""
    rows = [
        "order_id,customer_name,product,category,price,quantity",  # missing order_date
        "1,Alice,Laptop,Electronics,1000,1",
    ]
    csv_path = _write_csv(tmp_path, "orders_missing_col.csv", rows)

    with pytest.raises(ValueError):
        oa.load_orders(csv_path)


### total revenue tests ###


def test_calculate_total_revenue_basic(sample_orders_df: pd.DataFrame) -> None:
    """calculate_total_revenue should compute correct total from sample data."""
    total = oa.calculate_total_revenue(sample_orders_df.copy())
    # Total revenue computed from sample_orders_df
    # Alice: 1200*1 + 25*2 + 100*1 = 1350
    # Bob: 800*1 + 150*1 = 950
    # Charlie: 300*1 + 80*2 = 460
    # Diana: 200*1 + 300*1 = 500
    # Evan: 400*1 = 400
    expected_total = 1350 + 950 + 460 + 500 + 400
    assert total == pytest.approx(expected_total)


def test_calculate_total_revenue_empty_df() -> None:
    """Empty DataFrame should result in total revenue of 0.0."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "customer_name",
            "product",
            "category",
            "price",
            "quantity",
            "order_date",
        ]
    )
    # Validation will pass (columns exist), but DataFrame is empty.
    total = oa.calculate_total_revenue(empty_df)
    assert total == 0.0


def test_calculate_total_revenue_invalid_orders_type_raises() -> None:
    """Passing a non-DataFrame to calculate_total_revenue should raise TypeError."""
    with pytest.raises(TypeError):
        oa.calculate_total_revenue([])  # type: ignore[arg-type]


### revenue by product tests ###


def test_revenue_by_product_basic(sample_orders_df: pd.DataFrame) -> None:
    """revenue_by_product should aggregate revenue per product."""
    series = oa.revenue_by_product(sample_orders_df.copy())

    assert "Laptop" in series.index
    assert "Desk" in series.index
    # Laptop: 1200 * 1
    assert series["Laptop"] == pytest.approx(1200)
    # Mouse: 25 * 2
    assert series["Mouse"] == pytest.approx(50)


def test_revenue_by_product_empty_df() -> None:
    """Empty DataFrame should yield an empty revenue Series."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "customer_name",
            "product",
            "category",
            "price",
            "quantity",
            "order_date",
        ]
    )
    series = oa.revenue_by_product(empty_df)
    assert series.empty
    assert series.name == "revenue"


### revenue by category tests ###


def test_revenue_by_category_basic(sample_orders_df: pd.DataFrame) -> None:
    """revenue_by_category should aggregate revenue per category."""
    series = oa.revenue_by_category(sample_orders_df.copy())

    assert "Electronics" in series.index
    assert "Furniture" in series.index

    # Compute expected totals.
    electronics_total = (
        1200 * 1  # Laptop
        + 800 * 1  # Phone
        + 25 * 2  # Mouse
        + 200 * 1  # Headphones
        + 400 * 1  # Monitor
        + 100 * 1  # Keyboard
    )
    furniture_total = (
        300 * 1  # Desk
        + 150 * 1  # Chair
        + 80 * 2  # Lamp
        + 300 * 1  # Desk
    )

    assert series["Electronics"] == pytest.approx(electronics_total)
    assert series["Furniture"] == pytest.approx(furniture_total)


def test_revenue_by_category_empty_df() -> None:
    """Empty DataFrame should yield an empty revenue Series."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "customer_name",
            "product",
            "category",
            "price",
            "quantity",
            "order_date",
        ]
    )
    series = oa.revenue_by_category(empty_df)
    assert series.empty
    assert series.name == "revenue"


### top customers tests ###


def test_top_customers_default_n(sample_orders_df: pd.DataFrame) -> None:
    """top_customers should return the top 3 customers by revenue by default."""
    df = oa.top_customers(sample_orders_df.copy())

    # Alice: 1450, Bob: 950, Diana: 500, Evan: 400, Charlie: 460
    # Sorted desc: Alice, Bob, Diana, Charlie, Evan
    assert list(df["customer_name"]) == ["Alice", "Bob", "Diana"]
    assert df.iloc[0]["customer_name"] == "Alice"
    assert df.iloc[0]["revenue"] > df.iloc[1]["revenue"]


def test_top_customers_custom_n(sample_orders_df: pd.DataFrame) -> None:
    """top_customers should respect the provided n value."""
    df = oa.top_customers(sample_orders_df.copy(), n=2)
    assert len(df) == 2
    assert list(df["customer_name"]) == ["Alice", "Bob"]


def test_top_customers_invalid_n_type_raises(sample_orders_df: pd.DataFrame) -> None:
    """Non-integer n should raise TypeError."""
    with pytest.raises(TypeError):
        oa.top_customers(sample_orders_df.copy(), n=3.5)  # type: ignore[arg-type]


def test_top_customers_non_positive_n_raises(sample_orders_df: pd.DataFrame) -> None:
    """Non-positive n should raise ValueError."""
    with pytest.raises(ValueError):
        oa.top_customers(sample_orders_df.copy(), n=0)


def test_top_customers_empty_df() -> None:
    """Empty DataFrame should return an empty top customers DataFrame."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "customer_name",
            "product",
            "category",
            "price",
            "quantity",
            "order_date",
        ]
    )
    df = oa.top_customers(empty_df, n=3)
    assert df.empty
    assert list(df.columns) == ["customer_name", "revenue"]


### monthly revenue tests ###


def test_monthly_revenue_basic(sample_orders_df: pd.DataFrame) -> None:
    """monthly_revenue should aggregate revenue per calendar month."""
    series = oa.monthly_revenue(sample_orders_df.copy())

    # There should be three months: Jan, Feb, Mar 2024.
    assert len(series) == 3

    # Index should be Timestamp at month start.
    months = list(series.index)
    assert months[0].day == 1

    # Expected monthly totals:
    # January: orders 1001, 1002, 1003 -> 1200 + 800 + 300 = 2300
    # February: orders 1004, 1005, 1006 -> 25*2 + 150 + 200 = 400
    # March: orders 1007, 1008, 1009, 1010 -> 400 + 100 + 80*2 + 300 = 960
    assert series.iloc[0] == pytest.approx(2300)
    assert series.iloc[1] == pytest.approx(400)
    assert series.iloc[2] == pytest.approx(960)


def test_monthly_revenue_empty_df() -> None:
    """Empty DataFrame should yield an empty monthly revenue Series."""
    empty_df = pd.DataFrame(
        columns=[
            "order_id",
            "customer_name",
            "product",
            "category",
            "price",
            "quantity",
            "order_date",
        ]
    )
    series = oa.monthly_revenue(empty_df)
    assert series.empty
    assert series.name == "revenue"


### edge cases around missing values ###


def test_missing_numeric_values_treated_as_zero(tmp_path: Path) -> None:
    """
    Missing or invalid price/quantity values should be coerced to 0.
    """
    rows = [
        "order_id,customer_name,product,category,price,quantity,order_date",
        "1,Alice,Laptop,Electronics,,2,2024-01-01",  # missing price -> 0
        "2,Bob,Phone,Electronics,800,INVALID,2024-01-02",  # invalid quantity -> 0
    ]
    csv_path = _write_csv(tmp_path, "orders_missing_numeric.csv", rows)

    df = oa.load_orders(csv_path)
    # Both rows should remain.
    assert len(df) == 2
    # Revenue should be zero for both rows due to 0 in price or quantity.
    assert df["revenue"].tolist() == [0.0, 0.0]


def test_missing_non_numeric_values_preserved(tmp_path: Path) -> None:
    """
    Missing non-numeric values like product or category are allowed and
    should be preserved; revenue calculations should still work.
    """
    rows = [
        "order_id,customer_name,product,category,price,quantity,order_date",
        "1,Alice,,Electronics,100,1,2024-01-01",
        "2,,Phone,,200,1,2024-01-02",
    ]
    csv_path = _write_csv(tmp_path, "orders_missing_text.csv", rows)

    df = oa.load_orders(csv_path)
    assert len(df) == 2
    # Check that revenue is computed even when text fields are missing.
    assert df["revenue"].tolist() == [100.0, 200.0]

