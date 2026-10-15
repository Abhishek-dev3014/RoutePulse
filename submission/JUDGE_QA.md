# Judge questions: concise, evidence-backed answers

**What does the system actually decide?**
It moves published departures within their allowed windows and assigns existing vehicles. It preserves the published trips and route identities. CP-SAT solves assignments for candidate timetables; simulation evaluates passenger outcomes.

**Is this just a vehicle tracker?**
The map is one input view. Demonstrate the proposed duty changes, feasibility checks, before/after comparison and operator decision trail to show the planning workflow.

**How do you prevent cheating in the comparison?**
Candidate selection uses planning seed 809. The original evaluation uses a separate scenario seed. Both plans see the same generated passenger list and keyed traffic field. The twenty-day suite evaluates a frozen plan and never calls optimization.

**Do all passengers benefit?**
No. The service-first objective can worsen connections or individual stops. The Evidence lab exposes these changes. Use the selected run's actual transfer-regression count; don't claim universal improvement.

**Is the plan globally optimal?**
No. The search is bounded. A solver subproblem's optimal status does not prove global optimality of the whole transport system.

**Is the data real?**
No. The campus and operational data are synthetic. PS 02 allows synthetic inputs. The packaged data is locally generated; it has not been confirmed as the organizer's common dataset.

**What is the commercial proposition?**
An operator planning workflow for campuses and institutional fleets. A one-campus shadow pilot would test usability, data integration and actual value. No customers, price validation or savings claims exist yet.

**What can I reproduce?**
Start Docker Compose, run a scenario, export JSON, and replay the saved evaluation with the provided scripts. The package contains the exact JSON for the recorded demonstration plus the original five-scenario suite.

**What is missing for deployment?**
Real history calibration, full operator/driver rules, authentication, fleet/GPS integration and dispatch governance. Known outages currently cancel affected duties; roadside evacuation is not modeled.

**How was it built?**
With substantial AI coding assistance and the libraries listed in the lockfiles. Use the disclosure document and the team's actual build timeline; do not invent a different provenance.
