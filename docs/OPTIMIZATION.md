# Optimization and feasibility

## Search decisions

A bounded deterministic enumeration tries route-level departure offsets of −4, −2, 0, +2 or +4 minutes and selected combinations. Every departure remains within its published ±4-minute window. Headways within a route are preserved. For each fixed timetable, OR-Tools CP-SAT assigns one of seven existing vehicles to each of 21 duties.

Binary `x[trip,vehicle]` variables require exactly one vehicle per trip. Unavailable vehicle/time combinations are forbidden. For every pair of duties whose completion + turnaround + directed relocation exceeds the next start, the same vehicle cannot be assigned to both. Depot reachability and availability windows are checked. CP-SAT maximizes estimated useful seats near a duty, with a small penalty for reassignments and a deterministic vehicle-index tie-breaker. It uses one search worker and seed 23.

The assignment score is a heuristic subproblem, not the overall passenger objective. Each resulting plan passes the independent hard-constraint validator, then the event simulator evaluates it on independent planning passengers and travel seed 809. Only planning outcomes rank candidates.

## Objective ordering

All objectives are lexicographic, always minimizing unserved passengers first:

- **Service:** `(unserved people, missed connections, average queue minutes across all people, operating minutes + 0.1 × changed duties)`.
- **Wait:** `(unserved people, average queue minutes across all people, missed connections, operating minutes + 0.1 × changed duties)`.
- **Balanced:** service ordering with `operating minutes + 2 × changed duties` in the last position.

The final score term expresses an explicit cost preference rather than money. Service-first ordering prevents reductions in average waiting caused by abandoning hard-to-serve passengers. A feasible published baseline must be strictly beaten on the planning score to yield a recommendation. If the disrupted baseline is infeasible, feasible recovery is prioritized.

## Hard constraints

The validator independently checks fleet inventory, availability, positive capacities, immutable departure windows, vehicle exclusivity, turnaround/deadhead continuity, operating-window travel feasibility, directed network validity, minimum service and unique trip IDs. Published duties cannot be removed or have their route changed. Actual physical capacity is separately enforced at boarding and reported as a measured invariant.

## Timeouts and failure

Default search budget: 12 seconds, at most 24 requested candidates (the current enumerator contains 20 unique schedules). Each CP-SAT call receives at most 0.4 seconds. Requests cap the search budget at 30 seconds and candidate limit at 50. If time expires, the best fully validated incumbent can be returned with `TIME_LIMIT_FEASIBLE`. Without an incumbent, the API returns `TIME_LIMIT_NO_IMPROVEMENT` or `NO_FEASIBLE_IMPROVEMENT`. It never returns an infeasible partial solution as a recommendation. Final held-out simulation and serialization may add time beyond the search budget.

## Controlled evaluation and explanations

After candidate selection, both plans use exactly the same OD passenger list, fleet, network, evaluation seed, time horizon and disruption. Edge/time-bucket shocks are keyed independently of plan order. Every changed duty returns old/new vehicle, old/new departure and its verified window. The UI displays measured improvements and regressions, constraint checks, reserve consumption and schedule disruption trade-offs.

CP-SAT `OPTIMAL` means optimal only for a particular assignment subproblem at a fixed timetable. It is never a claim of global transport-plan optimality. The JSON report saves subproblem statuses, planning metrics and held-out metrics separately.

Search is wall-clock bounded, so another machine or CPU load can produce a different feasible incumbent even with the same solver seed. Saved-plan simulation replay is exact; reproducing an optimizer search is not a claim of machine-independent incumbent selection. Input snapshots retain the exact evaluation and planning passenger lists.
