"""Build a portable offline review page from the exact recorded evaluation."""

import html
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
report = json.loads((root / "submission/demo/recorded-validation.json").read_text())
run = json.loads((root / "submission/demo/recorded-optimization.json").read_text())
s = report["summary"]
body = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>RoutePulse · WILD BUGS PS 02</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f6f7fc;color:#26243e;font:16px/1.65 system-ui,sans-serif}}main{{max-width:1050px;margin:auto;padding:48px 24px}}.label{{color:#7160cc;text-transform:uppercase;letter-spacing:2px;font-size:12px;font-weight:700}}h1{{font-size:clamp(38px,7vw,68px);line-height:1.05;letter-spacing:-3px;margin:20px 0}}h2{{font-size:23px;line-height:1.3}}p{{color:#656579}}.hero{{max-width:800px}}.tag{{display:inline-block;padding:6px 12px;background:#eae5fa;color:#6654ae;border-radius:30px;font-size:12px}}video{{width:100%;border-radius:14px;background:#25223f}}.video{{background:white;padding:16px;border:1px solid #e2e1ee;border-radius:20px;margin:30px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}article{{background:white;border:1px solid #e2e1ee;border-radius:14px;padding:22px}}article strong{{display:block;font-size:35px;line-height:1.2;letter-spacing:-1px}}article p{{font-size:13px;margin-bottom:0}}a{{color:#6553ba;text-decoration:none;font-weight:600}}a:hover{{text-decoration:underline}}.links{{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}}.links a{{padding:10px 16px;border:1px solid #dcd7ef;border-radius:8px;background:white;font-size:14px}}code{{font-size:12px;overflow-wrap:anywhere}}.notice{{border-left:3px solid #8574d4;padding-left:18px;margin:30px 0}}footer{{font-size:12px;color:#77758a;margin-top:35px}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}main{{padding:28px 18px}}h1{{letter-spacing:-1.6px}}}}a:focus-visible{{outline:3px solid #9e8de6;outline-offset:3px}}
</style></head><body><main>
<div class="hero"><div class="label">WILD BUGS · PS 02 · Local review kit</div><h1>A better morning.<br>A plan you can verify.</h1><p>RoutePulse helps campus operators compare feasible timetable and vehicle changes, then inspect their impact on passenger journeys, waiting and connections.</p><span class="tag">Working prototype · Synthetic campus data</span></div>
<section class="video" aria-label="Recorded demonstration"><video controls preload="metadata" poster="demo/poster.png"><source src="demo/routepulse-demo.webm" type="video/webm"><track kind="captions" src="demo/captions.vtt" srclang="en" label="English">Your browser does not support WebM. Use the video download link.</video><p>Approximately two minutes. Silent, with visible captions. Actual localhost interactions; no mocked responses.</p><a href="demo/routepulse-demo.webm" download>Download walkthrough</a></section>
<h2>The recorded proposal, tested on {report["days"]} different mornings</h2>
<div class="grid"><article><div class="label">Completed journeys</div><strong>+{s["served"]["mean_delta"]:.1f}</strong><p>Mean daily change. {report["service_win_days"]}/{report["days"]} days improved.</p></article><article><div class="label">Mean waiting</div><strong>{s["average_wait"]["mean_delta"]:.2f} min</strong><p>Candidate minus baseline across paired synthetic days.</p></article><article><div class="label">Transfer trade-off</div><strong>{report["transfer_regression_days"]}/{report["days"]} days</strong><p>Missed transfers worsened. The report retains these regressions.</p></article></div>
<div class="notice"><p>These are simulator results, not observed campus benefits. The mean additional-journey bootstrap interval is {s["served"]["mean_ci_low"]:.2f}–{s["served"]["mean_ci_high"]:.2f}; it does not guarantee a future day's outcome. The plan remains {html.escape(run["decision"])}.</p></div>
<h2>Inspect the work</h2><div class="links"><a href="PROJECT_DESCRIPTION.md">Project description</a><a href="EVENT_REQUIREMENTS.md">Official requirement audit</a><a href="JUDGE_QA.md">Judge questions</a><a href="DISCLOSURE.md">Build disclosure</a><a href="demo/recorded-optimization.json">Recorded optimization JSON</a><a href="demo/recorded-validation.json">Twenty-day validation JSON</a><a href="../README.md">Run the source</a></div>
<p>Source experiment: <code>{html.escape(report["source_run_id"])}</code><br>Validation: <code>{html.escape(report["id"])}</code></p>
<h2>What remains with the entrant</h2><p>Add team identity and public project/video links through the submission account. Confirm the organizer's precise cutoff, common dataset and build-window declarations. This package has not been uploaded or submitted.</p>
<footer>RoutePulse · WILD BUGS PS 02 · The official challenge permits synthetic data; real campus integration is optional.</footer>
</main></body></html>"""
(root / "submission/index.html").write_text(body)
print("Built submission/index.html from recorded evidence")
