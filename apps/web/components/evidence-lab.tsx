"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Download,
  FlaskConical,
  LoaderCircle,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import {
  api,
  metricNames,
  number,
  type History,
  type Optimization,
} from "@/lib/api";
import type { components } from "@/lib/generated";
type Validation = components["schemas"]["RobustnessResponse"];

export default function EvidenceLab({
  scenarioId,
  current,
  onOptimize,
}: {
  scenarioId: string;
  current: Optimization | null;
  onOptimize: () => void;
}) {
  const client = useQueryClient();
  const [selected, setSelected] = useState("");
  const history = useQuery({
    queryKey: ["history"],
    queryFn: () => api<History[]>("optimizations"),
  });
  const available =
    history.data?.filter((r) => r.scenario_id === scenarioId && r.candidate) ||
    [];
  const sourceId = selected || current?.id || available[0]?.id;
  const run = useQuery({
    queryKey: ["evidence-run", sourceId],
    queryFn: () => api<Optimization>(`optimizations/${sourceId}`),
    enabled: !!sourceId,
  });
  const validation = useQuery({
    queryKey: ["validation", sourceId],
    queryFn: () =>
      api<Validation | null>(`optimizations/${sourceId}/validation`),
    enabled: !!sourceId,
  });
  const evaluate = useMutation({
    mutationFn: (id: string) =>
      api<Validation>(`optimizations/${id}/validation`, {}),
    onSuccess: (data, id) => client.setQueryData(["validation", id], data),
  });
  const saved = run.data;
  const report = validation.data;
  const error =
    history.error || run.error || validation.error || evaluate.error;
  const b = saved?.baseline.metrics;
  const c = saved?.candidate?.metrics;
  const changedVehicles = saved
    ? new Set(saved.candidate?.plan.trips.map((t) => t.vehicle_id)).size
    : 0;
  return (
    <div className="evidence-lab">
      <section className="evidence-hero">
        <div>
          <span className="evidence-kicker">
            <FlaskConical size={15} /> DECISION EVIDENCE
          </span>
          <h2>
            One better plan.
            <br />
            Twenty different mornings.
          </h2>
          <p>
            More students reaching their destination, using the fleet already on
            campus. Inspect the evidence before putting a plan into operation.
          </p>
          <span className="evidence-tag">
            Synthetic evaluation · No field results claimed
          </span>
        </div>
        <div className="evidence-protocol">
          <ShieldCheck size={28} />
          <strong>Freeze → pair → verify</strong>
          <p>
            The same demand and traffic conditions for both plans. No retuning
            between days. Every result stays visible.
          </p>
        </div>
      </section>
      <section className="panel evidence-section">
        <div className="panel-head">
          <div>
            <h2>Choose the decision to challenge</h2>
            <p>
              Saved proposals are compared with their original published
              baseline.
            </p>
          </div>
          <button className="secondary-button" onClick={onOptimize}>
            Create a proposal <ArrowRight size={15} />
          </button>
        </div>
        {error && (
          <div className="error-box" role="alert">
            <TriangleAlert size={18} />
            {error.message}
            <button
              onClick={() => {
                history.refetch();
                run.refetch();
                validation.refetch();
                evaluate.reset();
              }}
            >
              Retry
            </button>
          </div>
        )}
        {history.isPending && <p role="status">Loading saved proposals…</p>}
        {!history.isPending && !sourceId && (
          <p>
            No candidate saved for this scenario yet. Run Optimization Studio,
            then return to test it.
          </p>
        )}
        {sourceId && (
          <div className="evidence-controls">
            <label>
              Saved proposal
              <select
                aria-label="Evidence proposal"
                value={sourceId}
                disabled={evaluate.isPending}
                onChange={(e) => {
                  setSelected(e.target.value);
                  evaluate.reset();
                }}
              >
                {current && !available.some((r) => r.id === current.id) && (
                  <option value={current.id}>
                    Current proposal · {current.id.slice(0, 8)}
                  </option>
                )}
                {available.map((r) => (
                  <option key={r.id} value={r.id}>
                    {new Date(r.created_at).toLocaleString()} ·{" "}
                    {r.id.slice(0, 8)}
                  </option>
                ))}
              </select>
            </label>
            <button
              className="primary-button"
              disabled={
                !saved?.candidate ||
                evaluate.isPending ||
                !!report ||
                validation.isPending
              }
              onClick={() => sourceId && evaluate.mutate(sourceId)}
            >
              {evaluate.isPending ? (
                <LoaderCircle size={16} className="spin" />
              ) : (
                <FlaskConical size={16} />
              )}
              {report
                ? "20-day validation saved"
                : evaluate.isPending
                  ? "Evaluating 20 paired days…"
                  : "Test on 20 new days"}
            </button>
          </div>
        )}
        {saved && (
          <p className="evidence-note">
            {saved.scenario.name} · demand ×{saved.scenario.demand_multiplier} ·
            traffic ×{saved.scenario.traffic_factor} · breakdown{" "}
            {saved.scenario.breakdown_vehicle || "none"} · objective{" "}
            {saved.objective} · planning seed {saved.planning_seed} · original
            evaluation seed {saved.evaluation_seed}. Proposal status:{" "}
            {saved.decision}.
          </p>
        )}
      </section>
      {saved && b && c && (
        <>
          <section className="panel evidence-section">
            <div className="panel-head">
              <div>
                <h2>The original day, in human terms</h2>
                <p>
                  Computed from this saved proposal. These are simulated
                  outcomes.
                </p>
              </div>
              <a href={`/api/v1/reports/${saved.id}`} download>
                <Download size={14} /> Source JSON
              </a>
            </div>
            <div className="impact-grid">
              <Impact
                label="Additional completed journeys"
                value={`${c.served - b.served >= 0 ? "+" : ""}${number(c.served - b.served)}`}
                detail={`${b.served} → ${c.served} of ${b.passengers} passengers`}
              />
              <Impact
                label="Mean queue wait change"
                value={`${number(c.average_wait - b.average_wait, 2)} min`}
                detail={`${number(b.average_wait, 2)} → ${number(c.average_wait, 2)} min · lower is better`}
              />
              <Impact
                label="Vehicles used · candidate / baseline"
                value={`${changedVehicles} / ${new Set(saved.baseline.plan.trips.map((t) => t.vehicle_id)).size}`}
                detail={`${saved.changes.length} duties changed · ${number(c.operating_minutes - b.operating_minutes, 1)} operating minute change`}
              />
              <Impact
                label="Missed connection change"
                value={`${c.missed_connections - b.missed_connections > 0 ? "+" : ""}${c.missed_connections - b.missed_connections}`}
                detail={`${b.missed_connections} → ${c.missed_connections} · lower is better`}
              />
            </div>
            <p className="evidence-note">
              The service objective prioritizes completed journeys. An aggregate
              improvement can still worsen an individual stop or transfer;
              review the distribution below.
            </p>
          </section>
          {report && (
            <>
              <section
                className="panel evidence-section"
                aria-label="Multi-day validation results"
              >
                <div className="panel-head">
                  <div>
                    <h2>Does the improvement survive different days?</h2>
                    <p>
                      {report.days} paired evaluations ·{" "}
                      {report.protocol_version}
                    </p>
                  </div>
                  <div className="evidence-downloads">
                    <a href={`/api/v1/reports/${report.id}`} download>
                      Validation JSON
                    </a>
                    <a
                      href={`/api/v1/reports/${report.id}?format=csv`}
                      download
                    >
                      Daily CSV
                    </a>
                  </div>
                </div>
                <div className="impact-grid">
                  <Impact
                    label="Days with more completed journeys"
                    value={`${report.service_win_days} / ${report.days}`}
                    detail={`${report.service_loss_days} worse · ${report.days - report.service_win_days - report.service_loss_days} tied`}
                  />
                  <Impact
                    label="Mean additional journeys"
                    value={number(report.summary.served.mean_delta, 1)}
                    detail={`Observed range ${number(report.summary.served.minimum_delta)} to ${number(report.summary.served.maximum_delta)}`}
                  />
                  <Impact
                    label="Days with worse transfers"
                    value={`${report.transfer_regression_days} / ${report.days}`}
                    detail="All regressions remain in the results"
                  />
                  <Impact
                    label="Candidate violations across days"
                    value={String(
                      report.candidate_capacity_violations +
                        report.candidate_feasibility_violations,
                    )}
                    detail={`${report.candidate_capacity_violations} capacity · ${report.candidate_feasibility_violations} feasibility`}
                  />
                </div>
                <div className="table-scroll">
                  <table>
                    <caption>
                      Candidate minus published baseline. Lower is better except
                      completed journeys; operating time is a resource
                      trade-off.
                    </caption>
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>Mean change</th>
                        <th>95% interval for mean</th>
                        <th>Observed daily range</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(report.summary).map(([key, s]) => (
                        <tr key={key}>
                          <td>
                            {metricNames[key as keyof typeof metricNames]}
                          </td>
                          <td>{number(s.mean_delta, 2)}</td>
                          <td>
                            {number(s.mean_ci_low, 2)} to{" "}
                            {number(s.mean_ci_high, 2)}
                          </td>
                          <td>
                            {number(s.minimum_delta, 2)} to{" "}
                            {number(s.maximum_delta, 2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="evidence-note">{report.methodology}</p>
                <details>
                  <summary>
                    Inspect all {report.days} days and reproduction details
                  </summary>
                  <p className="evidence-note">
                    Seeds: {report.seeds.join(", ")}. Bootstrap:{" "}
                    {report.bootstrap_samples} samples, seed{" "}
                    {report.bootstrap_seed}. Snapshot SHA-256:{" "}
                    <code>{report.plan_sha256}</code>
                  </p>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          <th>Seed</th>
                          <th>Baseline served</th>
                          <th>Candidate served</th>
                          <th>Wait Δ (min)</th>
                          <th>Missed transfers Δ</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.rows.map((row) => (
                          <tr key={row.seed}>
                            <td>{row.seed}</td>
                            <td>{row.baseline.served}</td>
                            <td>{row.candidate.served}</td>
                            <td>{number(row.delta.average_wait, 2)}</td>
                            <td>{row.delta.missed_connections}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </details>
              </section>
              <section className="panel evidence-section">
                <div className="panel-head">
                  <div>
                    <h2>Who benefits — and who waits longer?</h2>
                    <p>
                      By passenger origin, pooled across all {report.days} days.
                      Final-destination completion includes transfers.
                    </p>
                  </div>
                </div>
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Origin</th>
                        <th>Passengers</th>
                        <th>Baseline served</th>
                        <th>Candidate served</th>
                        <th>Mean wait change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.origins.map((row) => (
                        <tr key={row.stop_id}>
                          <td>{row.stop_name}</td>
                          <td>{number(row.passengers)}</td>
                          <td>{number(row.baseline_service_rate, 1)}%</td>
                          <td>{number(row.candidate_service_rate, 1)}%</td>
                          <td>
                            <span
                              className={
                                row.mean_wait_delta > 0
                                  ? "impact-regression"
                                  : "impact-improvement"
                              }
                            >
                              {row.mean_wait_delta > 0 ? "+" : ""}
                              {number(row.mean_wait_delta, 2)} min
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}
        </>
      )}
      <section className="panel evidence-section">
        <div className="panel-head">
          <div>
            <h2>From simulation to a campus pilot</h2>
            <p>
              Proposed validation steps. No customers, interviews or deployments
              are claimed.
            </p>
          </div>
        </div>
        <div className="pilot-grid">
          <div>
            <span>01 / DISCOVER</span>
            <h3>One campus. One morning peak.</h3>
            <p>
              Interview a dispatcher and students. Obtain de-identified stop
              counts, vehicle capacities, timetables and GPS history.
            </p>
          </div>
          <div>
            <span>02 / SHADOW</span>
            <h3>Measure before dispatching.</h3>
            <p>
              Calibrate on real history, freeze the model, and compare
              recommendations on later days without changing live service.
            </p>
          </div>
          <div>
            <span>03 / DECIDE</span>
            <h3>Keep operators in control.</h3>
            <p>
              Agree on completion, wait and transfer targets with the transport
              office. Review driver constraints and stop-level regressions
              before a supervised trial.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
function Impact({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="impact-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
