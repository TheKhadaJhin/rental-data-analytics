"""Generate a deterministic, synthetic short-term-rental dataset.

The data contains no real guests, addresses, payment details, or customer
identifiers. Re-running the script produces the same dataset.
"""

from __future__ import annotations

import calendar
import csv
import random
from datetime import date, timedelta

from config import RAW_DATA_DIR, ensure_directories


RANDOM_SEED = 20260826
START_MONTH = date(2024, 1, 1)
MONTH_COUNT = 24
DATA_END_EXCLUSIVE = date(2026, 1, 1)

PROPERTIES = [
    {
        "property_id": "P001",
        "property_name": "Palermo Studio",
        "city": "Buenos Aires",
        "property_type": "Studio",
        "bedrooms": 1,
        "max_guests": 2,
        "active_from": "2024-01-01",
        "acquisition_channel": "Organic",
        "base_nightly_rate_usd": 68,
    },
    {
        "property_id": "P002",
        "property_name": "Recoleta Classic",
        "city": "Buenos Aires",
        "property_type": "Apartment",
        "bedrooms": 2,
        "max_guests": 4,
        "active_from": "2024-01-01",
        "acquisition_channel": "Partner",
        "base_nightly_rate_usd": 92,
    },
    {
        "property_id": "P003",
        "property_name": "San Telmo Loft",
        "city": "Buenos Aires",
        "property_type": "Loft",
        "bedrooms": 1,
        "max_guests": 3,
        "active_from": "2024-01-01",
        "acquisition_channel": "Organic",
        "base_nightly_rate_usd": 76,
    },
    {
        "property_id": "P004",
        "property_name": "Nueva Córdoba Flat",
        "city": "Córdoba",
        "property_type": "Apartment",
        "bedrooms": 1,
        "max_guests": 3,
        "active_from": "2024-01-01",
        "acquisition_channel": "Referral",
        "base_nightly_rate_usd": 51,
    },
    {
        "property_id": "P005",
        "property_name": "Güemes Terrace",
        "city": "Córdoba",
        "property_type": "Apartment",
        "bedrooms": 2,
        "max_guests": 5,
        "active_from": "2024-01-01",
        "acquisition_channel": "Partner",
        "base_nightly_rate_usd": 64,
    },
    {
        "property_id": "P006",
        "property_name": "Alta Gracia Retreat",
        "city": "Córdoba",
        "property_type": "House",
        "bedrooms": 2,
        "max_guests": 5,
        "active_from": "2024-03-01",
        "acquisition_channel": "Referral",
        "base_nightly_rate_usd": 58,
    },
    {
        "property_id": "P007",
        "property_name": "Mendoza Central Suite",
        "city": "Mendoza",
        "property_type": "Apartment",
        "bedrooms": 1,
        "max_guests": 2,
        "active_from": "2024-01-01",
        "acquisition_channel": "Organic",
        "base_nightly_rate_usd": 61,
    },
    {
        "property_id": "P008",
        "property_name": "Chacras Garden House",
        "city": "Mendoza",
        "property_type": "House",
        "bedrooms": 3,
        "max_guests": 7,
        "active_from": "2024-01-01",
        "acquisition_channel": "Partner",
        "base_nightly_rate_usd": 118,
    },
    {
        "property_id": "P009",
        "property_name": "Wine Route Cabin",
        "city": "Mendoza",
        "property_type": "Cabin",
        "bedrooms": 2,
        "max_guests": 4,
        "active_from": "2024-05-01",
        "acquisition_channel": "Referral",
        "base_nightly_rate_usd": 84,
    },
    {
        "property_id": "P010",
        "property_name": "Bariloche Lake View",
        "city": "Bariloche",
        "property_type": "Apartment",
        "bedrooms": 2,
        "max_guests": 5,
        "active_from": "2024-01-01",
        "acquisition_channel": "Partner",
        "base_nightly_rate_usd": 126,
    },
    {
        "property_id": "P011",
        "property_name": "Patagonia Cabin",
        "city": "Bariloche",
        "property_type": "Cabin",
        "bedrooms": 2,
        "max_guests": 5,
        "active_from": "2024-01-01",
        "acquisition_channel": "Organic",
        "base_nightly_rate_usd": 111,
    },
    {
        "property_id": "P012",
        "property_name": "Cerro Catedral Base",
        "city": "Bariloche",
        "property_type": "Apartment",
        "bedrooms": 1,
        "max_guests": 4,
        "active_from": "2024-06-01",
        "acquisition_channel": "Referral",
        "base_nightly_rate_usd": 98,
    },
]

