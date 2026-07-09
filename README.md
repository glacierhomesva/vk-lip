# vk-lip

vk-lip is a modular project scaffold for a backend-first application. The repository includes backend services, documentation, and placeholders for frontend, database, scripts, tests, and data.

## Repository structure

- `backend/`: Python backend service built with FastAPI and SQLAlchemy.
- `docs/`: Product vision, requirements, architecture, and database documentation.
- `frontend/`: Placeholder for frontend assets and implementation.
- `database/`: Database and migration-related files.
- `scripts/`: Automation and helper scripts.
- `tests/`: Unit and integration tests.
- `data/`: Data assets and sample datasets.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install backend dependencies:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```
3. Start the backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Production deployment (always-on)

Use the included deployment files to run the app continuously without local terminal sessions.

### Backend on Render

1. Create a new Web Service in Render and connect this repository.
2. Render will auto-detect `render.yaml`.
3. Set environment variables in Render:
   - `DATABASE_URL` (Supabase/Postgres connection string)
   - `CORS_ORIGINS` (comma-separated frontend origins, for example `https://vk-lip.vercel.app`)
4. Deploy. The backend runs with Gunicorn + Uvicorn workers and auto-applies migrations.

### Scheduled data sync on Render Cron

The repository includes two cron jobs in `render.yaml`:

1. `vk-lip-sync-nightly` at `0 6 * * *` (UTC)
   - datasets: `parcels owners assessments property_types`
2. `vk-lip-sync-weekly` at `30 6 * * 0` (UTC)
   - datasets: `boundary_details`

Each sync run uses a PostgreSQL advisory lock (`--job-name ...`) to prevent overlapping executions.
If a previous run is still active, the new run exits safely.

Set all source endpoint env vars for the cron services as needed:

- `SOURCE_PARCELS_URL`
- `SOURCE_OWNERS_URL`
- `SOURCE_ASSESSMENTS_URL`
- `SOURCE_PROPERTY_TYPES_URL`
- `SOURCE_BOUNDARY_DETAILS_URL`
- `SOURCE_TIMEOUT_SECONDS` (optional)

Manual run command (same logic as cron):

```bash
cd backend
python -m app.imports.sync_from_source \
  --datasets parcels owners assessments property_types \
  --chunk-size 1000 \
  --progress-every 2000 \
  --job-name nightly-core
```

### Frontend on Vercel

1. Import the repository in Vercel.
2. Set project root to `frontend`.
3. Set environment variable:
   - `VITE_API_BASE_URL` (for example `https://vk-lip-api.onrender.com`)
4. Deploy. `vercel.json` includes SPA route fallback so deep links work.

### Result

After both deployments complete, your frontend and backend are always on and available over HTTPS.

## Notes

This scaffold is intentionally minimal and ready for project-specific expansion.
