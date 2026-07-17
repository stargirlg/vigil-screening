from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TYPE risklevel ADD VALUE IF NOT EXISTS 'MEDIUM'"))
    conn.execute(text("ALTER TYPE risklevel ADD VALUE IF NOT EXISTS 'CRITICAL'"))
    conn.commit()
    print("Risk levels updated: LOW / MEDIUM / HIGH / CRITICAL")