WITH property_metrics AS (
    SELECT
        p.property_id,
        p.property_name,
        p.city,
        p.property_type,
        CAST(julianday('2026-01-01') - julianday(p.active_from) AS INTEGER) AS available_nights,
        SUM(
            CASE WHEN b.status = 'completed'
                THEN CAST(julianday(b.check_out) - julianday(b.check_in) AS INTEGER)
                ELSE 0
            END
        ) AS booked_nights,
        SUM(
            CASE WHEN b.status = 'completed'
                THEN (julianday(b.check_out) - julianday(b.check_in)) * b.nightly_rate_usd
                     + b.cleaning_fee_usd
                ELSE 0
            END
        ) AS gross_booking_value_usd,
        SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) AS completed_bookings,
        SUM(CASE WHEN b.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
        COUNT(b.booking_id) AS total_bookings,
        AVG(CASE WHEN b.status = 'completed' THEN b.rating END) AS avg_rating
    FROM properties AS p
    LEFT JOIN bookings AS b ON b.property_id = p.property_id
    GROUP BY
        p.property_id,
        p.property_name,
        p.city,
        p.property_type,
        p.active_from
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (
            PARTITION BY city
            ORDER BY gross_booking_value_usd DESC
        ) AS revenue_rank_in_city
    FROM property_metrics
)
SELECT
    property_id,
    property_name,
    city,
    property_type,
    available_nights,
    booked_nights,
    ROUND(100.0 * booked_nights / NULLIF(available_nights, 0), 2) AS occupancy_pct,
    ROUND(gross_booking_value_usd, 2) AS gross_booking_value_usd,
    ROUND(
        gross_booking_value_usd / NULLIF(booked_nights, 0),
        2
    ) AS gross_adr_usd,
    completed_bookings,
    cancelled_bookings,
    ROUND(100.0 * cancelled_bookings / NULLIF(total_bookings, 0), 2) AS cancellation_rate_pct,
    ROUND(avg_rating, 2) AS avg_rating,
    revenue_rank_in_city
FROM ranked
ORDER BY gross_booking_value_usd DESC;
