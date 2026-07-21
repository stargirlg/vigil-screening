from app.db.database import engine, SessionLocal, Base
from app.models import User, Customer, Alert, AuditLog, SanctionEntry  # noqa
from app.models.user import UserRole
from app.auth.password import hash_password
from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


def create_tables():
    log.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    log.info("Tables created.")


def seed_default_users():
    db = SessionLocal()

    try:
        users = [
            (
                settings.ADMIN_EMAIL,
                settings.ADMIN_PASSWORD,
                UserRole.ADMIN,
                "VIGIL Administrator",
            ),
            (
                "analyst@vigil.com",
                "Analyst@123!",
                UserRole.ANALYST,
                "AML Analyst",
            ),
            (
                "co@vigil.com",
                "CO@123456!",
                UserRole.CO,
                "Compliance Officer",
            ),
        ]

        for email, password, role, full_name in users:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                log.info(f"{email} already exists — skipping.")
                continue

            db.add(
                User(
                    email=email,
                    full_name=full_name,
                    hashed_password=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )
            log.info(f"Created user: {email}")

        db.commit()
        log.info("Default users seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def init():
    create_tables()
    seed_default_users()
    log.info("VIGIL DB initialization complete.")

if __name__ == "__main__":
    init()