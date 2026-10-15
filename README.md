# RoutePulse

**Intelligent campus transport planning, with evidence behind every decision.**

RoutePulse is a functioning single-campus hackathon MVP for observing shuttle operations, forecasting arrivals and demand, finding feasible schedule changes, and evaluating those changes against a controlled baseline. All campus geography, demand and GPS are synthetic. All displayed operational metrics are computed.

## Competition demonstration and stronger evidence

Use **2-minute demo** in the app for a guided walkthrough. The new **Evidence lab** evaluates a frozen proposal on 20 different synthetic days, displays uncertainty and transfer regressions, and breaks down impact by passenger origin. Reports persist and can be exported or replayed exactly.

[Research and competition strategy](docs/HACKATHON_STRATEGY.md) · [100 paired scenario evaluations](docs/ROBUSTNESS.md) · [Proposed campus pilot](docs/PILOT_PLAN.md)

## WILD BUGS / PS 02 submission kit

[Watch/download the narrated demo (MP4)](submission/demo/routepulse-demo-narrated.mp4) · [Dashboard screenshot](docs/screenshots/dashboard.png) · [Recorded evaluation](submission/demo/recorded-validation.json)

The official problem document matches this project's mandatory capabilities and weighted rubric. Synthetic data is permitted; real campus integration is optional. The [event audit](submission/EVENT_REQUIREMENTS.md) records remaining organizer/account details.

Open [the submission kit](submission/README.md) for the recorded walkthrough, exact recorded experiment, project description, judge Q&A and build disclosure. `submission/index.html` is an offline review page. Build a verified source/evidence archive with `.venv/bin/python scripts/package_submission.py` after the demo artifacts are present.

## Run with Docker

Requirements: Docker Desktop / Engine with Compose, approximately 2 GB free RAM and network access for the first dependency download.

```bash
cp .env.example .env
docker compose up --build
```

Open **http://localhost:3000**. Interactive API documentation: **http://localhost:8000/docs**. PostgreSQL migrations and idempotent demo seeding run automatically. The database uses a named volume. Services bind to loopback; this is an explicitly unauthenticated single-organization demo.

```bash
docker compose ps
docker compose exec api alembic -c services/api/alembic.ini upgrade head
docker compose exec api python scripts/seed.py
docker compose exec api python scripts/reset_demo.py
docker compose down                    # preserves database volume
```

The reset command resets seeded entities, retaining experiment and decision history. It does not erase results.

## Native development (tested Python 3.13 / Node 24)

```bash
python3 -m venv .venv
.venv/bin/pip install -r services/api/requirements.lock
npm ci --prefix apps/web
./scripts/dev.sh
```

The native fallback uses durable SQLite in `routepulse.db` and the same SQLAlchemy models and Alembic migration. PostgreSQL is the default Docker deployment. To use another PostgreSQL instance, set `DATABASE_URL=postgresql+psycopg://user:password@host/database` before starting. Native frontend proxies `/api` to `API_INTERNAL_URL`, default `http://127.0.0.1:8000`. Environment examples are in `.env.example`; do not commit real credentials.

## The operator workflow

1. **Overview:** select Normal Campus Operations; inspect computed metrics, alerts and next-stop ETA intervals.
2. **Morning Rush Hour:** observe capacity pressure, waiting passengers and missed transfers. Replay GPS with the map slider; inspect stops and vehicles, or toggle routes.
3. **Optimization Studio:** choose an objective and run CP-SAT-assisted candidate search. Inspect changed duties, feasibility and held-out baseline comparison.
4. **Accept or reject:** decisions are saved as an audit trail. Acceptance makes the candidate the monitored plan for that exact scenario configuration. The next optimization still compares with the immutable published baseline.
5. **Disruption simulator:** change demand, traffic, route, vehicle outage and time bounds. Run the simulation, then find a recovery plan.
6. **Evidence lab:** choose a saved proposal, test on 20 new days, inspect gains and regressions, and export the paired evidence. This does not accept or modify a plan.
7. **Analytics & reports:** inspect ETA and demand errors, download complete experiments as JSON or comparisons as CSV, and print the report to PDF.

## What is implemented

