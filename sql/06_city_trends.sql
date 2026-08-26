WITH RECURSIVE
months(month_start) AS (
    VALUES('2024-01-01')
    UNION ALL
    SELECT date(month_start, '+1 month')
    FROM months
    WHERE month_start < '2025-12-01'
),
cities AS (
    SELECT DISTINCT city FROM properties
),
monthly_city_revenue AS (
    SELECT
        date(b.check_in, 'start of month') AS month_start,
        p.city,
        SUM(
            CASE WHEN b.status = 'completed'
                THEN (julianday(b.check_out) - julianday(b.check_in)) * b.nightly_rate_usd
                     + b.cleaning_fee_usd
                ELSE 0
            END
        ) AS gross_booking_value_usd,
        SUM(CASE WHEN b.status = 'completed' THEN 1 ELSE 0 END) AS completed_bookings
    FROM bookings AS b
    JOIN properties AS p ON p.property_id = b.property_id
    GROUP BY date(b.check_in, 'start of month'), p.city
),
city_month_grid AS (
    SELECT
        m.month_start,
        c.city,
        COALESCE(r.gross_booking_value_usd, 0) AS gross_booking_value_usd,
        COALESCE(r.completed_bookings, 0) AS completed_bookings
    FROM months AS m
    CROSS JOIN cities AS c
    LEFT JOIN monthly_city_revenue AS r
      ON r.month_start = m.month_start
     AND r.city = c.city
),
with_prior_year AS (
    SELECT
        *,
        LAG(gross_booking_value_usd, 12) OVER (
            PARTITION BY city ORDER BY month_start
        ) AS prior_year_revenue_usd
    FROM city_month_grid
)
SELECT
    strftime('%Y-%m', month_start) AS month,
    city,
    ROUND(gross_booking_value_usd, 2) AS gross_booking_value_usd,
    completed_bookings,
    ROUND(prior_year_revenue_usd, 2) AS prior_year_revenue_usd,
    ROUND(
        100.0 * (gross_booking_value_usd - prior_year_revenue_usd)
        / NULLIF(prior_year_revenue_usd, 0),
        2
    ) AS yoy_revenue_growth_pct
FROM with_prior_year
ORDER BY month_start, city;
