import logging

from sqlalchemy import or_, select

from app.config import get_settings
from app.db.session import SessionLocal
from app.models.user import User
from app.security.password import hash_password

logger = logging.getLogger(__name__)


def seed_admin_user() -> None:
    settings = get_settings()
    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(or_(User.username == settings.admin_username, User.email == settings.admin_email))
        )
        if existing_user:
            logger.info("seed admin user already exists")
            return

        db.add(
            User(
                username=settings.admin_username,
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
                display_name=settings.admin_display_name,
                role="admin",
                is_active=True,
            )
        )
        db.commit()
        logger.info("seed admin user created")
