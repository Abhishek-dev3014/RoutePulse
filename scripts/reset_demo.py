"""Explicit seed reset; retains immutable experiments and their inputs."""

from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.persistence import Entity, engine, seed_database

with Session(engine) as db, db.begin():
    db.execute(delete(Entity))
seed_database()
print("Demo entities reset. Experiment and decision history retained.")
