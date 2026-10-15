# Verification record

Final production-container experiment source: `data/experiments/20261014T091653Z/summary.json`. Original native runs are retained in their earlier timestamped directories. No results were overwritten.

## Measured operational results

| Scenario | Completed baseline → candidate | Mean wait (minutes) | Unserved | Missed connections | Candidate feasibility / capacity violations |
|---|---:|---:|---:|---:|---:|
| normal | 514 → 593 | 18.891 → 13.157 | 98 → 19 | 13 → 11 | 0 / 0 |
| rush | 706 → 849 | 35.304 → 28.062 | 460 → 317 | 10 → 7 | 0 / 0 |
| breakdown | 602 → 739 | 32.058 → 20.941 | 279 → 142 | 3 → 12 | 0 / 0 |
| traffic | 617 → 689 | 24.596 → 19.980 | 179 → 107 | 36 → 18 | 0 / 0 |
| event | 669 → 780 | 35.117 → 30.260 | 477 → 366 | 8 → 8 | 0 / 0 |

Breakdown recovery completes more journeys but increases missed connections. Traffic recovery increases total terminal delay. Full JSON retains those trade-offs. Wall-clock-bounded CP-SAT can select a different feasible incumbent on another machine or under different CPU load; the simulator reproduces a saved plan exactly.

## Prediction evidence

| Scenario | ETA MAE (minutes) | Measured interval coverage | Demand MAE (riders/bin) |
|---|---:|---:|---:|
| normal | 0.384 | 77.05% | 1.727 |
| rush | 0.383 | 81.32% | 2.611 |
| breakdown | 0.392 | 78.98% | 2.511 |
| traffic | 0.462 | 75.94% | 1.845 |
| event | 0.34 | 86.49% | 3.271 |

ETA estimator v1.1 learns normalized segment priors from seeds 151–154, calibrates residual intervals on 201–204, and evaluates on scenario seeds 4101–4105. The interval target is 80%; empirical coverage is reported without claiming that target is guaranteed.

## Actual verification

- Backend: **36 tests passed**, **97% statement coverage** (1,212 statements, 40 missed). Includes domain, simulation, constraints, ETA, demand, optimizer, API, persistence and plan decisions.
- Frontend: **4 unit tests passed**; strict TypeScript and ESLint passed.
- Production browser: **4 Playwright workflows passed in 46.1 seconds** against Docker + PostgreSQL. Covers scenario changes, optimization, acceptance, CSV export, fleet/demand/disruption navigation, mobile viewport, API failure/retry state, guided demo, validation persistence and daily CSV export.
- Ruff lint passed. Native and Docker Next.js production builds passed.
- Dependency audit after replacing the vulnerable lint dependency chain: **0 npm vulnerabilities**.
- Docker Compose: PostgreSQL, API and frontend all started successfully and reported healthy. API health returned `database: postgresql`; frontend returned HTTP 200.
- PostgreSQL: Alembic migration, idempotent seed, saved optimization and active plan were verified. A database restart preserved the experiment and accepted decision. The temporary verification database was removed afterward.
- Reproducibility: all **13 baseline and 13 candidate metrics** from the final saved rush experiment replayed exactly using its stored passenger snapshot.
- All five scenario experiments were persisted into the production report history and copied into this workspace.
- Desktop and 390px mobile screenshots were visually inspected. The narrow-screen recommendation banner was fixed; final dashboard and report images are in `docs/screenshots`.
- A GitHub Actions workflow is provided; no remote CI execution is claimed.

Non-blocking tool notices: the current Starlette TestClient emits an httpx deprecation notice; Vitest emits a future config-loader notice. All executed tests passed.

## Deliberate scope limits

No live dispatch/GPS integration, authentication, passenger portal, deep learning, added trips/routes or billing. Known outages cancel affected duties rather than evacuating vehicles mid-road. Bounded search does not prove global optimality. This is a synthetic, single-campus local demo; commercial production would require authentication, real calibration and fleet integration.

## Evidence upgrade verification

`robustness.py` has 100% statement coverage in the executed suite. Paired identity tests verify identical plans produce exactly zero deltas; tests verify seed exclusion, unchanged optimizer inputs, invalid candidate rejection, persistence and CSV exports. A CLI regression test verifies JSON serialization replay. All five saved proposals were validated on twenty prespecified days each and all five validation artifacts replayed exactly. See [ROBUSTNESS.md](ROBUSTNESS.md) for results, including transfer regressions.

The production Evidence lab was inspected at 1440px desktop and 390px mobile widths. Browser page errors: zero; mobile document overflow: false. Screenshots are in `docs/screenshots/evidence-lab.png` and `docs/screenshots/evidence-mobile.png`. Validation reports for all five original saved scenarios are persisted in the local PostgreSQL application.

## WILD BUGS packaging pass

The application suite was rerun during submission preparation: 36 backend tests, four frontend tests and four browser workflows passed; TypeScript, ESLint and Ruff passed. Browser workflow duration was 48.2 seconds. Recording and packaging scripts are separate from the operational app. The recorder exercises real API calls, preserves its source optimization/validation and checks for browser page errors. The package builder validates CRC plus every manifest hash and excludes local databases and environment files.
