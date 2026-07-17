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


def seed_admin():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(
            User.email == settings.ADMIN_EMAIL
        ).first()
        if existing:
            log.info("Admin already exists — skipping.")
            return

        admin = User(
            email=settings.ADMIN_EMAIL,
            full_name="VIGIL Administrator",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        log.info(f"Admin seeded: {settings.ADMIN_EMAIL}")
    finally:
        db.close()


def init():
    create_tables()
    seed_admin()
    log.info("VIGIL DB initialization complete.")


if __name__ == "__main__":
    init()