from db.database import Base, engine
from db import models  # noqa: F401  registers models with Base.metadata


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created (or already exist).")


if __name__ == "__main__":
    init_db()
