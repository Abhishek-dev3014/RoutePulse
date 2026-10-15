from app.persistence import seed_database

seed_database()
print("Demo entities loaded (idempotent; existing experiments retained).")
