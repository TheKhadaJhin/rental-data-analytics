"""Integration checks for generated data and analytical outputs."""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "rental_analytics.db"
REPORT_DATA_DIR = PROJECT_ROOT / "reports" / "data"


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "run_pipeline.py")],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_source_row_counts(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            properties = connection.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
            bookings = connection.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        self.assertEqual(properties, 12)
        self.assertGreater(bookings, 300)

    def test_booking_ids_are_unique(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            row = connection.execute(
                "SELECT COUNT(*), COUNT(DISTINCT booking_id) FROM bookings"
            ).fetchone()
        self.assertEqual(row[0], row[1])

    def test_data_quality_checks_pass(self) -> None:
        quality = pd.read_csv(REPORT_DATA_DIR / "data_quality_checks.csv")
        self.assertEqual(int(quality["issue_count"].sum()), 0)

    def test_monthly_metrics_are_valid(self) -> None:
        monthly = pd.read_csv(REPORT_DATA_DIR / "monthly_kpis.csv")
        self.assertEqual(len(monthly), 24)
        self.assertTrue(monthly["occupancy_pct"].between(0, 100).all())
        self.assertTrue((monthly["gross_booking_value_usd"] >= 0).all())

    def test_property_rankings_are_complete(self) -> None:
        properties = pd.read_csv(REPORT_DATA_DIR / "property_performance.csv")
        self.assertEqual(len(properties), 12)
        self.assertTrue((properties["gross_booking_value_usd"] >= 0).all())
        self.assertTrue(properties["revenue_rank_in_city"].notna().all())


if __name__ == "__main__":
    unittest.main()
