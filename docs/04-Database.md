# Database Schema

**Project:** VK Land Intelligence Platform (VK-LIP)

**Version:** 0.1

**Status:** Draft

**Owner:** Viraj Kothari

**Technical Lead:** ChatGPT

**Last Updated:** 2026-06-30

---

# Purpose

This document defines the logical database model for VK-LIP.

The database is the single source of truth for all parcels, ownership, transactions, scoring, CRM activity, and AI-generated investment intelligence.

---

# Design Principles

1. Every parcel has one permanent identity.
2. Historical information is never overwritten.
3. Every score is reproducible.
4. Every dataset is traceable.
5. The schema must support multiple cities and states.
6. Business logic belongs in the application—not the database.

---

# Entity Relationship Diagram (Logical)

Market
   │
Neighborhood
   │
Parcel
 ├── Owner
 ├── Assessment
 ├── Sale
 ├── Structure
 ├── Zoning
 ├── Score
 ├── Note
 ├── Contact
 ├── Opportunity
 └── AI Memo

---

# Table: markets

Purpose

Represents a city or county.

Columns

- market_id (PK)
- name
- state
- country
- created_at

---

# Table: neighborhoods

Purpose

Logical neighborhood boundaries.

Columns

- neighborhood_id (PK)
- market_id (FK)
- name
- geometry
- created_at

---

# Table: parcels

Purpose

Master record for every parcel.

Columns

- parcel_id (PK)
- market_id (FK)
- parcel_number
- gpin
- address
- city
- state
- zip
- latitude
- longitude
- geometry
- lot_sqft
- acreage
- current_zoning
- land_use
- sia_flag
- corner_lot
- created_at
- updated_at

Rules

One row per parcel.

Parcel records are never deleted.

---

# Table: owners

Purpose

Current owner information.

Columns

- owner_id (PK)
- parcel_id (FK)
- owner_name
- mailing_address
- mailing_city
- mailing_state
- mailing_zip
- is_llc
- is_trust
- is_estate
- is_absentee
- created_at
- updated_at

---

# Table: sales

Purpose

Historical sales transactions.

Columns

- sale_id (PK)
- parcel_id (FK)
- sale_date
- sale_price
- deed_book
- deed_page
- arms_length
- created_at

Rules

Multiple sales allowed per parcel.

Never overwrite history.

---

# Table: assessments

Purpose

Annual tax assessments.

Columns

- assessment_id (PK)
- parcel_id (FK)
- tax_year
- land_value
- improvement_value
- total_value
- assessment_date

Rules

One record per tax year.

---

# Table: structures

Purpose

Building characteristics.

Columns

- structure_id (PK)
- parcel_id (FK)
- year_built
- living_sqft
- stories
- bedrooms
- bathrooms
- construction_type
- use_code
- updated_at

---

# Table: scores

Purpose

Calculated investment metrics.

Columns

- score_id (PK)
- parcel_id (FK)
- vk_score
- builder_score
- momentum_score
- seller_probability
- confidence_score
- calculated_at
- model_version

Rules

Scores are recalculated.

Previous score history may be retained.

---

# Table: opportunities

Purpose

Tracks acquisition recommendations.

Columns

- opportunity_id (PK)
- parcel_id (FK)
- priority
- recommended_action
- estimated_offer
- estimated_units
- estimated_profit
- status
- created_at

---

# Table: contacts

Purpose

CRM.

Columns

- contact_id (PK)
- parcel_id (FK)
- contact_date
- contact_type
- result
- next_follow_up
- notes

---

# Table: notes

Purpose

Manual notes.

Columns

- note_id (PK)
- parcel_id (FK)
- author
- body
- created_at

---

# Table: ai_memos

Purpose

Stores AI-generated investment summaries.

Columns

- memo_id (PK)
- parcel_id (FK)
- investment_thesis
- strengths
- risks
- recommended_strategy
- generated_at
- model

---

# Table: imports

Purpose

Track every imported dataset.

Columns

- import_id (PK)
- dataset_name
- source
- file_name
- imported_at
- record_count
- checksum
- status

Rules

Every import is auditable.

---

# Relationships

One Market

→ Many Neighborhoods

One Neighborhood

→ Many Parcels

One Parcel

→ One Current Owner

One Parcel

→ Many Sales

One Parcel

→ Many Assessments

One Parcel

→ One Structure

One Parcel

→ Many Scores

One Parcel

→ Many Contacts

One Parcel

→ Many Notes

One Parcel

→ Many AI Memos

---

# Index Strategy

Unique

- parcel_number
- gpin

Indexes

- address
- owner_name
- sale_date
- vk_score
- seller_probability
- geometry (PostGIS)

---

# Future Tables

- permits
- code_violations
- utility_connections
- flood_zones
- school_districts
- demolitions
- building_permits
- mail_campaigns

---

# Success Criteria

The schema supports:

- Multiple markets
- Millions of parcels
- Historical tracking
- AI analysis
- GIS queries
- CRM
- Financial modeling

without requiring structural redesign.
