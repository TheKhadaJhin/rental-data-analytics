-- Worked example of the allocation rules in ../03_monthly_kpis.sql.
-- Source: the committed synthetic booking B0002. This query only reads data.
WITH RECURSIVE
selected_booking AS (
    SELECT booking_id, check_in, check_out, nightly_rate_usd, cleaning_fee_usd
    FROM bookings
    WHERE booking_id = 'B0002' AND status = 'completed'
),
booking_nights AS (
    SELECT
        booking_id,
        date(check_in) AS stay_date,
        date(check_out) AS check_out,
        nightly_rate_usd
    FROM selected_booking

    UNION ALL

    SELECT
        booking_id,
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
    FROM selected_booking
    GROUP BY date(check_in, 'start of month')
)
SELECT
    strftime('%Y-%m', n.month_start) AS month,
    n.booked_nights,
    ROUND(n.lodging_revenue_usd, 2) AS lodging_revenue_usd,
    ROUND(COALESCE(c.cleaning_revenue_usd, 0), 2) AS cleaning_revenue_usd,
    ROUND(
        n.lodging_revenue_usd + COALESCE(c.cleaning_revenue_usd, 0),
        2
    ) AS gross_booking_value_usd
FROM night_metrics AS n
LEFT JOIN cleaning_metrics AS c ON c.month_start = n.month_start
ORDER BY n.month_start;
