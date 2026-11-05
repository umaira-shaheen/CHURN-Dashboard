"""Auditable calculations for the subscription cancellation dashboard.

Each row is a customer (CustomerID values are unique in the supplied dataset).
Churn == 1 is treated as a cancellation, per the individual work plan.
"""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ("CustomerID", "SubscriptionType", "MonthlyCharges", "Churn")
PLAN_ORDER = ("Basic", "Standard", "Premium")
BAND_EDGES = (4.99, 8.0, 11.0, 14.0, 17.0, 20.0)
BAND_LABELS = ("4.99–<8", "8–<11", "11–<14", "14–<17", "17–<20")
ALL_PLANS = "All plans"


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Check the dataset, then add ordered, non-time monthly-charge bands.

    Raise a user-facing ValueError rather than silently discarding customers.
    Bounds intentionally follow the supplied data's ~4.99 to ~19.99 charges.
    """
    missing = sorted(set(REQUIRED_COLUMNS) - set(raw.columns))
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    frame = raw.copy()
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("The required fields contain missing values; please clean the CSV.")

    if frame["CustomerID"].duplicated().any():
        raise ValueError("CustomerID must be unique so customers are not counted twice.")

    frame["MonthlyCharges"] = pd.to_numeric(frame["MonthlyCharges"], errors="coerce")
    frame["Churn"] = pd.to_numeric(frame["Churn"], errors="coerce")
    if frame[["MonthlyCharges", "Churn"]].isna().any().any():
        raise ValueError("MonthlyCharges and Churn must contain numeric values.")
    if not frame["Churn"].isin([0, 1]).all():
        raise ValueError("Churn must contain only 0 (retained) and 1 (cancelled).")

    observed_plans = set(frame["SubscriptionType"].unique())
    if not observed_plans.issubset(set(PLAN_ORDER)):
        raise ValueError("SubscriptionType must use Basic, Standard, or Premium.")

    charges = frame["MonthlyCharges"]
    if not ((charges >= BAND_EDGES[0]) & (charges < BAND_EDGES[-1])).all():
        raise ValueError("This dashboard uses charge bands from 4.99 to under 20; data outside that range was found.")

    frame["ChargeBand"] = pd.cut(
        charges,
        bins=BAND_EDGES,
        labels=BAND_LABELS,
        right=False,
        include_lowest=True,
        ordered=True,
    )
    return frame


def overall_summary(frame: pd.DataFrame) -> dict:
    customers = int(frame["CustomerID"].nunique())
    cancelled = int(frame["Churn"].sum())
    return {
        "customers": customers,
        "cancelled": cancelled,
        "cancellation_pct": cancelled / customers * 100 if customers else 0.0,
    }


def plan_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """One row per subscription type; counts and percentages share a denominator."""
    grouped = frame.groupby("SubscriptionType", observed=True).agg(
        customers=("CustomerID", "nunique"), cancelled=("Churn", "sum")
    )
    grouped = grouped.reindex(PLAN_ORDER, fill_value=0).reset_index()
    grouped["cancellation_pct"] = grouped["cancelled"].div(grouped["customers"].replace(0, float("nan"))).mul(100)
    return grouped


def charge_band_summary(frame: pd.DataFrame, selected_plan: str = ALL_PLANS) -> pd.DataFrame:
    """Calculate rate within each band and selected plan (never a raw count trend)."""
    if selected_plan != ALL_PLANS:
        if selected_plan not in PLAN_ORDER:
            raise ValueError(f"Unknown plan: {selected_plan}")
        frame = frame.loc[frame["SubscriptionType"] == selected_plan]

    grouped = frame.groupby("ChargeBand", observed=False).agg(
        customers=("CustomerID", "nunique"), cancelled=("Churn", "sum")
    )
    grouped = grouped.reindex(BAND_LABELS, fill_value=0).reset_index()
    grouped["ChargeBand"] = grouped["ChargeBand"].astype(str)
    grouped["cancellation_pct"] = grouped["cancelled"].div(grouped["customers"].replace(0, float("nan"))).mul(100)
    return grouped
