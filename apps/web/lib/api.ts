import type { components } from "./generated";
import { z } from "zod";
export const scenarioSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string(),
  challenge: z.string(),
  seed: z.number(),
  demand_multiplier: z.number(),
  traffic_factor: z.number(),
  breakdown_vehicle: z.string().nullable(),
  affected_route: z.string(),
  disruption_start: z.number(),
  disruption_end: z.number(),
  horizon: z.number(),
  version: z.string(),
  epoch_utc: z.string(),
  timezone: z.string(),
});
export type Scenario = z.infer<typeof scenarioSchema>;
// Core domain types are generated from FastAPI's OpenAPI response schemas.
export type Stop = components["schemas"]["Stop"];
export type Route = components["schemas"]["Route"];
export type Vehicle = components["schemas"]["Vehicle"];
export type Trip = components["schemas"]["Trip"] & {
  scheduled_arrivals?: number[];
};
export type Plan = components["schemas"]["Plan"];
export type Metrics = components["schemas"]["Metrics"];
export type Feasibility = components["schemas"]["Feasibility"];
export type GPS = components["schemas"]["GPS"];
export type StopEvent = components["schemas"]["StopEvent"];
export type Simulation = components["schemas"]["Simulation"];
export type Prediction = components["schemas"]["ArrivalPrediction"];
export type DemandRow = components["schemas"]["DemandRow"];
export type Dashboard = components["schemas"]["DashboardResponse"];
export type Comparison = components["schemas"]["Comparison"];
export type Optimization = components["schemas"]["OptimizationResponse"];
export type History = components["schemas"]["HistoryRow"];
export async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers:
      body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      data.error?.message || `Request failed (${response.status})`,
    );
  return data as T;
}
export function clock(minute: number) {
  const t = Math.round(480 + minute);
  return `${String(Math.floor(t / 60)).padStart(2, "0")}:${String(t % 60).padStart(2, "0")}`;
}
export function number(n: number, decimals = 0) {
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}
export const metricNames: Record<keyof Metrics, string> = {
  passengers: "Passenger demand",
  served: "Completed journeys",
  unserved: "Unserved passengers",
  service_rate: "Passenger service rate",
  average_wait: "Average wait",
  p95_wait: "95th percentile wait",
  missed_connections: "Missed connections",
  successful_connections: "Successful connections",
  fleet_utilization: "Fleet utilization",
  operating_minutes: "Operating minutes",
  total_trip_delay: "Total trip delay",
  capacity_violations: "Capacity violations",
  feasibility_violations: "Feasibility violations",
};