CHANNELS = ["Airbnb", "Booking.com", "Direct", "Expedia"]
CHANNEL_WEIGHTS = [0.34, 0.36, 0.22, 0.08]
GUEST_COUNTRIES = ["Argentina", "Brazil", "Chile", "Uruguay", "United States", "Spain"]
GUEST_WEIGHTS = [0.49, 0.18, 0.12, 0.08, 0.07, 0.06]


def month_sequence() -> list[date]:
    months = []
    year, month = START_MONTH.year, START_MONTH.month
    for _ in range(MONTH_COUNT):
        months.append(date(year, month, 1))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def season_multiplier(city: str, month: int) -> float:
    if city == "Bariloche":
        return 1.42 if month in {6, 7, 8} else 1.18 if month in {1, 2, 12} else 0.91
    if city == "Mendoza":
        return 1.28 if month in {2, 3, 4} else 1.10 if month in {9, 10, 11} else 0.94
    if city == "Córdoba":
        return 1.20 if month in {1, 2, 7} else 1.02
    return 1.18 if month in {3, 4, 10, 11} else 1.04


def demand_weight(city: str, month: int) -> float:
    return min(1.0, season_multiplier(city, month) / 1.35)


def generate_bookings() -> list[dict]:
    rng = random.Random(RANDOM_SEED)
    bookings: list[dict] = []
    occupied_dates: dict[str, set[date]] = {p["property_id"]: set() for p in PROPERTIES}
    booking_number = 1

    for property_row in PROPERTIES:
        active_from = date.fromisoformat(property_row["active_from"])
        for month_start in month_sequence():
            if month_start < active_from:
                continue

            demand = demand_weight(property_row["city"], month_start.month)
            attempts = rng.choices(
                [0, 1, 2, 3, 4],
                weights=[0.04, 0.17, 0.33, 0.31 * demand, 0.15 * demand],
                k=1,
            )[0]
            days_in_month = calendar.monthrange(month_start.year, month_start.month)[1]

            for _ in range(attempts):
                cancelled = rng.random() < 0.105
                nights = rng.randint(2, 8)
                check_in = None

                for _candidate in range(25):
                    start_day = rng.randint(1, max(1, days_in_month - 1))
                    candidate = date(month_start.year, month_start.month, start_day)
                    candidate_dates = {candidate + timedelta(days=offset) for offset in range(nights)}
                    if candidate + timedelta(days=nights) > DATA_END_EXCLUSIVE:
                        continue
                    if cancelled or not (candidate_dates & occupied_dates[property_row["property_id"]]):
                        check_in = candidate
                        if not cancelled:
                            occupied_dates[property_row["property_id"]].update(candidate_dates)
                        break

                if check_in is None:
                    continue

                check_out = check_in + timedelta(days=nights)
                lead_time = rng.randint(3, 95)
                booked_at = check_in - timedelta(days=lead_time)
                rate = property_row["base_nightly_rate_usd"] * season_multiplier(
                    property_row["city"], check_in.month
                )
                rate *= rng.uniform(0.88, 1.14)

                bookings.append(
                    {
                        "booking_id": f"B{booking_number:04d}",
                        "property_id": property_row["property_id"],
                        "booked_at": booked_at.isoformat(),
                        "check_in": check_in.isoformat(),
                        "check_out": check_out.isoformat(),
                        "nightly_rate_usd": round(rate, 2),
                        "cleaning_fee_usd": round(18 + property_row["bedrooms"] * 7.5, 2),
                        "channel": rng.choices(CHANNELS, CHANNEL_WEIGHTS, k=1)[0],
                        "status": "cancelled" if cancelled else "completed",
                        "guest_country": rng.choices(GUEST_COUNTRIES, GUEST_WEIGHTS, k=1)[0],
                        "rating": "" if cancelled else round(rng.uniform(4.0, 5.0), 1),
                    }
                )
                booking_number += 1

    return bookings


def write_csv(path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_directories()
    bookings = generate_bookings()
    write_csv(RAW_DATA_DIR / "properties.csv", PROPERTIES)
    write_csv(RAW_DATA_DIR / "bookings.csv", bookings)
    print(f"Generated {len(PROPERTIES)} properties and {len(bookings)} synthetic bookings.")


if __name__ == "__main__":
    main()
