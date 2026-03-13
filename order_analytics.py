"""
Order analytics utilities for e-commerce datasets.

This module provides a small, production-ready API for loading order data
from a CSV file and computing common revenue-based metrics using pandas.

The expected CSV schema (column names):
- order_id
- customer_name
- product
- category
- price
- quantity
- order_date

All public functions are designed to be:
- type hinted
- documented via docstrings
- defensive with respect to invalid inputs
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd
from pandas import DataFrame, Series


_REQUIRED_COLUMNS: Final[set[str]] = {
    "order_id",
    "customer_name",
    "product",
    "category",
    "price",
    "quantity",
    "order_date",
}


def _validate_orders_df(df: DataFrame) -> None:
    """
    Validate that the provided DataFrame conforms to the expected orders schema.

    This function checks:
    - Presence of required columns.
    - Numeric types for ``price`` and ``quantity`` (coercible to float).
    - Datetime type for ``order_date`` (coercible to datetime).

    It mutates the DataFrame in-place to:
    - Coerce ``price`` and ``quantity`` to numeric, treating invalid values as 0.
    - Coerce ``order_date`` to datetime, dropping rows where coercion fails.

    Parameters
    ----------
    df:
        The orders DataFrame to validate and normalize.

    Raises
    ------
    TypeError
        If ``df`` is not a pandas DataFrame.
    ValueError
        If required columns are missing after basic validation.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("orders must be a pandas DataFrame.")

    missing = _REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"orders DataFrame is missing required columns: {sorted(missing)}")

    # Coerce numeric fields; invalid entries become NaN then filled with 0.
    for col in ("price", "quantity"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Coerce order_date to datetime; drop rows where conversion fails.
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    before_drop = len(df)
    df.dropna(subset=["order_date"], inplace=True)

    # Optional: if all dates were invalid, this is likely a data issue.
    if before_drop > 0 and df.empty:
        raise ValueError("All rows have invalid 'order_date' values; cannot proceed.")


def _ensure_revenue_column(df: DataFrame) -> None:
    """
    Ensure that a ``revenue`` column exists on the DataFrame.

    Revenue is defined as ``price * quantity``.

    Parameters
    ----------
    df:
        Orders DataFrame that has already passed ``_validate_orders_df``.
    """
    if "revenue" not in df.columns:
        df["revenue"] = df["price"] * df["quantity"]


def load_orders(file_path: str | Path) -> DataFrame:
    """
    Load orders from a CSV file into a pandas DataFrame.

    The returned DataFrame is validated and normalized according to the
    expected schema described in this module. Invalid numeric values for
    ``price`` and ``quantity`` are treated as 0. Invalid ``order_date``
    values cause their rows to be dropped.

    Parameters
    ----------
    file_path:
        Path to the CSV file containing order data.

    Returns
    -------
    pandas.DataFrame
        A validated and normalized orders DataFrame.

    Raises
    ------
    FileNotFoundError
        If the supplied path does not exist or is not a file.
    ValueError
        If the CSV cannot be parsed or is missing required columns.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Orders file not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - very unlikely branch
        raise ValueError(f"Failed to read orders CSV: {exc}") from exc

    _validate_orders_df(df)
    _ensure_revenue_column(df)
    return df


def calculate_total_revenue(orders: DataFrame) -> float:
    """
    Calculate total revenue across all orders.

    Revenue is defined as ``price * quantity`` per row.

    Parameters
    ----------
    orders:
        Orders DataFrame returned by ``load_orders`` or an equivalent
        DataFrame that satisfies the same schema.

    Returns
    -------
    float
        The total revenue. Returns 0.0 if the DataFrame is empty.

    Raises
    ------
    TypeError
        If ``orders`` is not a DataFrame.
    ValueError
        If required columns are missing.
    """
    _validate_orders_df(orders)
    if orders.empty:
        return 0.0

    _ensure_revenue_column(orders)
    total = float(orders["revenue"].sum())
    return total


def revenue_by_product(orders: DataFrame) -> Series:
    """
    Compute revenue aggregated by product.

    Parameters
    ----------
    orders:
        Orders DataFrame returned by ``load_orders`` or an equivalent
        DataFrame that satisfies the same schema.

    Returns
    -------
    pandas.Series
        A Series indexed by product, containing revenue per product
        sorted in descending order of revenue. The Series name is
        ``'revenue'``.

    Raises
    ------
    TypeError
        If ``orders`` is not a DataFrame.
    ValueError
        If required columns are missing.
    """
    _validate_orders_df(orders)
    if orders.empty:
        return pd.Series(dtype="float64", name="revenue")

    _ensure_revenue_column(orders)
    revenue_series = (
        orders.groupby("product", dropna=False)["revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    revenue_series.name = "revenue"
    return revenue_series


def revenue_by_category(orders: DataFrame) -> Series:
    """
    Compute revenue aggregated by product category.

    Parameters
    ----------
    orders:
        Orders DataFrame returned by ``load_orders`` or an equivalent
        DataFrame that satisfies the same schema.

    Returns
    -------
    pandas.Series
        A Series indexed by category, containing revenue per category
        sorted in descending order of revenue. The Series name is
        ``'revenue'``.

    Raises
    ------
    TypeError
        If ``orders`` is not a DataFrame.
    ValueError
        If required columns are missing.
    """
    _validate_orders_df(orders)
    if orders.empty:
        return pd.Series(dtype="float64", name="revenue")

    _ensure_revenue_column(orders)
    revenue_series = (
        orders.groupby("category", dropna=False)["revenue"]
        .sum()
        .sort_values(ascending=False)
    )
    revenue_series.name = "revenue"
    return revenue_series


def top_customers(orders: DataFrame, n: int = 3) -> DataFrame:
    """
    Return the top N customers by total revenue.

    Parameters
    ----------
    orders:
        Orders DataFrame returned by ``load_orders`` or an equivalent
        DataFrame that satisfies the same schema.
    n:
        Number of customers to return. Must be a positive integer.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with columns:
        - ``customer_name``
        - ``revenue``
        Sorted in descending order of revenue. If ``orders`` is empty,
        an empty DataFrame with the above columns is returned.

    Raises
    ------
    TypeError
        If ``orders`` is not a DataFrame.
    ValueError
        If required columns are missing or ``n`` is not positive.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer.")
    if n <= 0:
        raise ValueError("n must be a positive integer.")

    _validate_orders_df(orders)
    if orders.empty:
        return pd.DataFrame(columns=["customer_name", "revenue"])

    _ensure_revenue_column(orders)
    grouped = (
        orders.groupby("customer_name", dropna=False)["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    grouped.rename(columns={"revenue": "revenue"}, inplace=True)
    return grouped


def monthly_revenue(orders: DataFrame) -> Series:
    """
    Compute revenue aggregated by calendar month.

    Revenue is aggregated based on the ``order_date`` column.

    Parameters
    ----------
    orders:
        Orders DataFrame returned by ``load_orders`` or an equivalent
        DataFrame that satisfies the same schema.

    Returns
    -------
    pandas.Series
        A Series indexed by month (Timestamp at month start), containing
        total revenue per month, sorted by month ascending. The Series
        name is ``'revenue'``.

    Raises
    ------
    TypeError
        If ``orders`` is not a DataFrame.
    ValueError
        If required columns are missing.
    """
    _validate_orders_df(orders)
    if orders.empty:
        return pd.Series(dtype="float64", name="revenue")

    _ensure_revenue_column(orders)

    # Use month start frequency so each index represents a calendar month.
    monthly = (
        orders.set_index("order_date")
        .groupby(pd.Grouper(freq="MS"))["revenue"]
        .sum()
    )
    monthly.name = "revenue"
    # Drop months with zero revenue that may appear due to all-NaN groups.
    monthly = monthly[monthly != 0]
    return monthly


__all__ = [
    "load_orders",
    "calculate_total_revenue",
    "revenue_by_product",
    "revenue_by_category",
    "top_customers",
    "monthly_revenue",
]

