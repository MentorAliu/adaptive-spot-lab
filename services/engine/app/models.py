from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """The metadata Alembic's ``env.py`` names. The schema is written by hand in each migration; no model is mapped."""