- 13 stops, three directed circular routes, seven vehicles (22–45 seats), 21 published duties and a reserve vehicle.
- Five genuinely different scenarios: normal, rush, breakdown, traffic and event surge.
- Chronological passenger arrivals, FIFO queues, destination-compatible boarding, alighting before boarding, two-leg transfers and horizon-based outcomes.
- Continuous edge-interpolated GPS, route map matching, observed-speed/prior ETA estimates and independently calibrated prediction windows.
- Twelve-day historical demand forecasts at origin/route/15-minute resolution, pressure thresholds and held-out errors.
- Ten categories of hard-constraint checks; runtime delays prevent vehicles physically operating overlapping duties.
- Departure-window shifts and fleet reassignments using OR-Tools CP-SAT with a bounded search and explicit timeout/failure states.
- Separate planning and evaluation seeds; identical passenger and exogenous traffic fields for fair baseline/candidate comparison.
- Durable entities, immutable experiment input/output snapshots and audited plan decisions; JSON/CSV exports.
- Responsive dashboard, offline interactive SVG network, playback, fleet/timetable, demand heatmap, optimization, disruption and reporting views.

## Architecture and stack

Next.js App Router / strict TypeScript / React / TanStack Query / Zod / Recharts / Lucide → FastAPI / Pydantic → pure Python domain services → SQLAlchemy / Alembic → PostgreSQL (SQLite native fallback). OR-Tools handles the assignment subproblem. The deterministic simulator is directly callable without a server or database.

The interface uses purpose-built CSS and accessible native controls instead of introducing Tailwind/shadcn. An always-available SVG graph is used instead of a tile-dependent map; every movement follows a graph edge. See [architecture](docs/ARCHITECTURE.md), [domain model](docs/DATA_MODEL.md), [simulation](docs/SIMULATION.md), [optimization](docs/OPTIMIZATION.md), and [evaluation](docs/EVALUATION.md).

## Verification and reproducible experiments

```bash
.venv/bin/pytest -q --cov=app --cov-report=term-missing
.venv/bin/ruff check services/api scripts
npm run typecheck --prefix apps/web
npm run lint --prefix apps/web
npm test --prefix apps/web
npm run build --prefix apps/web

# With API and frontend running:
cd apps/web
npx playwright install chromium
npm run test:e2e
cd ../..

PYTHONPATH=services/api .venv/bin/python scripts/experiments.py
# Add --persist to populate the application report history.
```

On macOS an installed browser can be used without a download:
`CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' npm run test:e2e --prefix apps/web`.

Replay a saved run with `PYTHONPATH=services/api .venv/bin/python scripts/replay.py data/experiments/20261014T091653Z/rush.json`. Regenerate shared contracts with `PYTHONPATH=services/api .venv/bin/python scripts/generate_contract.py` and `apps/web/node_modules/.bin/openapi-typescript data/openapi.json -o apps/web/lib/generated.ts`.

Experiment generation creates a new UTC-timestamped directory, never overwrites an earlier run, and stores inputs, seeds, both plans, outcomes, candidate search history, ETA and demand evaluations. See [verification record](docs/VERIFICATION.md) for actually executed checks and [judging evidence](docs/JUDGING_EVIDENCE.md) for rubric mapping.

## Assumptions and limits

- UTC epoch: `2026-10-14T02:30:00Z`; display: Asia/Kolkata, 08:00–10:00. Trip operation may extend to 10:20, but service outcomes are censored at 10:00.
- Fixed 27-second dwell, 2-minute transfer walk and 2-minute turnaround. Demand arrivals stop at 09:40, allowing a completion tail.
- Known outages cancel duties that would overlap the outage; roadside evacuation and sudden mid-leg breakdown recovery are not modeled.
- No live hardware, paid maps, authentication, production dispatch integration or notifications. Accepting a plan changes the simulation workspace, not a real fleet.
- Historical data is generated, not collected. Synthetic forecast accuracy is not a field-performance claim. The ETA interval has an 80% target; actual coverage can differ.
- Bounded search does not establish global optimality. A plan selected on historical estimates can regress on the held-out realization; those regressions are reported.
- This release shifts departures and reassigns existing duties. It does not add routes/trips, optimize driver shifts, or support passenger route redesign.
- No guarantee that infeasible disrupted schedules can always be recovered with seven vehicles. Failed searches retain explicit status.
- Frontend fonts optionally load from Google Fonts and fall back to system fonts offline. No core feature requires internet after installation.
- Production hosting requires authentication, organization-scoped authorization, a background worker queue, stronger traffic/dwell calibration and operational integration.

The architecture follows the documented [Next.js App Router installation](https://nextjs.org/docs/app/getting-started/installation) and [FastAPI request model](https://fastapi.tiangolo.com/tutorial/body/) patterns.

![Verified RoutePulse dashboard](docs/screenshots/dashboard.png)
