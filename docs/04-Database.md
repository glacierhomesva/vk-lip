# Database

The database layer uses SQLAlchemy for ORM modeling and connection management.

- `backend/app/db/session.py`: SQLAlchemy engine and session factory.
- `backend/app/models/`: declarative database models.
- `DATABASE_URL`: configured via `.env` or `.env.example`.
