"""SQLAlchemy storage: versioned entity documents and immutable experiment snapshots."""

import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, DateTime, ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Entity(Base):
    __tablename__ = "entities"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, default="meridian-demo")
    kind: Mapped[str] = mapped_column(String, index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, default="meridian-demo")
    kind: Mapped[str] = mapped_column(String, index=True)
    scenario_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    payload: Mapped[dict] = mapped_column(JSON)


class Decision(Base):
    __tablename__ = "decisions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.id"), index=True)
    scenario_id: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./routepulse.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)


def seed_database():
    from .seed import baseline, network, scenarios

    net = network()
    with Session(engine) as db, db.begin():
        items = [("network", "network-v1", net.model_dump()), ("plan", "published-v1", baseline().model_dump())]
        for kind, entities in [
            ("stop", net.stops),
            ("route", net.routes),
            ("vehicle", net.vehicles),
            ("scenario", scenarios()),
            ("trip", baseline().trips),
        ]:
            items.extend((kind, e.id, e.model_dump()) for e in entities)
        for kind, identity, payload in items:
            if db.get(Entity, f"{kind}:{identity}") is None:
                db.add(Entity(id=f"{kind}:{identity}", kind=kind, payload=payload))


def save_run(kind: str, scenario_id: str, payload: dict) -> dict:
    identity = str(uuid.uuid4())
    stamp = datetime.now(timezone.utc)
    body = {**payload, "id": identity, "created_at": stamp.isoformat()}
    with Session(engine) as db, db.begin():
        db.add(Run(id=identity, kind=kind, scenario_id=scenario_id, created_at=stamp, payload=body))
    return body


def get_run(identity: str) -> dict | None:
    with Session(engine) as db:
        row = db.get(Run, identity)
        if not row:
            return None
        result = dict(row.payload)
        decision = db.scalar(select(Decision).where(Decision.run_id == identity).order_by(Decision.created_at.desc()))
        if decision:
            result["decision"] = decision.value
        return result


def history() -> list[dict]:
    with Session(engine) as db:
        rows = db.scalars(select(Run).where(Run.kind == "optimization").order_by(Run.created_at.desc()).limit(30)).all()
        return [
            dict(
                id=r.id,
                scenario_id=r.scenario_id,
                created_at=(
                    r.created_at if r.created_at.tzinfo else r.created_at.replace(tzinfo=timezone.utc)
                ).isoformat(),
                status=r.payload["status"],
                baseline=r.payload["baseline"]["metrics"],
                candidate=r.payload["candidate"]["metrics"] if r.payload["candidate"] else None,
            )
            for r in rows
        ]


def decide(identity: str, value: str):
    with Session(engine) as db, db.begin():
        run = db.get(Run, identity)
        db.add(Decision(id=str(uuid.uuid4()), run_id=identity, scenario_id=run.scenario_id, value=value))


def active(sc: dict) -> dict | None:
    with Session(engine) as db:
        seen = set()
        for row in db.scalars(
            select(Decision).where(Decision.scenario_id == sc["id"]).order_by(Decision.created_at.desc())
        ):
            if row.run_id in seen:
                continue
            seen.add(row.run_id)
            run = db.get(Run, row.run_id)
            if run.payload["scenario"] == sc and row.value == "accepted":
                return {"run_id": run.id, "plan": run.payload["candidate"]["plan"]}
    return None


def validation_for(identity: str, protocol: str) -> dict | None:
    with Session(engine) as db:
        # Store source identity in the indexed scenario_id column for this run kind.
        rows = db.scalars(
            select(Run).where(Run.kind == "validation", Run.scenario_id == identity).order_by(Run.created_at.desc())
        )
        for row in rows:
            if row.payload.get("protocol_version") == protocol:
                return dict(row.payload)
    return None
