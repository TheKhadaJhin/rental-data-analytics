PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS properties;

CREATE TABLE properties (
    property_id TEXT PRIMARY KEY,
    property_name TEXT NOT NULL,
    city TEXT NOT NULL,
    property_type TEXT NOT NULL,
    bedrooms INTEGER NOT NULL CHECK (bedrooms >= 0),
    max_guests INTEGER NOT NULL CHECK (max_guests > 0),
    active_from TEXT NOT NULL,
    acquisition_channel TEXT NOT NULL,
    base_nightly_rate_usd REAL NOT NULL CHECK (base_nightly_rate_usd > 0)
);

CREATE TABLE bookings (
    booking_id TEXT PRIMARY KEY,
    property_id TEXT NOT NULL,
    booked_at TEXT NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    nightly_rate_usd REAL NOT NULL CHECK (nightly_rate_usd > 0),
    cleaning_fee_usd REAL NOT NULL CHECK (cleaning_fee_usd >= 0),
    channel TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('completed', 'cancelled')),
    guest_country TEXT NOT NULL,
    rating REAL CHECK (rating BETWEEN 1 AND 5 OR rating IS NULL),
    FOREIGN KEY (property_id) REFERENCES properties(property_id),
    CHECK (date(check_out) > date(check_in)),
    CHECK (date(booked_at) <= date(check_in))
);

CREATE INDEX idx_bookings_property ON bookings(property_id);
CREATE INDEX idx_bookings_check_in ON bookings(check_in);
CREATE INDEX idx_bookings_channel ON bookings(channel);
CREATE INDEX idx_bookings_status ON bookings(status);

