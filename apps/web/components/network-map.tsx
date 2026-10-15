"use client";
import { useState } from "react";
import { Maximize2, Pause, Play, MapPin, BusFront } from "lucide-react";
import type { Dashboard, GPS } from "@/lib/api";
import { clock } from "@/lib/api";
export default function NetworkMap({
  data,
  minute,
  setMinute,
  playing,
  setPlaying,
  large = false,
}: {
  data: Dashboard;
  minute: number;
  setMinute: (n: number) => void;
  playing: boolean;
  setPlaying: (v: boolean) => void;
  large?: boolean;
}) {
  const [selected, setSelected] = useState("S00");
  const [hidden, setHidden] = useState<string[]>([]);
  const net = data.network;
  const byId = Object.fromEntries(net.stops.map((s) => [s.id, s]));
  const visible = net.routes.filter((r) => !hidden.includes(r.id));
  const current: Record<string, GPS> = {};
  for (const g of data.simulation.gps) {
    if (g.timestamp <= minute && minute - g.timestamp < 1)
      current[g.vehicle_id] = g;
  }
  const stop = byId[selected];
  const vehicle = net.vehicles.find((v) => v.id === selected);
  const event = vehicle
    ? data.simulation.events
        .filter((e) => e.vehicle_id === vehicle.id && e.time <= minute)
        .at(-1)
    : null;
  return (
    <section className={`panel map-panel ${large ? "map-large" : ""}`}>
      <div className="panel-head">
        <div>
          <h2>
            Campus network{" "}
            <span className="live-label">
              <span /> SIMULATED
            </span>
          </h2>
          <p>
            Meridian University · {net.stops.length} stops · offline network map
          </p>
        </div>
        <button
          className="icon-button"
          aria-label="Expand campus map"
          onClick={() =>
            document.getElementById("campus-map")?.requestFullscreen?.()
          }
        >
          <Maximize2 size={17} />
        </button>
      </div>
      <div className="map-stage" id="campus-map">
        <svg
          viewBox="50 30 880 680"
          role="img"
          aria-label="Interactive campus routes and simulated vehicle positions"
        >
          <defs>
            <pattern
              id="grid"
              width="32"
              height="32"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 32 0 L 0 0 0 32"
                fill="none"
                stroke="#e6e9e7"
                strokeWidth=".7"
              />
            </pattern>
            <filter id="shadow">
              <feDropShadow dx="0" dy="3" stdDeviation="4" floodOpacity=".12" />
            </filter>
          </defs>
          <rect x="0" y="0" width="1000" height="750" fill="#f5f7f4" />
          <rect x="0" y="0" width="1000" height="750" fill="url(#grid)" />
          <path
            d="M68 90 Q280 230 320 320 T400 710"
            stroke="#deece6"
            strokeWidth="52"
            fill="none"
          />
          <path
            d="M70 560 Q270 550 460 240 T920 85"
            stroke="#e4ecef"
            strokeWidth="28"
            fill="none"
          />
          {[
            { x: 230, y: 220, w: 90, h: 75 },
            { x: 290, y: 340, w: 75, h: 54 },
            { x: 510, y: 280, w: 75, h: 65 },
            { x: 640, y: 250, w: 78, h: 60 },
            { x: 580, y: 550, w: 55, h: 50 },
            { x: 720, y: 430, w: 67, h: 50 },
            { x: 350, y: 130, w: 75, h: 60 },
          ].map((b, i) => (
            <g key={i}>
              <rect
                {...{ x: b.x, y: b.y, width: b.w, height: b.h }}
                rx="10"
                fill="#e9ece6"
                stroke="#dce1d9"
              />
              <path
                d={`M${b.x + 10} ${b.y + 12}h${b.w - 20}`}
                stroke="#f5f7f4"
                strokeWidth="5"
              />
            </g>
          ))}
          <text x="280" y="86" className="map-area">
            NORTH CAMPUS
          </text>
          <text x="640" y="72" className="map-area">
            RESEARCH DISTRICT
          </text>
          <text x="480" y="697" className="map-area">
            SOUTH CAMPUS
          </text>
          {visible.map((r) => (
            <g key={r.id}>
              <polyline
                points={r.stops
                  .map((id) => `${byId[id].x},${byId[id].y}`)
                  .join(" ")}
                fill="none"
                stroke="white"
                strokeWidth="13"
                strokeLinejoin="round"
              />
              <polyline
                points={r.stops
                  .map((id) => `${byId[id].x},${byId[id].y}`)
                  .join(" ")}
                fill="none"
                stroke={r.color}
                strokeWidth="5"
                strokeLinejoin="round"
                opacity=".85"
              />
            </g>
          ))}
          {net.stops
            .filter((s) => visible.some((r) => r.stops.includes(s.id)))
            .map((s) => (
              <g
                key={s.id}
                role="button"
                tabIndex={0}
                aria-label={`Inspect ${s.name}`}
                onClick={() => setSelected(s.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") setSelected(s.id);
                }}
                className="map-stop"
              >
                {s.id === selected && (
                  <circle
                    cx={s.x}
                    cy={s.y}
                    r="19"
                    fill="#7169e7"
                    opacity=".13"
                  />
                )}
                <circle
                  cx={s.x}
                  cy={s.y}
                  r={s.id === "S00" ? 10 : 6}
                  fill="white"
                  stroke={s.id === "S00" ? "#334155" : "#6b7385"}
                  strokeWidth="3"
                />
                <text
                  x={s.x}
                  y={s.y - 17}
                  textAnchor="middle"
                  className="stop-label"
                >
                  {s.name}
                </text>
              </g>
            ))}
          {Object.values(current)
            .filter((g) =>
              visible.some((r) =>
                data.simulation.plan.trips.some(
                  (t) => t.id === g.trip_id && t.route_id === r.id,
                ),
              ),
            )
            .map((g) => {
              const x = (g.longitude - 77.56) / 0.000012,
                y = (12.98 - g.latitude) / 0.000012;
              const trip = data.simulation.plan.trips.find(
                (t) => t.id === g.trip_id,
              );
              const color = net.routes.find(
                (r) => r.id === trip?.route_id,
              )?.color;
              return (
                <g
                  key={g.vehicle_id}
                  tabIndex={0}
                  role="button"
                  aria-label={`Inspect vehicle ${g.vehicle_id}`}
                  onClick={() => setSelected(g.vehicle_id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") setSelected(g.vehicle_id);
                  }}
                  style={{ cursor: "pointer" }}
                  filter="url(#shadow)"
                >
                  <rect
                    x={x - 17}
                    y={y - 13}
                    width="34"
                    height="26"
                    rx="8"
                    fill={color}
                  />
                  <text
                    x={x}
                    y={y + 4}
                    fill="white"
                    textAnchor="middle"
                    fontSize="10"
                    fontWeight="700"
                  >
                    {g.vehicle_id}
                  </text>
                </g>
              );
            })}
        </svg>
        <div className="map-detail">
          {vehicle ? (
            <>
              <BusFront size={16} />
              <div>
                <strong>
                  {vehicle.id} · {vehicle.number}
                </strong>
                <small>
                  {event
                    ? `${event.occupancy} / ${vehicle.capacity} onboard`
                    : "Idle / no active GPS"}{" "}
                  · capacity {vehicle.capacity}
                </small>
              </div>
            </>
          ) : (
            <>
              <MapPin size={16} />
              <div>
                <strong>{stop?.name}</strong>
                <small>{stop?.kind} · wheelchair accessible</small>
              </div>
            </>
          )}
        </div>
        <div className="map-compass">
          N<span>↑</span>
        </div>
      </div>
      <div className="map-legend">
        {net.routes.map((r) => (
          <button
            key={r.id}
            onClick={() =>
              setHidden((h) =>
                h.includes(r.id) ? h.filter((x) => x !== r.id) : [...h, r.id],
              )
            }
            className={hidden.includes(r.id) ? "muted-route" : ""}
          >
            <span style={{ background: r.color }} />
            {r.name}
          </button>
        ))}
        <small>Fictional geography</small>
      </div>
      <div className="playback">
        <button
          className="play-button"
          aria-label={playing ? "Pause playback" : "Play simulation"}
          onClick={() => setPlaying(!playing)}
        >
          {playing ? <Pause size={15} /> : <Play size={15} />}
        </button>
        <strong>{clock(minute)}</strong>
        <input
          aria-label="Simulation time"
          type="range"
          min="0"
          max="120"
          step=".5"
          value={minute}
          onChange={(e) => setMinute(Number(e.target.value))}
        />
        <span>10:00 IST</span>
        <span className="badge neutral">×30</span>
      </div>
    </section>
  );
}
