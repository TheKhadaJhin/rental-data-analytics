WITH RECURSIVE
months(month_start) AS (
    VALUES('2024-01-01')
    UNION ALL
    SELECT date(month_start, '+1 month')
    FROM months
    WHERE month_start < '2025-12-01'
),
availability AS (
    SELECT
        m.month_start,
        COUNT(p.property_id) AS active_properties,
        SUM(
            CAST(
                julianday(date(m.month_start, '+1 month'))
                - julianday(MAX(date(m.month_start), date(p.active_from)))
                AS INTEGER
            )
        ) AS available_nights
    FROM months AS m
    LEFT JOIN properties AS p
      ON date(p.active_from) < date(m.month_start, '+1 month')
    GROUP BY m.month_start
),
booking_nights AS (
    SELECT
        booking_id,
        property_id,
        date(check_in) AS stay_date,
        date(check_out) AS check_out,
        nightly_rate_usd
    FROM bookings
    WHERE status = 'completed'

    UNION ALL

    SELECT
        booking_id,
        property_id,
        date(stay_date, '+1 day'),
        check_out,
        nightly_rate_usd
    FROM booking_nights
    WHERE date(stay_date, '+1 day') < date(check_out)
),
night_metrics AS (
    SELECT
        date(stay_date, 'start of month') AS month_start,
        COUNT(*) AS booked_nights,
        SUM(nightly_rate_usd) AS lodging_revenue_usd
    FROM booking_nights
    GROUP BY date(stay_date, 'start of month')
),
cleaning_metrics AS (
    SELECT
        date(check_in, 'start of month') AS month_start,
        SUM(cleaning_fee_usd) AS cleaning_revenue_usd
    FROM bookings
    WHERE status = 'completed'
    GROUP BY date(check_in, 'start of month')
),
booking_metrics AS (
    SELECT
        date(check_in, 'start of month') AS month_start,
        COUNT(*) AS total_bookings,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_bookings,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
        AVG(julianday(check_in) - julianday(booked_at)) AS avg_lead_time_days,
        AVG(
            CASE WHEN status = 'completed'
                THEN julianday(check_out) - julianday(check_in)
            END
        ) AS avg_length_of_stay
    FROM bookings
    GROUP BY date(check_in, 'start of month')
)
SELECT
    strftime('%Y-%m', m.month_start) AS month,
    COALESCE(a.active_properties, 0) AS active_properties,
    COALESCE(a.available_nights, 0) AS available_nights,
    COALESCE(n.booked_nights, 0) AS booked_nights,
    ROUND(
        100.0 * COALESCE(n.booked_nights, 0) / NULLIF(a.available_nights, 0),
        2
    ) AS occupancy_pct,
    ROUND(COALESCE(n.lodging_revenue_usd, 0), 2) AS lodging_revenue_usd,
    ROUND(COALESCE(c.cleaning_revenue_usd, 0), 2) AS cleaning_revenue_usd,
    ROUND(
        COALESCE(n.lodging_revenue_usd, 0) + COALESCE(c.cleaning_revenue_usd, 0),
        2
    ) AS gross_booking_value_usd,
    ROUND(
        COALESCE(n.lodging_revenue_usd, 0) / NULLIF(n.booked_nights, 0),
        2
    ) AS adr_usd,
    ROUND(
        COALESCE(n.lodging_revenue_usd, 0) / NULLIF(a.available_nights, 0),
        2
    ) AS revpar_usd,
    COALESCE(b.completed_bookings, 0) AS completed_bookings,
    COALESCE(b.cancelled_bookings, 0) AS cancelled_bookings,
    ROUND(
        100.0 * COALESCE(b.cancelled_bookings, 0) / NULLIF(b.total_bookings, 0),
        2
    ) AS cancellation_rate_pct,
    ROUND(COALESCE(b.avg_lead_time_days, 0), 1) AS avg_lead_time_days,
    ROUND(COALESCE(b.avg_length_of_stay, 0), 1) AS avg_length_of_stay
FROM months AS m
LEFT JOIN availability AS a ON a.month_start = m.month_start
LEFT JOIN night_metrics AS n ON n.month_start = m.month_start
LEFT JOIN cleaning_metrics AS c ON c.month_start = m.month_start
LEFT JOIN booking_metrics AS b ON b.month_start = m.month_start
ORDER BY m.month_start;
