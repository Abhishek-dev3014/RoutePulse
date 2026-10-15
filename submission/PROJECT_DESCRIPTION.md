# RoutePulse — campus transport decisions with inspectable evidence

Target: WILD BUGS, PS 02.

## One-line description

RoutePulse helps campus transport operators test feasible timetable and vehicle-assignment changes, then inspect their impact on passenger journeys, waiting and connections.

## Problem and intended users

Campus operators must work with limited vehicles, departure windows and changing demand. A location map can show where a bus is; deciding which duties to change also requires demand estimates, capacity checks and a comparison of passenger outcomes. RoutePulse's intended daily user is a transport supervisor or dispatcher. Students and staff are the intended beneficiaries. The problem statement is a working hypothesis pending campus interviews; no field survey is claimed.

## What the prototype does

The application models a fictional campus with 13 stops, three directed routes, seven vehicles and 21 published duties. It simulates individual passenger arrivals, FIFO boarding, capacity limits, transfers, traffic and known outages. GPS traces feed an ETA estimator evaluated against simulation ground truth. Historical synthetic demand drives forecasts and a bounded search using OR-Tools CP-SAT for vehicle assignment.

An operator can compare a proposal with the published timetable using identical passengers and exogenous traffic conditions, inspect feasibility and trade-offs, accept or reject it, and export its complete evidence. Acceptance changes the monitored plan in the demo, not a real fleet.

The Evidence lab freezes a saved proposal and tests twenty prespecified synthetic days. It reports mean changes, bootstrap intervals, individual daily outcomes and passenger-origin impact, including regressions. Evaluation results are kept separate from the optimization's planning seed.

## Measured result and its limit

The original saved rush-hour proposal completed 849 journeys versus 706 on its original evaluation day. In its twenty-day follow-up evaluation it averaged 149.8 additional completed journeys and 7.38 minutes less mean waiting. Completed journeys improved on all twenty days; missed transfers worsened on thirteen days. Candidate capacity and feasibility violations were zero in that suite.

These numbers refer to `data/experiments/20261014T091653Z/rush.json` and `rush-validation-v1.json`. The walkthrough may generate another proposal; its own JSON accompanies the video and governs any numbers shown there. These are simulator results, not observed improvements at a university.

## Technical contribution

The central contribution is an end-to-end, reproducible decision workflow: demand and ETA estimation, discrete-event simulation, constrained optimization, paired evaluation and an operator decision trail. The assignment solver is bounded by a route-level timetable search; the overall transport plan is not proven globally optimal. The system makes aggregate and stop-level trade-offs inspectable rather than treating every suggested change as beneficial.

## Built with

Next.js, React, TypeScript, TanStack Query, Recharts and Lucide; FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL and OR-Tools. Docker Compose runs the local stack; SQLite is supported for native development. The offline SVG map follows the graph without a map-provider dependency.

## Validation and reproduction

The executed suite contains 36 backend tests, four frontend unit tests and four browser workflows, with 97% backend statement coverage in the last measured coverage run. Five saved scenarios have twenty-day follow-up reports. JSON snapshots, seeds, passenger hashes and replay commands accompany the results. Start the app with `docker compose up --build`; detailed setup is in the root README.

## Challenges and next step

The service-first objective improves total completion while sometimes worsening transfers. Real deployment also requires real data calibration, driver and labor constraints, integration, authentication and dispatch governance. The proposed next step is a single-campus shadow pilot: interview operators and riders, calibrate on earlier history, evaluate later history, and agree on acceptable stop-level and transfer trade-offs before any supervised operational trial.

## Submission fields still requiring the entrant

The event and problem are WILD BUGS / PS 02. Team names, submission account, event-specific word limits, public source/video links, actual build timeline and any required AI-use statement still need the entrant's details. See EVENT_REQUIREMENTS.md for the official-source audit and unresolved conditions.
