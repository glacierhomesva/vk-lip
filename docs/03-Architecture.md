# Architecture

vk-lip is designed as a small modular backend service with the following layers:

- API layer: FastAPI endpoints and route definitions.
- Core layer: configuration, settings, and application constants.
- Database layer: session management, models, and persistence.
- Scoring layer: business logic for scoring and analysis.
- Import layer: data ingestion and preprocessing utilities.
