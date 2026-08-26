"""Shared paths and project configuration."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_DATA_DIR = REPORTS_DIR / "data"
FIGURES_DIR = REPORTS_DIR / "figures"
DATABASE_PATH = PROCESSED_DATA_DIR / "rental_analytics.db"


def ensure_directories() -> None:
    """Create generated-output directories when they do not exist."""

    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        REPORTS_DIR,
        REPORT_DATA_DIR,
        FIGURES_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)

