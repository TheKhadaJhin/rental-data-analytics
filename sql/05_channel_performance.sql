WITH channel_metrics AS (
    SELECT
        channel,
        COUNT(*) AS total_bookings,
        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_bookings,
        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
        SUM(
            CASE WHEN status = 'completed'
                THEN CAST(julianday(check_out) - julianday(check_in) AS INTEGER)
                ELSE 0
            END
        ) AS booked_nights,
        SUM(
            CASE WHEN status = 'completed'
                THEN (julianday(check_out) - julianday(check_in)) * nightly_rate_usd
                     + cleaning_fee_usd
                ELSE 0
            END
        ) AS gross_booking_value_usd,
        AVG(julianday(check_in) - julianday(booked_at)) AS avg_lead_time_days
    FROM bookings
    GROUP BY channel
),
ranked AS (
    SELECT
        *,
        DENSE_RANK() OVER (ORDER BY gross_booking_value_usd DESC) AS revenue_rank,
        SUM(gross_booking_value_usd) OVER () AS portfolio_revenue_usd
    FROM channel_metrics
)
SELECT
    channel,
    total_bookings,
    completed_bookings,
    cancelled_bookings,
    booked_nights,
    ROUND(gross_booking_value_usd, 2) AS gross_booking_value_usd,
    ROUND(100.0 * gross_booking_value_usd / NULLIF(portfolio_revenue_usd, 0), 2) AS revenue_share_pct,
    ROUND(gross_booking_value_usd / NULLIF(booked_nights, 0), 2) AS gross_adr_usd,
    ROUND(100.0 * cancelled_bookings / NULLIF(total_bookings, 0), 2) AS cancellation_rate_pct,
    ROUND(avg_lead_time_days, 1) AS avg_lead_time_days,
    revenue_rank
FROM ranked
ORDER BY revenue_rank, channel;
