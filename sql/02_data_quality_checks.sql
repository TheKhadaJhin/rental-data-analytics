WITH overlap_issues AS (
    SELECT COUNT(*) AS issue_count
    FROM bookings AS first_booking
    JOIN bookings AS second_booking
      ON first_booking.property_id = second_booking.property_id
     AND first_booking.booking_id < second_booking.booking_id
     AND first_booking.status = 'completed'
     AND second_booking.status = 'completed'
     AND date(first_booking.check_in) < date(second_booking.check_out)
     AND date(second_booking.check_in) < date(first_booking.check_out)
),
checks AS (
    SELECT
        'duplicate_booking_ids' AS check_name,
        COUNT(*) - COUNT(DISTINCT booking_id) AS issue_count
    FROM bookings

    UNION ALL

    SELECT
        'orphan_property_references',
        COUNT(*)
    FROM bookings AS b
    LEFT JOIN properties AS p ON p.property_id = b.property_id
    WHERE p.property_id IS NULL

    UNION ALL

    SELECT
        'invalid_stay_dates',
        COUNT(*)
    FROM bookings
    WHERE date(check_out) <= date(check_in)

    UNION ALL

    SELECT
        'booking_created_after_check_in',
        COUNT(*)
    FROM bookings
    WHERE date(booked_at) > date(check_in)

    UNION ALL

    SELECT
        'invalid_prices',
        COUNT(*)
    FROM bookings
    WHERE nightly_rate_usd <= 0 OR cleaning_fee_usd < 0

    UNION ALL

    SELECT
        'invalid_ratings_by_status',
        COUNT(*)
    FROM bookings
    WHERE (status = 'completed' AND rating IS NULL)
       OR (status = 'cancelled' AND rating IS NOT NULL)

    UNION ALL

    SELECT
        'overlapping_completed_stays',
        issue_count
    FROM overlap_issues
)
SELECT check_name, issue_count
FROM checks
ORDER BY check_name;
