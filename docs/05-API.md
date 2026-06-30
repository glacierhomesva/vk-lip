# API Specification

**Project:** VK Land Intelligence Platform (VK-LIP)

**Version:** 0.1

**Status:** Draft

**Owner:** Viraj Kothari

**Technical Lead:** ChatGPT

**Last Updated:** 2026-06-30

---

# Purpose

This document defines the REST API contract between the VK-LIP frontend and backend.

The API is responsible for exposing parcel information, search capabilities, scoring, maps, CRM activity, and investment intelligence.

The frontend never communicates directly with the database.

---

# API Design Principles

1. REST-first
2. JSON responses
3. Stateless requests
4. Versioned API
5. Predictable URLs
6. Consistent error handling

Base URL

/api/v1

---

# Health

GET /health

Purpose

Verify application status.

Response

{
  "status": "ok",
  "version": "0.1.0"
}

---

# Parcels

GET /parcels

Purpose

Return paginated parcel list.

Query Parameters

- page
- pageSize
- city
- neighborhood
- minScore
- maxScore
- zoning
- ownerType

Response

{
  "items": [],
  "page": 1,
  "total": 15672
}

---

GET /parcels/{parcelId}

Purpose

Return complete parcel details.

Includes

- Parcel
- Owner
- Sales
- Assessments
- Structure
- Scores
- CRM
- AI Memo

---

GET /parcels/{parcelId}/neighbors

Purpose

Return adjacent parcels.

Used for assemblage analysis.

---

GET /parcels/{parcelId}/history

Purpose

Return ownership, assessment and sales timeline.

---

# Search

GET /search

Purpose

Global search.

Searches

- Address
- Parcel Number
- Owner
- Street
- Neighborhood

Response

{
  "results": []
}

---

# Neighborhoods

GET /neighborhoods

Return all neighborhoods.

---

GET /neighborhoods/{id}

Return neighborhood summary.

Includes

- Parcel Count
- Average VK Score
- Average Assessment
- Average Sale Price
- Top Opportunities

---

# Scores

GET /scores/{parcelId}

Return

- VK Score
- Builder Score
- Momentum Score
- Seller Probability
- Confidence Score
- Model Version

---

POST /scores/recalculate

Purpose

Recalculate all parcel scores.

Restricted to administrators.

---

# Opportunities

GET /opportunities

Purpose

Return recommended acquisition opportunities.

Filters

- Priority
- Neighborhood
- Status
- Minimum Score
- Recommended Action

---

GET /opportunities/top

Purpose

Return Top 25 opportunities.

---

# CRM

GET /contacts

Return outreach history.

---

POST /contacts

Create new contact record.

---

PATCH /contacts/{id}

Update follow-up information.

---

# Notes

GET /notes/{parcelId}

Return analyst notes.

---

POST /notes

Create note.

---

DELETE /notes/{id}

Delete note.

---

# AI

GET /memo/{parcelId}

Return AI-generated investment memo.

---

POST /memo/{parcelId}/refresh

Regenerate investment memo.

---

# Imports

POST /imports

Upload dataset.

---

GET /imports

Return import history.

---

POST /imports/rebuild

Rebuild database after import.

Administrator only.

---

# Authentication

POST /auth/login

POST /auth/logout

GET /auth/me

Future

- Single Sign-On
- Google Login
- Microsoft Login

---

# Error Format

All errors use

{
    "error": {
        "code": "PARCEL_NOT_FOUND",
        "message": "Parcel does not exist."
    }
}

---

# HTTP Status Codes

- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 500 Internal Server Error

---

# API Versioning

All APIs use

/api/v1

Breaking changes require

/api/v2

---

# Success Criteria

The API should allow the frontend to function without direct database access.

Every feature within VK-LIP should be exposed through a documented API endpoint.

No business logic should exist in the frontend.
