# VIGIL — System Architecture

**Version:** 1.0.0  
**Date:** August 2026

---

# Overview

VIGIL follows a layered architecture that separates the user interface, business logic, persistence layer, and background processing. This separation improves maintainability, scalability, and testability.

---

# High-Level Architecture

```text
                React Frontend
                       │
                 REST API (HTTPS)
                       │
                FastAPI Backend
       ┌───────────────┼───────────────┐
       │               │               │
 Authentication   Screening Engine   Rule Engine
       │               │               │
       └───────────────┼───────────────┘
                       │
                  SQLAlchemy ORM
                       │
                 PostgreSQL Database
                       │
          Celery + Redis Background Jobs
```

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Frontend | React 19 + TypeScript + Vite |
| Backend | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2 |
| Authentication | JWT |
| Validation | Pydantic v2 |
| Background Jobs | Celery + Redis |
| Reporting | ReportLab |
| Charts | Recharts |
| Matching Engine | RapidFuzz |

---

# Backend Structure

```text
app/
├── api/
├── auth/
├── core/
├── db/
├── models/
├── schemas/
├── tasks/
├── utils/
├── config.py
├── dependencies.py
└── main.py

```

---

# Request Flow

```text
User

↓

React Frontend

↓

REST API Request

↓

FastAPI Router

↓

Core Business Logic

↓

Database

↓

JSON Response

↓

Frontend Update
```

---

# Authentication Flow

```text
User Login

↓

JWT Token Generated

↓

Stored by Frontend

↓

Token sent with API Requests

↓

FastAPI Authentication Middleware

↓

Role Validation

↓

Protected Endpoint
```

---

# AML Screening Flow

```text
Customer

↓

Customer Screening

↓

Risk Score Calculation

↓

Alert Generation

↓

Analyst Investigation

↓

Compliance Officer Decision

↓

Case Closure
```

---

# Database

Primary database:

- PostgreSQL 16

Main entities:

- Users
- Customers
- Alerts
- Cases
- Rules
- Rule Versions
- Screening Snapshots
- Internal Watchlist
- Audit Logs

---

# Security

- JWT Authentication
- Role-Based Access Control (RBAC)
- Password Hashing
- Immutable Audit Logs
- Protected API Endpoints

---

# Background Processing

Celery and Redis provide the infrastructure for asynchronous background processing.

Current tasks:
- Bulk screening
- Report generation
- Scheduled jobs

Planned:
- Notification services

Redis is used as the message broker.

---

# Design Principles

- Layered Architecture
- Separation of Concerns
- Stateless REST APIs
- Configurable Rule Engine
- Immutable Audit Trail
- Modular Components

---

# Future Improvements

- Kubernetes deployment
- API Gateway
- Horizontal scaling
- Distributed caching
- Real-time notifications
- Monitoring with Prometheus and Grafana