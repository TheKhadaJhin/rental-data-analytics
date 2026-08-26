# Data Dictionary

All fields in this project are synthetic.

## `properties`

| Field | Type | Description |
|---|---|---|
| `property_id` | text | Stable synthetic property identifier |
| `property_name` | text | Fictional public-facing property name |
| `city` | text | Argentine destination city |
| `property_type` | text | Studio, apartment, loft, house, or cabin |
| `bedrooms` | integer | Bedroom count |
| `max_guests` | integer | Maximum guest capacity |
| `active_from` | date | First date available in the portfolio |
| `acquisition_channel` | text | Fictional portfolio acquisition source |
| `base_nightly_rate_usd` | decimal | Starting rate used by the generator |

## `bookings`

| Field | Type | Description |
|---|---|---|
| `booking_id` | text | Stable synthetic booking identifier |
| `property_id` | text | Foreign key to `properties` |
| `booked_at` | date | Date the booking was created |
| `check_in` | date | Inclusive arrival date |
| `check_out` | date | Exclusive departure date |
| `nightly_rate_usd` | decimal | Nightly lodging rate in USD |
| `cleaning_fee_usd` | decimal | One-time cleaning fee in USD |
| `channel` | text | Airbnb, Booking.com, Direct, or Expedia |
| `status` | text | `completed` or `cancelled` |
| `guest_country` | text | Synthetic guest country, used only for aggregate analysis |
| `rating` | decimal | Rating from 1 to 5 for completed stays; null when cancelled |

## Derived metrics

| Metric | Definition |
|---|---|
| Available nights | Calendar nights after a property becomes active |
| Booked nights | Completed-stay nights; checkout date excluded |
| Occupancy | Booked nights / available nights |
| ADR | Lodging revenue / booked nights |
| RevPAR | Lodging revenue / available nights |
| Gross booking value | Lodging revenue + cleaning fees for completed stays |
| Lead time | Days between booking creation and check-in |
| Length of stay | Nights between check-in and checkout |
| Cancellation rate | Cancelled bookings / total bookings |
