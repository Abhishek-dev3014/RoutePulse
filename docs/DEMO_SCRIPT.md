# A 3–5 minute RoutePulse demonstration

**0:00–0:40 · Observe.** Open Overview, select Normal Campus Operations. Explain that the campus is fictional but the calculations are real. Inspect the three route loops, an active shuttle and its stop predictions. Drag the time slider to demonstrate continuous edge-following GPS. The entire map works offline.

**0:40–1:15 · Detect.** Switch to Morning Rush Hour. Highlight completed journeys, average queue wait, unserved demand and missed connections. Open Demand intelligence and point to forecast/seats ratios. Clarify that a queue warning is capacity pressure, not an overfilled bus: the physical capacity-violation metric remains zero.

**1:15–2:15 · Optimize and validate.** Open Optimization Studio and run Service first. Explain the two decisions: shift departures within published windows and reassign existing vehicles. Show the changed duties and all ten constraint categories. Note that the optimizer only uses planning seed 809; it never selects candidates using the displayed held-out day's outcomes.

**2:15–2:55 · Compare.** Show the baseline/candidate charts and full metric table. Use the current values, not a memorized improvement percentage. In the documented rush experiment, completed journeys increase from 706 to 849 and mean queue wait changes from 35.304 to 28.062 minutes. Check the seed and scenario before quoting these values. A different search budget, objective, machine or CPU load can choose another feasible candidate. The final production evidence is in data/experiments/20261014T091653Z.

**2:55–3:35 · Stress and recover.** Select Vehicle Breakdown, inspect cancelled duties, then run recovery optimization. Show the existing spare fleet being used and zero feasibility violations in the recommendation. In the saved breakdown experiment, 602→739 passengers complete, while missed connections increase 3→12: make the trade-off explicit rather than hiding it.

**3:35–4:15 · Decide and report.** Accept a feasible plan, return to Overview and point out “Accepted plan in operation.” Open Analytics & reports. Show empirical ETA coverage versus its 80% target; download JSON for reproducibility and CSV for comparison. Use Print report to generate a PDF.

**Close.** Universities and private campuses can use the same observe → predict → detect → optimize → validate workflow. A field deployment needs fleet/GPS integration, calibrated real history, authentication and dispatch governance. This MVP demonstrates the planning/evaluation core rather than claiming those integrations already exist.

## New two-minute path

Click **2-minute demo** in the top bar. The guide moves through four stages without accepting a plan or deleting any saved work:

- **0:00–0:20:** current operational situation and the fictional-campus disclosure.
- **0:20–1:00:** Studio, run optimization, show feasibility and calculated comparison.
- **1:00–1:40:** Evidence lab, test the current proposal on 20 days or open its persisted validation; show both wins and regressions.
- **1:40–2:00:** Reports, measured ETA quality, reproducibility, and the proposed campus pilot.

Prepare a saved validation before presenting if time is tight. The protocol never reoptimizes on its evaluation seeds. Different proposals have different results; quote the currently selected proposal, not the best headline from another run. See [HACKATHON_STRATEGY.md](HACKATHON_STRATEGY.md) for sources and rationale.
