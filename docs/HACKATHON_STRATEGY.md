# RoutePulse: research and competition strategy

Research date: 14 October 2026. The user subsequently identified WILD BUGS. Its linked PS 02 is RoutePulse and confirms the same seven weighted criteria used here. See [the event-specific audit](../submission/EVENT_REQUIREMENTS.md). Confirm event eligibility, permitted pre-existing work and AI/tool disclosure before submission; this repository already existed before the current research.

## What the historical examples actually support

This is a qualitative comparison of selected official winner profiles, not a statistical model of winning. Public profiles omit judging scores, unsuccessful entries and selection factors. We cannot estimate a win probability or conclude that a feature caused a win. NASA's themed hackathon and Microsoft's student startup competition have different incentives.

| Official example | Observed feature | RoutePulse implication (our inference) |
|---|---|---|
| NASA Space Apps 2024: Waterwise, Best Use of Data | Supports farmers managing water availability | Make the operational decision and intended user explicit |
| NASA Space Apps 2024: G.R.O.W., Local Impact | Makes environmental GIS information accessible | Translate technical metrics into passenger outcomes |
| NASA Space Apps 2025: SkySense, Best Use of Technology | Personalized weather risk and activity windows | Connect predictions to an action an operator can take |
| NASA Space Apps 2025: PureFlow, Best Mission Concept | Models habitats and tests threats | Let judges challenge a plan rather than only inspect a dashboard |
| NASA Space Apps 2025: Gaia+LEO, Global Connection | Mixed-integer infrastructure optimization | Optimization can itself be a compelling technical contribution |
| Imagine Cup 2025: Argus, world champion | Assistive wearable inspired by family experience of low vision | Validate a specific human problem before claiming adoption |

Sources: [NASA 2024 winners](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/), [NASA 2025 winners](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/), [Microsoft's Argus profile](https://www.microsoft.com/en-us/startups/blog/could-your-startup-be-the-next-imagine-cup-world-champion/). A compact source index is in `data/research/winner_examples.csv`.

There is no universal rubric. [MLH's standard rules](https://github.com/MLH/mlh-policies/blob/main/standard-hackathon-rules.md) emphasize technology, design, completion and learning for their specified categories; they explicitly distinguish those from salesmanship and business merit. Its [organizer guide](https://guide.mlh.com/general-information/judging-and-submissions/judging-plan) recommends short demonstrations, including two-minute videos. Our guided walkthrough therefore exposes working behavior; the pilot plan supports the commercial criterion in this project's own brief rather than assuming every hackathon rewards a business pitch.

## Audit and changes implemented

| Gap in RoutePulse | Change | Original rubric supported |
|---|---|---|
| Useful functions spread over seven screens; a new judge must find the story | Four-step two-minute guide inside the running app | Explainability, engineering |
| One held-out day per scenario gives limited evidence of robustness | Freeze a saved candidate; evaluate 20 prespecified independent synthetic days with identical inputs within each pair | Improvement, robustness, reproducibility |
| Mean improvement hides possible harm | Expose transfer-regression days, every daily result, and pooled service/wait by passenger origin | Demand/capacity, explainability |
| Technical metrics need human interpretation | Original-day completed journeys, queue minutes, vehicle use and transfer changes displayed together | Operational improvement |
| Evidence was exportable but multi-day results did not exist | Persist and export validation JSON/CSV; exact replay CLI; snapshot and demand hashes | Engineering/reproducibility |
| No credible adoption path | Proposed campus shadow pilot with named users, required data and success criteria | Commercial relevance |

No chatbot, extra model, carbon claim, revenue projection or fictional customer has been added. These would require their own evidence and were not the main gaps identified in the current brief.

## Positioning and presentation

Opening: **“RoutePulse helps a campus transport operator test a better morning plan using the fleet already available.”**

Demonstrate the complete decision: observe demand → generate a proposal → validate constraints → compare outcomes → challenge on multiple days → operator decides. Explain that the optimization uses planning demand separately from evaluation. The differentiator to demonstrate is an inspectable decision with constraints, counterfactual results and visible trade-offs. Do not claim that no competing product has these capabilities; no exhaustive competitor study was performed.

Use the on-screen numbers for the selected proposal. The recorded rush plan gained 149.8 completed journeys per simulated morning across 20 new seeds, with service gains on all 20; transfer misses worsened on 13 days. These results justify further testing, not a deployment promise. See [ROBUSTNESS.md](ROBUSTNESS.md).

For future deployment, the most valuable evidence still missing is outside the simulator: an actual campus transport problem, permission to use historical operations data, and observed user feedback. The official PS 02 allows synthetic data and makes real campus integration optional, so this is not an unfulfilled MVP requirement. Follow [PILOT_PLAN.md](PILOT_PLAN.md). Do not invent interviews or silently re-label synthetic data as real.

## Submission preparation

1. Obtain the event's official rubric, duration, submission format and allowed prior-work rules; map each criterion to a visible result.
2. Rehearse the in-app two-minute guide. Keep a longer disruption demonstration ready for questions.
3. Prepare a short recording of the working app and include the source repository, setup command and limitations in the submission.
4. State what the team built, what libraries/tools were used and what predated the event, as required by that event.
5. Bring a reproducible saved report so the demonstration can be inspected without waiting for another optimization.

Winning depends on the event, competing entries and judges. This work strengthens demonstrable evidence and presentation; it cannot guarantee a rank.
