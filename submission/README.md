# WILD BUGS submission kit — RoutePulse / PS 02

Start with [EVENT_REQUIREMENTS.md](EVENT_REQUIREMENTS.md), then adapt [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md) for the entrant's submission form. [JUDGE_QA.md](JUDGE_QA.md) prepares the evidence-based answers; [DISCLOSURE.md](DISCLOSURE.md) records build/data limitations.

Open `index.html` in a browser for the portable video and evidence overview. The project description and disclosure remain editable drafts for the submission form.

## Contents

- `demo/routepulse-demo-narrated.mp4`: upload-ready H.264/AAC version, approximately 1 minute 55 seconds, with synchronized synthetic macOS Samantha narration and the original visible captions.
- `demo/narration-en.srt`: approximate sentence-timed speech subtitles for YouTube.
- `demo/narration-script.md` and `demo/narration.json`: spoken script and timing metadata.

- `demo/routepulse-demo.webm`: captioned recording of actual app interactions, approximately two minutes, with no audio.
- `demo/captions.vtt`: companion captions.
- `demo/recording.json`: capture metadata and caption timing.
- `demo/recorded-optimization.json` and `demo/recorded-validation.json`: exact computed evidence shown in the recording.
- `pilot/`: blank interview, data request and shadow measurement materials. These are future-work templates, not completed research.
- Root `README.md`, `docs/`, `data/experiments/20261014T091653Z/`, source and lockfiles: included in the archive for reproduction.

## Judge walkthrough

1. Extract the archive and follow the root README to start the app with Docker Compose.
2. Open `http://localhost:3000/` and use **2-minute demo**, or watch the included video.
3. Inspect the Evidence lab. Report numbers belong to the selected proposal; a new optimization can return a different feasible incumbent.
4. Reproduce the recorded validation with:

```bash
PYTHONPATH=services/api .venv/bin/python scripts/validate_plan.py submission/demo/recorded-validation.json
```

For the original evidence use the equivalent command with `data/experiments/20261014T091653Z/rush-validation-v1.json`.

## Record another demonstration

With the application running and frontend dependencies installed:

```bash
# Use an installed Chrome, or install Playwright Chromium instead.
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/routepulse-media apps/web/node_modules/.bin/playwright install ffmpeg
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/routepulse-media \
CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
DEMO_OUTPUT=submission/demo-new node scripts/record_demo.cjs
```

The script preserves an existing recording: choose a new output directory to rerun. Captions derive numerical claims from API results. No API response is mocked and no plan is accepted during recording. This is a scripted walkthrough, not a recording of user research.

## Entrant's final steps

Supply team identity and final public source/video/demo links through your own submission account. Verify the actual cutoff, PS assignment, common dataset and any build-window/AI declaration rules with the organizer. The official overview and schedule differ about duration; the published schedule currently ends on 15 October at 11:59 PM UTC+05:30. No registration, hosting, account upload or final submission has been performed here.
