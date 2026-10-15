# Data model and units

All identities are stable strings. Stored timestamps use UTC ISO-8601 / timezone-aware datetimes. Operational time is float minutes from the scenario's UTC epoch. The display converts this to 08:00–10:00 IST. Distances are kilometers, speeds kilometers/hour, occupancy integer people and service rates percentages from 0 to 100.

| Entity | Contents / relationship |
|---|---|
| Stop | ID, name, synthetic lat/lon, map x/y, type and wheelchair accessibility |
| Route | Ordered stop IDs, color, clockwise direction, operating window, minimum duty count; geometry follows consecutive graph edges |
| Edge | Directed origin/destination, distance, expected minutes, speed assumption and congestion factor |
| Vehicle | ID, fleet number, positive capacity, status, availability bounds and depot stop |
| Trip | ID, route, vehicle, selected departure and immutable earliest/latest departure bounds |
| Plan | Named collection of trip assignments; published baseline never changes during optimization |
| Passenger | Unique individual, arrival minute, origin, final destination and one or two ordered legs |
| Leg | Route, boarding origin and alighting destination; second leg includes a two-minute walk |
| Scenario | ID/version/seed, epoch/timezone, horizon, demand factor and typed disruption parameters |
| GPS | Vehicle/trip, timestamp, lat/lon, instantaneous observed speed and quality |
| Simulation | Full plan, seed/version, chronological stop events, operational events, GPS, passenger outcomes, metrics and feasibility |
| Optimization | Input snapshot, objective, planning/evaluation seeds, bounded search history, chosen plan, baseline/candidate evaluation, explanation and trade-offs |
| Decision | Immutable accepted/rejected action referencing an optimization, scenario and UTC timestamp |

Demand counts are represented as individual passengers rather than fractional groups, allowing exact capacity enforcement and FIFO outcomes. OD legs distinguish transfers from direct travel.

Three database tables store entity documents, runs and decisions. Indexes support kind/scenario/history reads; the migration also establishes the decision-to-run foreign key. A UUID identifies every saved run. Seeding only adds missing entities. Reset only replaces entities; historical runs keep their own complete snapshots.

Five scenarios use evaluation seeds 4101–4105. Forecast history uses seeds 110–121; optimization planning uses 809; ETA prior training uses 151–154 and residual calibration uses 201–204. Exogenous travel randomness is keyed by seed, directed edge and 10-minute clock bucket, so plan edits cannot change random draw order.
