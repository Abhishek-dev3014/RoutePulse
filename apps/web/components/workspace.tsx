"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  QueryClient,
  QueryClientProvider,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  BusFront,
  Check,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Clock3,
  Download,
  FlaskConical,
  Layers3,
  LayoutDashboard,
  LoaderCircle,
  Map,
  MoreHorizontal,
  Network,
  PanelLeftClose,
  Printer,
  Radio,
  RefreshCw,
  Route as RouteIcon,
  ShieldCheck,
  Sparkles,
  TriangleAlert,
  Users,
  X,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { z } from "zod";
import {
  api,
  clock,
  metricNames,
  number,
  scenarioSchema,
  type Dashboard,
  type Feasibility,
  type History,
  type Optimization,
  type Prediction,
} from "@/lib/api";
import NetworkMap from "./network-map";
import EvidenceLab from "./evidence-lab";
const client = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 60000, retry: 1, refetchOnWindowFocus: false },
  },
});
const nav = [
  { id: "overview", name: "Overview", icon: LayoutDashboard },
  { id: "network", name: "Campus network", icon: Map },
  { id: "fleet", name: "Fleet & timetable", icon: BusFront },
  { id: "demand", name: "Demand intelligence", icon: Users },
  { id: "studio", name: "Optimization Studio", icon: Sparkles },
  { id: "disruptions", name: "Disruption simulator", icon: Zap },
  { id: "evidence", name: "Evidence lab", icon: FlaskConical },
  { id: "reports", name: "Analytics & reports", icon: BarChart3 },
];
const titles: Record<string, [string, string]> = {
  overview: [
    "Operations overview",
    "A clearer view of your campus. A better plan for every journey.",
  ],
  network: [
    "Campus network",
    "Follow shuttle movements, inspect stops and replay the morning.",
  ],
  fleet: [
    "Fleet & timetable",
    "Every vehicle, every duty, every departure window.",
  ],
  demand: [
    "Demand intelligence",
    "Understand where your next capacity pressure will emerge.",
  ],
  studio: [
    "Optimization Studio",
    "Turn operational pressure into a feasible, measurable plan.",
  ],
  disruptions: [
    "Disruption simulator",
    "Test the unexpected. Find a recovery plan before it happens.",
  ],
  evidence: [
    "Evidence lab",
    "Challenge a frozen proposal. Make the gains and trade-offs inspectable.",
  ],
  reports: [
    "Analytics & reports",
    "Measured outcomes, transparent assumptions and reproducible evidence.",
  ],
};
export default function Workspace() {
  return (
    <QueryClientProvider client={client}>
      <Shell />
    </QueryClientProvider>
  );
}
function Shell() {
  const [view, setView] = useState("overview");
  const [scenarioId, setScenarioId] = useState("rush");
  const [collapsed, setCollapsed] = useState(false);
  const [demoStep, setDemoStep] = useState<number | null>(null);
  const demoSteps = [
    {
      view: "overview",
      time: "0:00–0:20",
      title: "A student waiting is an operational problem.",
      text: "Show the current campus fleet and queues. This is a fictional campus with calculated passenger outcomes.",
    },
    {
      view: "studio",
      time: "0:20–1:00",
      title: "Change the plan with the fleet you have.",
      text: "Run optimization. Show the changed duties, ten constraint checks and before/after results. Proposals need an operator decision.",
    },
    {
      view: "evidence",
      time: "1:00–1:40",
      title: "Challenge the result on twenty mornings.",
      text: "Test the saved proposal or open its saved validation. Show completed journeys, transfer regressions and stop-level impact.",
    },
    {
      view: "reports",
      time: "1:40–2:00",
      title: "Leave the judges with evidence.",
      text: "Show measured ETA error and export a report. Close with a one-campus shadow pilot; real-world benefits still need validation.",
    },
  ];
  const scenarios = useQuery({
    queryKey: ["scenarios"],
    queryFn: async () =>
      z.array(scenarioSchema).parse(await api<unknown>("scenarios")),
  });
  return (
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="sidebar">
        <Link className="brand" href="/">
          <span className="brand-icon">
            <Activity size={24} />
          </span>
          <span>
            Route<span className="brand-light">Pulse</span>
            <small>TRANSPORT INTELLIGENCE</small>
          </span>
        </Link>
        <button className="campus-switch" onClick={() => setView("network")}>
          <span className="campus-avatar">M</span>
          <span>
            <strong>Meridian University</strong>
            <small>Campus workspace</small>
          </span>
          <ChevronDown size={14} />
        </button>
        <p className="nav-label">WORKSPACE</p>
        <nav aria-label="Main navigation">
          {nav.map((n) => (
            <button
              key={n.id}
              aria-label={n.name}
              className={view === n.id ? "nav-active" : ""}
              onClick={() => setView(n.id)}
              aria-current={view === n.id ? "page" : undefined}
            >
              <n.icon size={19} />
              <span>{n.name}</span>
              {n.id === "studio" && <span className="nav-new">LAB</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="demo-card">
            <span>
              <FlaskConical size={16} /> DEMO ENVIRONMENT
            </span>
            <p>
              Real calculations.
              <br />
              Synthetic campus data.
            </p>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
            >
              Explore the API <ArrowUpRight size={14} />
            </a>
          </div>
          <button className="support-link" onClick={() => setView("reports")}>
            <CircleHelp size={18} /> Methodology & evidence
          </button>
          <div className="profile">
            <span>OP</span>
            <div>
              <strong>Campus operator</strong>
              <small>Single-organization demo</small>
            </div>
            <MoreHorizontal size={17} />
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            <button
              className="icon-button"
              aria-label="Toggle navigation"
              onClick={() => setCollapsed(!collapsed)}
            >
              <PanelLeftClose size={18} />
            </button>
            <span>Workspace</span>
            <span>/</span>
            <strong>{nav.find((n) => n.id === view)?.name}</strong>
          </div>
          <div className="topbar-right">
            <button
              className="secondary-button"
              onClick={() => {
                setDemoStep(0);
                setScenarioId("rush");
                setView("overview");
              }}
            >
              2-minute demo
            </button>
            <span className="system-state">
              <i /> Simulation environment
            </span>
            <button
              className="icon-button"
              aria-label="View operational alerts"
              onClick={() => setView("overview")}
            >
              <Bell size={18} />
            </button>
            <span className="avatar">OP</span>
          </div>
        </header>
        <main>
          <div className="page-title">
            <div>
              <div className="eyebrow">
                MERIDIAN CAMPUS <span> / </span> WED, 14 OCT 2026
              </div>
              <h1>{titles[view][0]}</h1>
              <p>{titles[view][1]}</p>
            </div>
            <div className="title-actions">
              <label className="scenario-picker">
                <FlaskConical size={16} />
                <select
                  aria-label="Scenario"
                  value={scenarioId}
                  onChange={(e) => setScenarioId(e.target.value)}
                >
                  {scenarios.data?.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </label>
              <button
                className="primary-button"
                onClick={() => setView("studio")}
              >
                <Sparkles size={16} /> Optimize plan
              </button>
            </div>
          </div>
          {demoStep !== null && (
            <section className="demo-guide" aria-label="Guided demo">
              <div>
                <span>
                  DEMO {demoStep + 1} / 4 · {demoSteps[demoStep].time}
                </span>
                <strong>{demoSteps[demoStep].title}</strong>
                <p>{demoSteps[demoStep].text}</p>
              </div>
              <div className="demo-guide-actions">
                <button
                  className="secondary-button"
                  onClick={() => {
                    const next = Math.max(0, demoStep - 1);
                    setDemoStep(next);
                    setView(demoSteps[next].view);
                  }}
                  disabled={demoStep === 0}
                >
                  Back
                </button>
                <button
                  className="primary-button"
                  onClick={() => {
                    if (demoStep === 3) {
                      setDemoStep(null);
                    } else {
                      setDemoStep(demoStep + 1);
                      setView(demoSteps[demoStep + 1].view);
                    }
                  }}
                >
                  {demoStep === 3 ? "Finish demo" : "Next step"}
                </button>
                <button
                  className="icon-button"
                  aria-label="Close guided demo"
                  onClick={() => setDemoStep(null)}
                >
                  <X size={17} />
                </button>
              </div>
            </section>
          )}
          {scenarios.error ? (
            <ErrorBox
              message={scenarios.error.message}
              retry={() => scenarios.refetch()}
            />
          ) : (
            <Content
              key={scenarioId}
              scenarioId={scenarioId}
              view={view}
              setView={setView}
            />
          )}
          <footer>
            <span>
              <Activity size={13} /> RoutePulse · Explainable campus mobility
            </span>
            <span>Synthetic data · Asia/Kolkata · 08:00–10:00 evaluation</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
function Content({
  scenarioId,
  view,
  setView,
}: {
  scenarioId: string;
  view: string;
  setView: (v: string) => void;
}) {
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["dashboard", scenarioId],
    queryFn: () => api<Dashboard>(`dashboard?scenario_id=${scenarioId}`),
  });
  const [custom, setCustom] = useState<Dashboard | null>(null);
  const [minute, setMinute] = useState(40);
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<Optimization | null>(null);
  const [objective, setObjective] = useState("service");
  const data = custom || query.data;
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(
      () => setMinute((t) => (t >= 119.5 ? 0 : t + 0.5)),
      1000,
    );
    return () => clearInterval(timer);
  }, [playing]);
  const optimizer = useMutation({
    mutationFn: () =>
      api<Optimization>("optimizations", {
        scenario_id: scenarioId,
        objective,
        ...(custom
          ? {
              demand_multiplier: custom.scenario.demand_multiplier,
              traffic_factor: custom.scenario.traffic_factor,
              breakdown_vehicle: custom.scenario.breakdown_vehicle,
              affected_route: custom.scenario.affected_route,
              disruption_start: custom.scenario.disruption_start,
              disruption_end: custom.scenario.disruption_end,
            }
          : {}),
      }),
    onSuccess: (r) => {
      setResult(r);
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });
  const decision = useMutation({
    mutationFn: (value: string) =>
      api(`optimizations/${result?.id}/decision`, { decision: value }),
    onSuccess: async (_, value) => {
      setResult((r) => (r ? { ...r, decision: value } : r));
      if (custom) {
        const sc = custom.scenario;
        const updated = await api<Dashboard>("simulations", {
          scenario_id: sc.id,
          demand_multiplier: sc.demand_multiplier,
          traffic_factor: sc.traffic_factor,
          breakdown_vehicle: sc.breakdown_vehicle,
          affected_route: sc.affected_route,
          disruption_start: sc.disruption_start,
          disruption_end: sc.disruption_end,
        });
        setCustom(updated);
      }
      queryClient.invalidateQueries({ queryKey: ["dashboard", scenarioId] });
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });
  if (query.error)
    return (
      <ErrorBox message={query.error.message} retry={() => query.refetch()} />
    );
  if (!data)
    return (
      <div className="loading-state">
        <LoaderCircle className="spin" />
        <h2>Building your operations picture</h2>
        <p>Running the seeded simulation and validating forecasts…</p>
      </div>
    );
  const m = data.simulation.metrics;
  return (
    <>
      <div className="context-strip">
        <span>
          <span className="status-dot" />
          {data.active_plan
            ? "Accepted plan in operation"
            : "Published baseline"}
          <span className="divider">|</span>
          {data.scenario.description}
        </span>
        <span className="seed-label">
          SEED {data.scenario.seed} <span className="divider">|</span> v
          {data.scenario.version}
        </span>
      </div>
      {(view === "overview" || view === "network") && (
        <>
          {view === "overview" && (
            <>
              <div className="stats-grid">
                <Stat
                  label="Completed journeys"
                  value={number(m.served)}
                  unit={`/ ${number(m.passengers)}`}
                  icon={Users}
                  foot={`${number(m.service_rate, 1)}% passenger service rate`}
                  tone="purple"
                />
                <Stat
                  label="Average passenger wait"
                  value={number(m.average_wait, 1)}
                  unit="min"
                  icon={Clock3}
                  foot={`95th percentile · ${number(m.p95_wait, 1)} min`}
                  tone="amber"
                />
                <Stat
                  label="Fleet utilization"
                  value={number(m.fleet_utilization, 1)}
                  unit="%"
                  icon={BusFront}
                  foot={`${data.network.vehicles.length} vehicles · ${number(m.operating_minutes)} operating min`}
                  tone="blue"
                />
                <Stat
                  label="Operational alerts"
                  value={String(data.alerts.length)}
                  unit="issues"
                  icon={TriangleAlert}
                  foot={`${m.unserved} unserved · ${m.missed_connections} missed transfers`}
                  tone="rose"
                />
              </div>
              <div className="opportunity-banner">
                <span className="opportunity-icon">
                  <Sparkles size={22} />
                </span>
                <div>
                  <strong>A better morning starts with a better plan.</strong>
                  <p>
                    {data.scenario.challenge} Explore feasible changes using the
                    fleet you already have.
                  </p>
                </div>
                <button onClick={() => setView("studio")}>
                  Open Optimization Studio <ArrowRight size={17} />
                </button>
              </div>
            </>
          )}
          <div
            className={view === "overview" ? "overview-grid" : "network-layout"}
          >
            <NetworkMap
              data={data}
              minute={minute}
              setMinute={setMinute}
              playing={playing}
              setPlaying={setPlaying}
              large={view === "network"}
            />
            <div className="right-stack">
              <Alerts data={data} />
              <div className="panel compact-panel">
                <div className="panel-head">
                  <h2>Network health</h2>
                  <ShieldCheck size={18} />
                </div>
                <div className="health-row">
                  <span>Physical capacity violations</span>
                  <strong className="green">{m.capacity_violations}</strong>
                </div>
                <div className="health-row">
                  <span>Schedule constraints</span>
                  <span
                    className={`badge ${data.simulation.feasibility.feasible ? "success" : "warning"}`}
                  >
                    {data.simulation.feasibility.feasible
                      ? "All passed"
                      : `${m.feasibility_violations} issues`}
                  </span>
                </div>
                <div className="health-row">
                  <span>ETA interval coverage</span>
                  <strong>{data.eta.coverage}%</strong>
                </div>
                <p className="micro-copy">
                  Measured on held-out GPS traces. 80% target coverage.
                </p>
              </div>
            </div>
          </div>
          <div className="two-col">
            <DemandChart data={data} />
            <ArrivalBoard data={data} minute={minute} />
          </div>
        </>
      )}
      {view === "evidence" && (
        <EvidenceLab
          scenarioId={scenarioId}
          current={result}
          onOptimize={() => setView("studio")}
        />
      )}
      {view === "fleet" && <Fleet data={data} />}
      {view === "demand" && <Demand data={data} />}
      {view === "studio" && (
        <>
          <div className="studio-hero">
            <div>
              <span className="eyebrow">
                OBSERVE → PREDICT → OPTIMIZE → VALIDATE
              </span>
              <h2>Your next move, backed by evidence.</h2>
              <p>
                Search departure windows and vehicle assignments. Compare both
                plans against the same passengers, traffic and evaluation seed.
              </p>
            </div>
            <div className="solver-mark">
              <Network size={58} />
              <span>CONSTRAINT-AWARE PLANNING</span>
            </div>
          </div>
          <div className="studio-controls">
            <div>
              <label htmlFor="objective">Planning objective</label>
              <select
                id="objective"
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
              >
                <option value="service">
                  Service first · reduce unserved demand
                </option>
                <option value="wait">
                  Service first · then minimize waiting
                </option>
                <option value="balanced">
                  Service first · balance waits and changes
                </option>
              </select>
            </div>
            <span>
              <ShieldCheck size={16} /> 10 constraint categories
              <br />
              <small>
                Existing fleet · bounded search · separate planning seed
              </small>
            </span>
            <button
              className="primary-button"
              disabled={optimizer.isPending}
              onClick={() => optimizer.mutate()}
            >
              {optimizer.isPending ? (
                <LoaderCircle className="spin" size={17} />
              ) : (
                <Sparkles size={17} />
              )}{" "}
              {optimizer.isPending
                ? "Evaluating candidates…"
                : "Run optimization"}
            </button>
          </div>
          {optimizer.error && <ErrorBox message={optimizer.error.message} />}
          {result ? (
            <>
              <div
                className={`recommendation ${result.candidate ? "" : "no-result"}`}
              >
                <div className="recommendation-heading">
                  <span className="badge success">
                    <ShieldCheck size={13} />
                    {result.candidate
                      ? "Feasible recommendation"
                      : "Search complete"}
                  </span>
                  <span>
                    {result.candidates_evaluated} candidates ·{" "}
                    {result.runtime_seconds}s ·{" "}
                    {result.status.replaceAll("_", " ").toLowerCase()}
                  </span>
                </div>
                <h2>
                  {result.candidate
                    ? `${result.changes.length} duty changes. One validated plan.`
                    : "No feasible improvement found."}
                </h2>
                <p>{result.explanation}</p>
                <div className="recommendation-actions">
                  {result.candidate && result.decision === "pending" ? (
                    <>
                      <button
                        className="primary-button"
                        disabled={decision.isPending}
                        onClick={() => decision.mutate("accepted")}
                      >
                        <Check size={16} /> Accept plan
                      </button>
                      <button
                        className="secondary-button"
                        disabled={decision.isPending}
                        onClick={() => decision.mutate("rejected")}
                      >
                        Reject proposal
                      </button>
                    </>
                  ) : (
                    <span className="badge neutral">
                      {result.decision.replaceAll("_", " ")}
                    </span>
                  )}
                  <a
                    className="text-link"
                    href={`/api/v1/reports/${result.id}?format=json`}
                    download
                  >
                    <Download size={15} /> Export experiment
                  </a>
                </div>
                {decision.error && (
                  <ErrorBox message={decision.error.message} />
                )}
              </div>
              <Comparison result={result} />
              <div className="two-col">
                <div className="panel">
                  <div className="panel-head">
                    <h2>What changes</h2>
                    <span className="badge neutral">
                      {result.changes.length} duties
                    </span>
                  </div>
                  <div className="change-list">
                    {result.changes.map((c) => (
                      <div className="change-item" key={c.trip_id}>
                        <span className="change-icon">
                          <RouteIcon size={17} />
                        </span>
                        <div>
                          <strong>
                            {c.trip_id}{" "}
                            <span className="muted">/ {c.route_id}</span>
                          </strong>
                          <p>
                            {c.old_vehicle} → <b>{c.new_vehicle}</b>{" "}
                            <span className="divider">·</span>{" "}
                            {clock(c.old_departure)} →{" "}
                            <b>{clock(c.new_departure)}</b>
                          </p>
                          <small>{c.explanation}</small>
                        </div>
                      </div>
                    ))}
                    {!result.changes.length && (
                      <p className="empty-copy">
                        The published timetable remains unchanged.
                      </p>
                    )}
                  </div>
                </div>
                <div>
                  <FeasibilityCard
                    report={(result.candidate || result.baseline).feasibility}
                  />
                  <div className="panel padded tradeoffs">
                    <h2>Trade-offs & assumptions</h2>
                    {result.tradeoffs.map((t, i) => (
                      <p key={i}>
                        <span>{i + 1}</span>
                        {t}
                      </p>
                    ))}
                    <small>
                      Planning seed {result.planning_seed} · evaluation seed{" "}
                      {result.evaluation_seed}. Selection happens before
                      held-out evaluation.
                    </small>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="two-col">
              <div className="panel padded">
                <h2>Current operating picture</h2>
                <p className="section-copy">
                  Run the search to produce an actual recommendation and
                  comparison.
                </p>
                <div className="baseline-facts">
                  <div>
                    <strong>{m.unserved}</strong>
                    <span>unserved passengers</span>
                  </div>
                  <div>
                    <strong>
                      {m.average_wait}
                      <small> min</small>
                    </strong>
                    <span>average wait, all riders</span>
                  </div>
                  <div>
                    <strong>{m.missed_connections}</strong>
                    <span>missed connections</span>
                  </div>
                </div>
              </div>
              <FeasibilityCard report={data.simulation.feasibility} />
            </div>
          )}
        </>
      )}
      {view === "disruptions" && (
        <Disruptions
          data={data}
          onRun={(d) => {
            setCustom(d);
            setResult(null);
          }}
          onOptimize={() => setView("studio")}
        />
      )}
      {view === "reports" && (
        <Reports
          data={data}
          result={result}
          onOpen={(r) => {
            setResult(r);
            setView("studio");
          }}
        />
      )}
    </>
  );
}
function Stat({
  label,
  value,
  unit,
  icon: Icon,
  foot,
  tone,
}: {
  label: string;
  value: string;
  unit: string;
  icon: typeof Users;
  foot: string;
  tone: string;
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <span>{label}</span>
        <span className={`stat-icon ${tone}`}>
          <Icon size={17} />
        </span>
      </div>
      <div className="stat-value">
        {value}
        <span>{unit}</span>
      </div>
      <div className="stat-foot">
        <span className={`tiny-dot ${tone}`} />
        {foot}
      </div>
    </div>
  );
}
function ErrorBox({ message, retry }: { message: string; retry?: () => void }) {
  return (
    <div className="error-box" role="alert">
      <TriangleAlert size={19} />
      <span>{message}</span>
      {retry && <button onClick={retry}>Retry</button>}
    </div>
  );
}
function Alerts({ data }: { data: Dashboard }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <section className="panel alerts-panel">
      <div className="panel-head">
        <h2>
          Needs attention{" "}
          <span className="count-pill">{data.alerts.length}</span>
        </h2>
        <Radio size={17} />
      </div>
      <div className={`alerts-list ${expanded ? "expanded" : ""}`}>
        {(expanded ? data.alerts : data.alerts.slice(0, 3)).map((a) => (
          <div className={`alert-item ${a.severity}`} key={a.id}>
            <span className="alert-symbol">
              <TriangleAlert size={16} />
            </span>
            <div>
              <strong>{a.title}</strong>
              <p>{a.description}</p>
              <span className="alert-type">{a.type.replaceAll("_", " ")}</span>
            </div>
          </div>
        ))}
        {!data.alerts.length && (
          <p className="empty-copy">No issues detected for this run.</p>
        )}
      </div>
      {data.alerts.length > 3 && (
        <button
          className="panel-bottom-button"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded
            ? "Show fewer alerts"
            : `View all ${data.alerts.length} alerts`}{" "}
          <ArrowRight size={14} />
        </button>
      )}
    </section>
  );
}
function DemandChart({ data }: { data: Dashboard }) {
  const bins = Array.from({ length: 8 }, (_, i) => ({
    time: clock(i * 15),
    forecast: Math.round(
      data.demand.rows
        .filter((r) => r.minute === i * 15)
        .reduce((s, r) => s + r.expected, 0),
    ),
    actual: data.demand.rows
      .filter((r) => r.minute === i * 15)
      .reduce((s, r) => s + r.actual, 0),
  }));
  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Demand across the morning</h2>
          <p>Passenger arrivals · 15-minute intervals</p>
        </div>
        <span className="badge neutral">HELD-OUT DAY</span>
      </div>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={bins}
            margin={{ top: 10, right: 22, left: -18, bottom: 0 }}
          >
            <defs>
              <linearGradient id="demandFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#7169e7" stopOpacity={0.22} />
                <stop offset="100%" stopColor="#7169e7" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="4 4"
              vertical={false}
              stroke="#eceef2"
            />
            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={false}
              fontSize={10}
            />
            <YAxis tickLine={false} axisLine={false} fontSize={10} />
            <Tooltip />
            <Area
              isAnimationActive={false}
              type="monotone"
              dataKey="actual"
              name="Actual arrivals"
              stroke="#7367e7"
              fill="url(#demandFill)"
              strokeWidth={2.5}
            />
            <Area
              isAnimationActive={false}
              type="monotone"
              dataKey="forecast"
              name="Historical forecast"
              stroke="#a5b2be"
              fill="none"
              strokeDasharray="5 4"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="chart-legend">
        <span>
          <i style={{ background: "#7367e7" }} /> Actual arrivals
        </span>
        <span>
          <i style={{ background: "#a5b2be" }} /> Historical forecast
        </span>
        <span>MAE {data.demand.mae} riders / bin</span>
      </div>
    </section>
  );
}
function ArrivalBoard({ data, minute }: { data: Dashboard; minute: number }) {
  const relevant = data.simulation.gps.filter(
    (g) => g.timestamp <= minute && g.timestamp >= minute - 2,
  );
  const predictions = useQuery({
    queryKey: ["eta", data.scenario, data.simulation.plan.id, minute],
    queryFn: () =>
      api<{ predictions: Prediction[] }>("forecasts/eta", {
        scenario_id: data.scenario.id,
        demand_multiplier: data.scenario.demand_multiplier,
        traffic_factor: data.scenario.traffic_factor,
        breakdown_vehicle: data.scenario.breakdown_vehicle,
        affected_route: data.scenario.affected_route,
        disruption_start: data.scenario.disruption_start,
        disruption_end: data.scenario.disruption_end,
        plan: data.simulation.plan,
        observations: relevant,
        as_of: minute,
      }),
    enabled: relevant.length > 0,
  });
  const rows =
    predictions.data?.predictions
      .filter(
        (r, i, all) =>
          all.findIndex((x) => x.vehicle_id === r.vehicle_id) === i,
      )
      .slice(0, 4) || [];
  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Next arrivals</h2>
          <p>GPS-based estimates at {clock(minute)}</p>
        </div>
        <span className="badge success">
          <span className="status-dot" /> PREDICTED
        </span>
      </div>
      <div className="arrival-list">
        {rows.map((r) => (
          <div className="arrival-item" key={r.trip_id}>
            <span className="bus-icon">
              <BusFront size={18} />
            </span>
            <div>
              <strong>
                {data.network.stops.find((s) => s.id === r.stop_id)?.name}
              </strong>
              <small>
                {r.vehicle_id} ·{" "}
                {data.network.routes.find((t) => t.id === r.route_id)?.name}
              </small>
            </div>
            <div className="arrival-time">
              <strong>{clock(r.expected)}</strong>
              <small>
                {clock(r.earliest)}–{clock(r.latest)}
              </small>
            </div>
          </div>
        ))}
        {predictions.error ? (
          <p className="empty-copy">
            Arrival estimates unavailable. Move the time slider to retry.
          </p>
        ) : (
          !rows.length && (
            <p className="empty-copy">
              No moving vehicles at this instant. Move the playback slider.
            </p>
          )
        )}
      </div>
      <div className="panel-note">
        80% target interval · empirical coverage {data.eta.coverage}%
      </div>
    </section>
  );
}
function FeasibilityCard({ report }: { report: Feasibility }) {
  return (
    <section className="panel feasibility">
      <div className="panel-head">
        <h2>
          <ShieldCheck size={18} /> Feasibility checks
        </h2>
        <span className={`badge ${report.feasible ? "success" : "warning"}`}>
          {report.feasible ? "Passed" : "Issues found"}
        </span>
      </div>
      <div className="constraint-grid">
        {report.checked.map((c) => {
          const bad = report.violations.some((v) => v.constraint === c);
          return (
            <div key={c} className={bad ? "bad" : ""}>
              {bad ? <X size={15} /> : <CheckCircle2 size={15} />}
              <span>{c.replaceAll("_", " ")}</span>
            </div>
          );
        })}
      </div>
      {report.violations.length > 0 && (
        <div className="violations">
          {report.violations.map((v, i) => (
            <p key={i}>
              {v.trip_id}: {v.detail}
            </p>
          ))}
        </div>
      )}
      <div className="panel-note">
        {report.vehicles_used} existing vehicles · {report.trips_scheduled}{" "}
        scheduled trips
      </div>
    </section>
  );
}
function Comparison({ result }: { result: Optimization }) {
  return (
    <section className="panel comparison">
      <div className="panel-head">
        <div>
          <h2>One scenario. A fair comparison.</h2>
          <p>
            Same network, demand realization, fleet, disruption and seed{" "}
            {result.evaluation_seed}
          </p>
        </div>
        <span className="badge neutral">MEASURED RESULTS</span>
      </div>
      <div className="comparison-charts">
        {[
          ["average_wait", "p95_wait"],
          ["served", "unserved"],
        ].map((keys, i) => (
          <div key={i}>
            <p>
              {i === 0
                ? "Passenger queue time · minutes"
                : "Journey outcomes · passengers"}
            </p>
            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={result.comparison
                    .filter((c) => keys.includes(c.metric))
                    .map((c) => ({
                      name: metricNames[c.metric],
                      baseline: c.baseline,
                      candidate: c.candidate,
                    }))}
                  margin={{ left: -15, right: 15, top: 10 }}
                >
                  <CartesianGrid
                    strokeDasharray="4 4"
                    vertical={false}
                    stroke="#eceef2"
                  />
                  <XAxis
                    dataKey="name"
                    fontSize={9}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis fontSize={9} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar
                    isAnimationActive={false}
                    dataKey="baseline"
                    name="Published baseline"
                    fill="#c1c6d6"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={42}
                  />
                  <Bar
                    isAnimationActive={false}
                    dataKey="candidate"
                    name="Proposed plan"
                    fill="#8070df"
                    radius={[4, 4, 0, 0]}
                    maxBarSize={42}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 9 }} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Operational metric</th>
              <th>Published baseline</th>
              <th>Proposed plan</th>
              <th>Absolute change</th>
              <th>Outcome</th>
            </tr>
          </thead>
          <tbody>
            {result.comparison
              .filter((c) => c.metric !== "passengers")
              .map((c) => (
                <tr key={c.metric}>
                  <td>{metricNames[c.metric]}</td>
                  <td>{number(c.baseline, 2)}</td>
                  <td className="bold">{number(c.candidate, 2)}</td>
                  <td>
                    {c.delta > 0 ? "+" : ""}
                    {number(c.delta, 2)}
                  </td>
                  <td>
                    <span className={`outcome ${c.direction}`}>
                      {c.direction === "improved" ? (
                        <ArrowDownRight size={14} />
                      ) : c.direction === "regressed" ? (
                        <ArrowUpRight size={14} />
                      ) : null}
                      {c.improvement_percent !== null && c.delta !== 0
                        ? `${Math.abs(c.improvement_percent)}% ${c.direction === "improved" ? "better" : "worse"}`
                        : c.delta === 0
                          ? "Unchanged"
                          : "Trade-off"}
                    </span>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
function Fleet({ data }: { data: Dashboard }) {
  const [route, setRoute] = useState("all");
  return (
    <>
      <div className="vehicle-grid">
        {data.network.vehicles.map((v) => {
          const trips = data.timetable.filter((t) => t.vehicle_id === v.id);
          const events = data.simulation.events.filter(
            (e) => e.vehicle_id === v.id,
          );
          const breakdown = data.scenario.breakdown_vehicle === v.id;
          return (
            <div className="panel vehicle-card" key={v.id}>
              <div>
                <span className="vehicle-icon">
                  <BusFront size={24} />
                </span>
                <span
                  className={`badge ${breakdown ? "warning" : trips.length ? "success" : "neutral"}`}
                >
                  {breakdown
                    ? "Disrupted"
                    : trips.length
                      ? "Assigned"
                      : "Reserve"}
                </span>
              </div>
              <h2>
                {v.id} <small>{v.number}</small>
              </h2>
              <p>{v.capacity} passenger capacity · accessible</p>
              <div className="vehicle-facts">
                <span>
                  <strong>{trips.length}</strong> duties
                </span>
                <span>
                  <strong>
                    {Math.max(0, ...events.map((e) => e.occupancy))}
                  </strong>{" "}
                  peak onboard
                </span>
              </div>
              <small>
                Available {clock(v.available_from)}–{clock(v.available_until)} ·
                Depot S00
              </small>
            </div>
          );
        })}
      </div>
      <div className="panel">
        <div className="panel-head">
          <div>
            <h2>Published duties & departure windows</h2>
            <p>
              Actual arrivals reflect delays, cancellations and shared vehicle
              duties.
            </p>
          </div>
          <select
            aria-label="Filter timetable route"
            value={route}
            onChange={(e) => setRoute(e.target.value)}
          >
            <option value="all">All routes</option>
            {data.network.routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Trip / route</th>
                <th>Vehicle</th>
                <th>Departure</th>
                <th>Permitted window</th>
                <th>Planned finish</th>
                <th>Actual finish</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {data.timetable
                .filter((t) => route === "all" || t.route_id === route)
                .sort((a, b) => a.departure - b.departure)
                .map((t) => {
                  const events = data.simulation.events.filter(
                    (e) => e.trip_id === t.id,
                  );
                  const finish = events.find((e) => e.stop_index === 5);
                  return (
                    <tr key={t.id}>
                      <td>
                        <strong>{t.id}</strong>
                        <small>
                          {
                            data.network.routes.find((r) => r.id === t.route_id)
                              ?.name
                          }
                        </small>
                      </td>
                      <td>{t.vehicle_id}</td>
                      <td className="bold">{clock(t.departure)}</td>
                      <td>
                        {clock(t.earliest)}–{clock(t.latest)}
                      </td>
                      <td>{clock(t.scheduled_arrivals?.at(-1) || 0)}</td>
                      <td>{finish ? clock(finish.time) : "—"}</td>
                      <td>
                        <span
                          className={`badge ${!events.length ? "warning" : finish ? "success" : "neutral"}`}
                        >
                          {!events.length
                            ? "Cancelled"
                            : finish
                              ? "Completed"
                              : "In progress at cutoff"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
      <FeasibilityCard report={data.simulation.feasibility} />
    </>
  );
}
function Demand({ data }: { data: Dashboard }) {
  const [route, setRoute] = useState("all");
  const rows = data.demand.rows.filter(
    (r) => route === "all" || r.route_id === route,
  );
  return (
    <>
      <div className="stats-grid">
        <Stat
          label="Forecast accuracy"
          value={number(data.demand.mae, 2)}
          unit="MAE"
          icon={Activity}
          foot="Riders per origin / route / 15-min bin"
          tone="purple"
        />
        <Stat
          label="Weighted absolute error"
          value={data.demand.wape === null ? "—" : number(data.demand.wape, 1)}
          unit="%"
          icon={BarChart3}
          foot="Held-out arrivals, independent history"
          tone="blue"
        />
        <Stat
          label="High-pressure intervals"
          value={String(rows.filter((r) => r.category === "high").length)}
          unit="bins"
          icon={TriangleAlert}
          foot="Expected demand exceeds available seats"
          tone="amber"
        />
        <Stat
          label="Historical weekdays"
          value="12"
          unit="days"
          icon={Layers3}
          foot="Distinct historical and evaluation seeds"
          tone="purple"
        />
      </div>
      <div className="two-col">
        <DemandChart data={data} />
        <div className="panel padded">
          <h2>A forecast you can explain</h2>
          <p className="section-copy">{data.demand.assumptions}</p>
          <div className="risk-explainer">
            <span>
              <i className="risk-low" /> Low{" "}
              <small>≤ 80% of available seats</small>
            </span>
            <span>
              <i className="risk-medium" /> Medium{" "}
              <small>80–100% of available seats</small>
            </span>
            <span>
              <i className="risk-high" /> High{" "}
              <small>Demand exceeds seats</small>
            </span>
          </div>
          <div className="health-row">
            <span>Peak-period MAE</span>
            <strong>{data.demand.by_period.peak}</strong>
          </div>
          <div className="health-row">
            <span>Off-peak MAE</span>
            <strong>{data.demand.by_period.off_peak}</strong>
          </div>
        </div>
      </div>
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Stop-level capacity pressure</h2>
            <p>
              Expected arrivals / available seats · includes upstream occupancy
              estimates
            </p>
          </div>
          <select
            aria-label="Filter demand route"
            value={route}
            onChange={(e) => setRoute(e.target.value)}
          >
            <option value="all">All routes</option>
            {data.network.routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div className="table-scroll">
          <table className="heatmap">
            <thead>
              <tr>
                <th>Origin / direction</th>
                {Array.from({ length: 8 }, (_, i) => (
                  <th key={i}>{clock(i * 15)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from(
                new Set(rows.map((r) => `${r.stop_id}:${r.route_id}`)),
              ).map((key) => {
                const [stop, rid] = key.split(":");
                return (
                  <tr key={key}>
                    <td>
                      <strong>
                        {data.network.stops.find((s) => s.id === stop)?.name}
                      </strong>
                      <small>
                        {data.network.routes.find((r) => r.id === rid)?.name}
                      </small>
                    </td>
                    {Array.from({ length: 8 }, (_, i) => {
                      const r = rows.find(
                        (r) =>
                          r.stop_id === stop &&
                          r.route_id === rid &&
                          r.minute === i * 15,
                      );
                      return (
                        <td key={i}>
                          <div
                            className={`heat-cell risk-${r?.category}`}
                            title={
                              r
                                ? `Range ${r.low}–${r.high}; actual ${r.actual}; predicted unmet ${r.unmet}`
                                : ""
                            }
                          >
                            {number(r?.expected || 0)}{" "}
                            <span>/ {r?.capacity || 0}</span>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
const disruptionSchema = z
  .object({
    demand_multiplier: z.number().min(0.1).max(5),
    traffic_factor: z.number().min(1).max(3),
    disruption_start: z.number().min(0).max(120),
    disruption_end: z.number().positive().max(140),
  })
  .refine((v) => v.disruption_end > v.disruption_start, {
    message: "End time must be later than start time.",
  });
function Disruptions({
  data,
  onRun,
  onOptimize,
}: {
  data: Dashboard;
  onRun: (d: Dashboard) => void;
  onOptimize: () => void;
}) {
  const [demand, setDemand] = useState(data.scenario.demand_multiplier);
  const [traffic, setTraffic] = useState(data.scenario.traffic_factor);
  const [vehicle, setVehicle] = useState(data.scenario.breakdown_vehicle || "");
  const [route, setRoute] = useState(data.scenario.affected_route);
  const [start, setStart] = useState(data.scenario.disruption_start);
  const [end, setEnd] = useState(data.scenario.disruption_end);
  const [error, setError] = useState("");
  const run = useMutation({
    mutationFn: () =>
      api<Dashboard>("simulations", {
        scenario_id: data.scenario.id,
        demand_multiplier: demand,
        traffic_factor: traffic,
        breakdown_vehicle: vehicle || null,
        affected_route: route,
        disruption_start: start,
        disruption_end: end,
      }),
    onSuccess: onRun,
  });
  return (
    <>
      <div className="disruption-layout">
        <section className="panel padded">
          <div className="eyebrow">SCENARIO CONTROLS</div>
          <h2>Put your network to the test.</h2>
          <p className="section-copy">
            These controls change the actual simulation inputs. Run a new
            experiment, then search for a feasible recovery.
          </p>
          <div className="form-stack">
            <label>
              Demand multiplier <strong>{demand.toFixed(1)}×</strong>
              <input
                type="range"
                min=".1"
                max="5"
                step=".1"
                value={demand}
                onChange={(e) => setDemand(Number(e.target.value))}
              />
            </label>
            <label>
              Travel time multiplier <strong>{traffic.toFixed(2)}×</strong>
              <input
                type="range"
                min="1"
                max="3"
                step=".05"
                value={traffic}
                onChange={(e) => setTraffic(Number(e.target.value))}
              />
            </label>
            <label>
              Affected route
              <select value={route} onChange={(e) => setRoute(e.target.value)}>
                {data.network.routes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Vehicle breakdown
              <select
                aria-label="Vehicle breakdown"
                value={vehicle}
                onChange={(e) => setVehicle(e.target.value)}
              >
                <option value="">No vehicle breakdown</option>
                {data.network.vehicles.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.id} · {v.capacity} seats
                  </option>
                ))}
              </select>
            </label>
            <div className="two-col form-times">
              <label>
                Start · minutes after 08:00
                <input
                  type="number"
                  value={start}
                  min="0"
                  max="120"
                  onChange={(e) => setStart(Number(e.target.value))}
                />
              </label>
              <label>
                End · minutes after 08:00
                <input
                  type="number"
                  value={end}
                  min="1"
                  max="140"
                  onChange={(e) => setEnd(Number(e.target.value))}
                />
              </label>
            </div>
          </div>
          <button
            className="primary-button full-width"
            disabled={run.isPending}
            onClick={() => {
              const parsed = disruptionSchema.safeParse({
                demand_multiplier: demand,
                traffic_factor: traffic,
                disruption_start: start,
                disruption_end: end,
              });
              if (!parsed.success) {
                setError(parsed.error.issues[0].message);
                return;
              }
              setError("");
              run.mutate();
            }}
          >
            {run.isPending ? (
              <LoaderCircle className="spin" size={16} />
            ) : (
              <Zap size={16} />
            )}{" "}
            {run.isPending ? "Simulating disruption…" : "Run simulation"}
          </button>
          {(error || run.error) && (
            <ErrorBox message={error || run.error?.message || ""} />
          )}
          <p className="micro-copy">
            Known breakdowns prevent dispatch across the outage window; this
            demo does not simulate roadside evacuation.
          </p>
        </section>
        <div>
          <div className="panel padded">
            <span className="badge neutral">LATEST COMPUTED RUN</span>
            <h2 className="mt">{data.scenario.name}</h2>
            <div className="baseline-facts">
              <div>
                <strong>{data.simulation.metrics.unserved}</strong>
                <span>unserved passengers</span>
              </div>
              <div>
                <strong>{data.simulation.metrics.average_wait}</strong>
                <span>minutes average wait</span>
              </div>
            </div>
            <p className="section-copy">
              {data.scenario.demand_multiplier}× demand ·{" "}
              {data.scenario.traffic_factor}× travel time on{" "}
              {data.scenario.affected_route}
              <br />
              {data.scenario.breakdown_vehicle
                ? `${data.scenario.breakdown_vehicle} unavailable ${clock(data.scenario.disruption_start)}–${clock(data.scenario.disruption_end)}`
                : "No vehicle outage"}
            </p>
            {run.isSuccess && (
              <div className="success-message">
                <CheckCircle2 size={16} /> Simulation saved. Results are ready.
              </div>
            )}
            <button
              className="secondary-button full-width"
              onClick={onOptimize}
            >
              <Sparkles size={16} /> Find a recovery plan{" "}
              <ArrowRight size={16} />
            </button>
          </div>
          <Alerts data={data} />
        </div>
      </div>
    </>
  );
}
function Reports({
  data,
  result,
  onOpen,
}: {
  data: Dashboard;
  result: Optimization | null;
  onOpen: (r: Optimization) => void;
}) {
  const history = useQuery({
    queryKey: ["history"],
    queryFn: () => api<History[]>("optimizations"),
  });
  const open = useMutation({
    mutationFn: (id: string) => api<Optimization>(`optimizations/${id}`),
    onSuccess: onOpen,
  });
  const chart = data.eta.rows.slice(0, 45).map((r, i) => ({
    sample: i + 1,
    predicted: r.expected - r.prediction_time,
    actual: (r.actual || 0) - r.prediction_time,
  }));
  return (
    <>
      <div className="report-toolbar">
        <p>
          <ShieldCheck size={16} /> Every number is calculated from a saved or
          reproducible simulation.
        </p>
        <button className="secondary-button" onClick={() => window.print()}>
          <Printer size={16} /> Print report / PDF
        </button>
      </div>
      <div className="stats-grid">
        <Stat
          label="ETA mean absolute error"
          value={number(data.eta.mae, 2)}
          unit="min"
          icon={Clock3}
          foot={`${data.eta.sample_count} held-out stop predictions`}
          tone="purple"
        />
        <Stat
          label="Prediction interval coverage"
          value={number(data.eta.coverage, 1)}
          unit="%"
          icon={ShieldCheck}
          foot="Empirical coverage · 80% target"
          tone="blue"
        />
        <Stat
          label="90th percentile error"
          value={number(data.eta.p90_absolute_error, 2)}
          unit="min"
          icon={Activity}
          foot={`Median absolute error · ${data.eta.median_absolute_error} min`}
          tone="amber"
        />
        <Stat
          label="Average interval width"
          value={number(data.eta.average_width, 2)}
          unit="min"
          icon={Layers3}
          foot="Calibrated on four separate days"
          tone="purple"
        />
      </div>
      <div className="two-col">
        <section className="panel">
          <div className="panel-head">
            <div>
              <h2>Predicted vs actual arrival</h2>
              <p>Minutes remaining · first 45 held-out predictions</p>
            </div>
          </div>
          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={chart}
                margin={{ left: -15, right: 20, top: 10 }}
              >
                <CartesianGrid strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="sample" fontSize={10} />
                <YAxis fontSize={10} />
                <Tooltip />
                <Line
                  isAnimationActive={false}
                  dataKey="predicted"
                  name="Predicted"
                  stroke="#7169e7"
                  dot={false}
                />
                <Line
                  isAnimationActive={false}
                  dataKey="actual"
                  name="Ground truth"
                  stroke="#15a58b"
                  dot={false}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="panel padded">
          <h2>How to read the evidence</h2>
          <p className="section-copy">{data.eta.assumptions}</p>
          <p className="section-copy">
            Waiting time includes unfinished riders until the horizon. A served
            passenger must reach their final destination. Capacity pressure
            counts riders left in queues, never passengers above the vehicle
            limit.
          </p>
          <a
            className="text-link"
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
          >
            View versioned API documentation <ArrowUpRight size={14} />
          </a>
        </section>
      </div>
      {result && <Comparison result={result} />}
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Scenario robustness</h2>
            <p>
              Latest saved result per scenario · improvements and regressions
              remain visible
            </p>
          </div>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Scenario</th>
                <th>Completed journeys</th>
                <th>Mean wait · minutes</th>
                <th>Missed connections</th>
                <th>Candidate constraints</th>
              </tr>
            </thead>
            <tbody>
              {history.data
                ?.filter(
                  (h, i, all) =>
                    all.findIndex((x) => x.scenario_id === h.scenario_id) === i,
                )
                .map((h) => (
                  <tr key={h.id}>
                    <td className="bold">{h.scenario_id}</td>
                    <td>
                      {h.baseline.served} → {h.candidate?.served ?? "—"}
                    </td>
                    <td>
                      {number(h.baseline.average_wait, 2)} →{" "}
                      {h.candidate ? number(h.candidate.average_wait, 2) : "—"}
                    </td>
                    <td>
                      {h.baseline.missed_connections} →{" "}
                      {h.candidate?.missed_connections ?? "—"}
                    </td>
                    <td>
                      <span
                        className={`badge ${h.candidate?.feasibility_violations === 0 ? "success" : "neutral"}`}
                      >
                        {h.candidate
                          ? `${h.candidate.feasibility_violations} violations`
                          : "No candidate"}
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {!history.data?.length && (
            <p className="empty-copy">
              Save optimization runs across scenarios to compare recovery
              outcomes here.
            </p>
          )}
        </div>
      </section>
      <section className="panel">
        <div className="panel-head">
          <div>
            <h2>Experiment history</h2>
            <p>
              Immutable inputs and outcomes · selected scenario from the latest
              30 runs
            </p>
          </div>
          <button
            className="icon-button"
            aria-label="Refresh experiment history"
            onClick={() => history.refetch()}
          >
            <RefreshCw size={16} />
          </button>
        </div>
        {(history.error || open.error) && (
          <ErrorBox message={(history.error || open.error)?.message || ""} />
        )}
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Run / scenario</th>
                <th>Service rate</th>
                <th>Average wait</th>
                <th>Status</th>
                <th>Report</th>
              </tr>
            </thead>
            <tbody>
              {history.data
                ?.filter((h) => h.scenario_id === data.scenario.id)
                .map((h) => (
                  <tr key={h.id}>
                    <td>
                      <button
                        className="table-link"
                        onClick={() => open.mutate(h.id)}
                      >
                        {h.scenario_id} · {h.id.slice(0, 8)}
                      </button>
                      <small>{new Date(h.created_at).toLocaleString()}</small>
                    </td>
                    <td>
                      {number(h.baseline.service_rate, 1)}% →{" "}
                      {h.candidate
                        ? `${number(h.candidate.service_rate, 1)}%`
                        : "—"}
                    </td>
                    <td>
                      {number(h.baseline.average_wait, 1)} →{" "}
                      {h.candidate ? number(h.candidate.average_wait, 1) : "—"}{" "}
                      min
                    </td>
                    <td>
                      <span className="badge neutral">
                        {h.status.replaceAll("_", " ").toLowerCase()}
                      </span>
                    </td>
                    <td>
                      <a href={`/api/v1/reports/${h.id}?format=csv`} download>
                        CSV
                      </a>
                      <span className="divider"> / </span>
                      <a href={`/api/v1/reports/${h.id}?format=json`} download>
                        JSON
                      </a>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {!history.data?.some((h) => h.scenario_id === data.scenario.id) && (
            <p className="empty-copy">
              Run an optimization to create your first saved experiment.
            </p>
          )}
        </div>
      </section>
      <FeasibilityCard report={data.simulation.feasibility} />
    </>
  );
}
