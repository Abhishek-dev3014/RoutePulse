# Event simulation

`simulate(network, scenario, plan, passengers, seed)` is a pure callable with no database or web dependency. A priority heap orders events by timestamp, priority and insertion sequence. Passenger queue arrivals precede vehicle stop events at equal timestamps. Vehicle duties are generated in selected-departure order, and all stop events are then processed in chronological order.

## Vehicle movement

The directed graph supplies edge lengths and prior travel times (18 km/h baseline). Travel time multiplies the prior by known route congestion and a bounded lognormal edge/time-bucket shock. A hash-derived RNG makes each environmental draw independent of candidate enumeration and passenger boardings.

A vehicle's actual departure is the maximum of its chosen departure and its previous actual completion + 2-minute turnaround + shortest directed deadhead travel. Initial dispatch also respects depot travel. Invalid schedules therefore generate violations and delays, never simultaneously operating the same physical vehicle. A known breakdown prevents dispatch of any duty whose realized interval overlaps the outage. Unavailable/maintenance vehicles and duties that finish outside availability are cancelled. Breakdown and cancellation events are reported. This is advance-known loss of availability, not roadside evacuation.

GPS observations at half-minute spacing interpolate along each traversed network edge. Dwell observations remain stationary. The frontend replays these observations; it does not jump vehicles from one stop to the next. No map tile provider is required.

## Passenger processing

1. People join an origin/route queue at their demand arrival minute.
2. At a stop, passengers whose current leg ends there alight first.
3. Finishing their final leg marks them completed. Transfer passengers join their next queue after two minutes walking.
4. Waiting passengers are eligible only if the route serves their leg destination later in the ordered trip.
5. Eligible people board in ready-time / stable-ID FIFO order, up to `capacity - remaining onboard`.
6. Excess people remain queued. The stop event records boardings, alightings, physical occupancy and left-behind queue size.

At 10:00, any passenger not at their final destination is unserved, including onboard riders. Accumulated queue wait includes pending passengers through the cutoff. Riding and walking minutes are not counted as queue wait. Aggregate average wait includes every passenger, preventing the appearance of improvement by dropping unfinished riders.

## Transfers

When a first leg alights, its scheduled arrival plus two minutes defines the intended connection threshold. The first scheduled compatible onward duty at/after that time is the intended connection. A delayed but boarded intended duty is successful. An earlier alternative is not marked missed. Boarding a later duty, or remaining incomplete after finishing the first leg, counts as a missed connection. People who never complete the first leg are unserved but not also recorded as a missed transfer. A missed connection can ultimately complete, so missed connections and unserved people are not additive.

## Evaluation authority and limits

The simulator's outcomes are the sole source of comparison metrics. The planning simulator is run with seed 809; the evaluated day uses the scenario seed only after the proposed plan is fixed. Traffic is piecewise stationary in ten-minute buckets and dwell is fixed; congestion does not depend on vehicle flow. Passenger abandonment, wheelchair boarding time, driver breaks and mid-journey evacuation are outside this release.
