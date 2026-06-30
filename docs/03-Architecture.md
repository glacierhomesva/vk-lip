# System Architecture

**Project:** VK Land Intelligence Platform (VK-LIP)

**Version:** 0.1

**Status:** Draft

**Owner:** Viraj Kothari

**Technical Lead:** ChatGPT

**Last Updated:** 2026-06-30

---

# Purpose

This document defines the high-level architecture for VK-LIP.

Its purpose is to establish a scalable, maintainable, and modular system that supports acquisition intelligence for residential developers.

The architecture favors simplicity, extensibility, and clear separation of responsibilities.

---

# Guiding Principles

1. One Source of Truth
2. Modular Design
3. API-First
4. Cloud-Native
5. GIS-Centric
6. AI-Augmented (not AI-dependent)

---

# High-Level Architecture

                    Browser
                       │
                       │
                React Frontend
                       │
               REST / JSON API
                       │
                 FastAPI Backend
                       │
        ┌──────────────┴──────────────┐
        │                             │
 Business Logic                 Import Engine
        │                             │
        └──────────────┬──────────────┘
                       │
               PostgreSQL + PostGIS
                       │
        Parcel • Owner • Sales • Scores

---

# Major Components

## 1. Frontend

Technology

- React
- TypeScript
- MapLibre GL

Responsibilities

- Dashboard
- Search
- Parcel Detail
- Interactive Map
- Filters
- CRM Interface

The frontend should never contain business logic.

It only presents information returned by the API.

---

## 2. Backend

Technology

- FastAPI
- Python

Responsibilities

- Authentication
- Parcel Search
- Scoring
- AI Integration
- Import Services
- Reporting

The backend owns all business rules.

---

## 3. Database

Technology

- PostgreSQL
- PostGIS

Responsibilities

- Store parcel geometry
- Store ownership
- Sales history
- Assessments
- Scores
- Notes
- CRM

The database is the single source of truth.

---

## 4. Import Engine

Purpose

Import public datasets into the database.

Examples

- Parcel Boundaries
- Assessments
- Sales
- Residential Details
- Zoning
- Permits
- Future MLS exports

Each importer should be independent.

---

## 5. Scoring Engine

Purpose

Generate investment intelligence.

Outputs

- VK Score™
- Builder Score™
- Momentum Score™
- Seller Probability™

The scoring engine should be stateless.

Scores are recalculated whenever source data changes.

---

## 6. AI Engine

Purpose

Convert data into recommendations.

Examples

- Investment Thesis
- Offer Strategy
- Risk Summary
- Next Best Action

The AI engine never modifies source data.

It generates recommendations only.

---

# Data Flow

County Data

↓

Import Engine

↓

Database

↓

Scoring Engine

↓

AI Engine

↓

REST API

↓

React Frontend

↓

Developer

---

# Design Rules

Rule 1

No business logic inside React.

---

Rule 2

No direct database access from the frontend.

---

Rule 3

Every feature must be exposed through an API.

---

Rule 4

Every score must be reproducible.

No hidden calculations.

---

Rule 5

Every imported dataset must be traceable.

The system should always know:

- Source
- Import date
- Version

---

# Deployment Architecture

Browser

↓

GitHub

↓

GitHub Codespaces

↓

FastAPI

↓

Supabase

↓

PostGIS

---

# Security

Authentication

- JWT
- Role-based permissions
- HTTPS only
- Secrets stored in environment variables

No credentials committed to GitHub

---

# Future Expansion

The architecture should support:

- Multiple cities
- Multiple counties
- Multiple users
- Commercial licensing
- Mobile applications
- AI assistants

without redesigning the core platform.

---

# Out of Scope

- Construction Management
- Accounting
- Scheduling
- Payroll
- Property Management

These remain external systems.

---

# Architecture Success Criteria

The architecture is successful if:

- New datasets can be imported without changing existing code.
- New scoring models can be added independently.
- The frontend can be replaced without rewriting the backend.
- The platform scales from one neighborhood to multiple states.
