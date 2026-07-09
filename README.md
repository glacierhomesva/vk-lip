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

## Production deployment (low-cost path)

Use Render only for the static frontend, host backend API on your preferred provider, and run scheduled data sync in GitHub Actions.

### Frontend on Render Static Site

1. In Render, create a Blueprint from this repository.
2. Render will use `render.yaml` to create `vk-lip-frontend` as a static site.
3. Set `VITE_API_BASE_URL` to your deployed backend URL (for example `https://your-api.example.com`).
4. Deploy.

### Backend hosting (outside Render)

Deploy the backend (`backend/`) on any provider that supports Python web services and environment variables.
Required backend env vars:

- `DATABASE_URL`
- `CORS_ORIGINS` (comma-separated, include your Render frontend URL)

### Scheduled data sync in GitHub Actions

The workflow `.github/workflows/scheduled-source-sync.yml` runs:

1. Nightly core sync at `0 6 * * *` (UTC)
   - datasets: `parcels owners assessments property_types`
2. Weekly boundary sync at `30 6 * * 0` (UTC)
   - dataset: `boundary_details`

Add these repository secrets in GitHub: Settings -> Secrets and variables -> Actions:

- `DATABASE_URL`
- `SOURCE_PARCELS_URL`
- `SOURCE_OWNERS_URL`
- `SOURCE_ASSESSMENTS_URL`
- `SOURCE_PROPERTY_TYPES_URL`
- `SOURCE_BOUNDARY_DETAILS_URL`
- `SOURCE_TIMEOUT_SECONDS` (optional)

Each run uses PostgreSQL advisory locking via `--job-name` to avoid overlapping syncs.

Manual run command (same logic as scheduler):

```bash
cd backend
python -m app.imports.sync_from_source \
  --datasets parcels owners assessments property_types \
  --chunk-size 1000 \
  --progress-every 2000 \
  --job-name nightly-core
```

### Result

After deployment and secret setup, your frontend is hosted on Render, backend stays always-on at your chosen provider, and data refresh is automated by GitHub Actions.

## Notes

This scaffold is intentionally minimal and ready for project-specific expansion.
