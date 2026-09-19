from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Every model in this project inherits from this.

    Deliberately kept model-free: Alembic's env.py and app/models/__init__.py
    are responsible for importing concrete models so they register on
    Base.metadata, which avoids circular imports between this module and
    the models that depend on it.
    """
    pass