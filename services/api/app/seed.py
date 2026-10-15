"""Fictional, connected campus. No coordinates describe a verified campus."""

from .domain import Edge, Network, Plan, Route, Scenario, Stop, Trip, Vehicle


def network() -> Network:
    specs = [
        ("Transit Commons", 460, 320, "interchange"),
        ("North Residences", 180, 120, "residence"),
        ("West Residences", 140, 300, "residence"),
        ("Academic Quarter", 250, 460, "academic"),
        ("Central Library", 410, 480, "academic"),
        ("Administration", 580, 180, "campus"),
        ("Research Park", 730, 120, "academic"),
        ("Innovation Center", 810, 290, "academic"),
        ("Medical Center", 650, 400, "campus"),
        ("South Parking", 490, 640, "parking"),
        ("Sports Complex", 710, 620, "campus"),
        ("Auditorium", 840, 500, "event"),
        ("Food Court", 590, 510, "campus"),
    ]
    stops = [
        Stop(id=f"S{i:02}", name=n, x=x, y=y, kind=k, latitude=12.98 - y * 0.000012, longitude=77.56 + x * 0.000012)
        for i, (n, x, y, k) in enumerate(specs)
    ]
    routes = [
        Route(id="R1", name="Residence Loop", color="#5b66e8", stops=["S00", "S01", "S02", "S03", "S04", "S00"]),
        Route(id="R2", name="Research Express", color="#15a58b", stops=["S00", "S05", "S06", "S07", "S08", "S00"]),
        Route(id="R3", name="Campus Connector", color="#e6a347", stops=["S00", "S09", "S10", "S11", "S12", "S00"]),
    ]
    by_id = {s.id: s for s in stops}
    edges = []
    for r in routes:
        for a, b in zip(r.stops, r.stops[1:]):
            distance = ((by_id[a].x - by_id[b].x) ** 2 + (by_id[a].y - by_id[b].y) ** 2) ** 0.5 * 0.0034
            edges.append(
                Edge(origin=a, destination=b, distance_km=round(distance, 3), minutes=round(distance / 18 * 60, 3))
            )
    vehicles = [
        Vehicle(id=f"V{i + 1:02}", number=f"MP-{101 + i}", capacity=c)
        for i, c in enumerate([22, 26, 32, 36, 28, 30, 45])
    ]
    return Network(stops=stops, routes=routes, edges=edges, vehicles=vehicles)


def baseline() -> Plan:
    trips = []
    for ri in range(3):
        for i in range(7):
            dep = 8 + i * 15 + ri * 2
            trips.append(
                Trip(
                    id=f"T{ri + 1}{i + 1:02}",
                    route_id=f"R{ri + 1}",
                    vehicle_id=f"V{ri * 2 + i % 2 + 1:02}",
                    departure=dep,
                    earliest=dep - 4,
                    latest=dep + 4,
                )
            )
    return Plan(id="published-v1", trips=trips)


def scenarios() -> list[Scenario]:
    return [
        Scenario(
            id="normal",
            name="Normal Campus Operations",
            description="A typical weekday with steady campus travel.",
            challenge="Maintain dependable service with a reserve vehicle.",
            seed=4101,
        ),
        Scenario(
            id="rush",
            name="Morning Rush Hour",
            description="Residence departures build before the first lecture.",
            challenge="Heavy residence queues and tight research transfers.",
            seed=4102,
            demand_multiplier=1.9,
        ),
        Scenario(
            id="breakdown",
            name="Vehicle Breakdown",
            description="V01 is out of service from 08:20 to 09:30.",
            challenge="Recover disrupted trips using the existing fleet.",
            seed=4103,
            demand_multiplier=1.5,
            breakdown_vehicle="V01",
        ),
        Scenario(
            id="traffic",
            name="Traffic Delay",
            description="Road works slow the Residence Loop by 65%.",
            challenge="Restore headways without overlapping vehicle duties.",
            seed=4104,
            traffic_factor=1.65,
            demand_multiplier=1.3,
        ),
        Scenario(
            id="event",
            name="Campus Event Demand Surge",
            description="An auditorium event draws a concentrated arrival wave.",
            challenge="Meet temporary demand on the Campus Connector.",
            seed=4105,
            demand_multiplier=1.4,
        ),
    ]
