"""Run the SQL analysis and create recruiter-friendly reports and charts."""

from __future__ import annotations

import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import (
    DATABASE_PATH,
    FIGURES_DIR,
    REPORT_DATA_DIR,
    REPORTS_DIR,
    SQL_DIR,
    ensure_directories,
)


QUERY_FILES = {
    "data_quality_checks": "02_data_quality_checks.sql",
    "monthly_kpis": "03_monthly_kpis.sql",
    "property_performance": "04_property_performance.sql",
    "channel_performance": "05_channel_performance.sql",
    "city_trends": "06_city_trends.sql",
}

COLORS = {
    "navy": "#16324F",
    "blue": "#2F80ED",
    "teal": "#00A896",
    "orange": "#F2994A",
    "slate": "#607D8B",
}


def run_queries(connection: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    """Execute every portfolio SQL file and save the results as CSV."""

    results: dict[str, pd.DataFrame] = {}
    for output_name, sql_file in QUERY_FILES.items():
        query = (SQL_DIR / sql_file).read_text(encoding="utf-8")
        frame = pd.read_sql_query(query, connection)
        frame.to_csv(REPORT_DATA_DIR / f"{output_name}.csv", index=False)
        results[output_name] = frame
    return results


def apply_chart_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "#F8FAFC",
            "axes.edgecolor": "#CBD5E1",
            "axes.labelcolor": "#334155",
            "axes.titlecolor": COLORS["navy"],
            "font.size": 10,
            "axes.titleweight": "bold",
            "grid.color": "#E2E8F0",
            "grid.linewidth": 0.8,
        }
    )


def save_monthly_occupancy_chart(monthly: pd.DataFrame) -> None:
    frame = monthly.copy()
    frame["month"] = pd.to_datetime(frame["month"])
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(
        frame["month"],
        frame["occupancy_pct"],
        color=COLORS["blue"],
        linewidth=2.4,
        marker="o",
        markersize=4,
    )
    ax.fill_between(frame["month"], frame["occupancy_pct"], alpha=0.12, color=COLORS["blue"])
    ax.set_title("Monthly Portfolio Occupancy", loc="left", pad=14)
    ax.set_ylabel("Occupancy (%)")
    ax.set_xlabel("")
    ax.grid(axis="y")
    ax.spines[["top", "right"]].set_visible(False)
    fig.autofmt_xdate(rotation=35)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "monthly_occupancy.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_monthly_revenue_chart(monthly: pd.DataFrame) -> None:
    frame = monthly.copy()
    frame["month"] = pd.to_datetime(frame["month"])
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(
        frame["month"],
        frame["gross_booking_value_usd"],
        width=20,
        color=COLORS["teal"],
        alpha=0.9,
    )
    ax.set_title("Monthly Gross Booking Value", loc="left", pad=14)
    ax.set_ylabel("USD")
    ax.set_xlabel("")
    ax.grid(axis="y")
    ax.spines[["top", "right"]].set_visible(False)
    ax.ticklabel_format(style="plain", axis="y")
    fig.autofmt_xdate(rotation=35)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "monthly_revenue.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def save_channel_chart(channels: pd.DataFrame) -> None:
    frame = channels.sort_values("gross_booking_value_usd", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.barh(
        frame["channel"],
        frame["gross_booking_value_usd"],
        color=[COLORS["slate"], COLORS["orange"], COLORS["blue"], COLORS["teal"]],
    )
    ax.bar_label(bars, labels=[f"${value:,.0f}" for value in frame["gross_booking_value_usd"]], padding=5)
    ax.set_title("Gross Booking Value by Channel", loc="left", pad=14)
    ax.set_xlabel("USD")
    ax.grid(axis="x")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, frame["gross_booking_value_usd"].max() * 1.18)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "channel_performance.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_executive_summary(results: dict[str, pd.DataFrame]) -> None:
    monthly = results["monthly_kpis"]
    properties = results["property_performance"]
    channels = results["channel_performance"]
    quality = results["data_quality_checks"]

    total_revenue = monthly["gross_booking_value_usd"].sum()
    total_booked_nights = int(monthly["booked_nights"].sum())
    total_available_nights = int(monthly["available_nights"].sum())
    weighted_occupancy = 100 * total_booked_nights / total_available_nights
    completed = int(monthly["completed_bookings"].sum())
    cancelled = int(monthly["cancelled_bookings"].sum())
    cancellation_rate = 100 * cancelled / (completed + cancelled)
    first_year_revenue = monthly.iloc[:12]["gross_booking_value_usd"].sum()
    second_year_revenue = monthly.iloc[12:]["gross_booking_value_usd"].sum()
    year_growth = 100 * (second_year_revenue - first_year_revenue) / first_year_revenue

    top_property = properties.iloc[0]
    top_channel = channels.iloc[0]
    high_cancel_channel = channels.sort_values("cancellation_rate_pct", ascending=False).iloc[0]
    peak_month = monthly.loc[monthly["gross_booking_value_usd"].idxmax()]
    issue_count = int(quality["issue_count"].sum())

    summary = f"""# Executive Summary

## Portfolio snapshot

- **Gross booking value:** ${total_revenue:,.0f}
- **Completed bookings:** {completed:,}
- **Booked nights:** {total_booked_nights:,}
- **Weighted occupancy:** {weighted_occupancy:.1f}%
- **Cancellation rate:** {cancellation_rate:.1f}%
- **Data quality issues detected:** {issue_count}

## Findings

1. **{top_property['property_name']}** generated the highest property revenue at **${top_property['gross_booking_value_usd']:,.0f}**, with {top_property['occupancy_pct']:.1f}% occupancy.
2. **{top_channel['channel']}** was the leading channel, contributing **{top_channel['revenue_share_pct']:.1f}%** of portfolio revenue.
3. The strongest revenue month was **{peak_month['month']}**, reaching **${peak_month['gross_booking_value_usd']:,.0f}**.
4. Second-year revenue changed by **{year_growth:+.1f}%** versus the first year as the portfolio matured and additional properties became active.
5. **{high_cancel_channel['channel']}** had the highest channel cancellation rate at **{high_cancel_channel['cancellation_rate_pct']:.1f}%**.

## Recommended actions

- Review pricing and minimum-stay rules before high-demand months, using occupancy and RevPAR together rather than revenue alone.
- Protect the strongest channel mix while testing direct-booking incentives to reduce dependency on third-party platforms.
- Investigate cancellation patterns for {high_cancel_channel['channel']} and compare booking lead times before changing policies.
- Use the city and property rankings to prioritize experiments on low-occupancy listings without discounting the entire portfolio.

## Method notes

The analysis uses deterministic synthetic data covering January 2024 through December 2025. Checkout dates are excluded from occupied-night counts. Monthly lodging revenue is allocated to the actual stay night; cleaning fees are attributed to the check-in month. All figures are for portfolio demonstration only.
"""
    (REPORTS_DIR / "executive_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_directories()
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("SQLite database is missing. Run src/load_data.py first.")

    apply_chart_style()
    with sqlite3.connect(DATABASE_PATH) as connection:
        results = run_queries(connection)

    save_monthly_occupancy_chart(results["monthly_kpis"])
    save_monthly_revenue_chart(results["monthly_kpis"])
    save_channel_chart(results["channel_performance"])
    create_executive_summary(results)
    print(f"Created {len(results)} CSV reports, 3 charts, and an executive summary.")


if __name__ == "__main__":
    main()
