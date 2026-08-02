# VIGIL — Product Requirements Document (PRD)

**Version:** 1.0.0  
**Date:** August 2026  
**Status:** Production

---

## 1. Problem Statement

Compliance teams at NBFCs and Banks face:
- 700+ AML alerts per day
- Small investigation teams (3-5 analysts)
- 24-48 hour SLA requirements
- Manual screening taking 15-20 minutes per customer
- High false positive rates (60-80%)
- No structured audit trail for regulators

**Result:** Analysts are overwhelmed, SLAs are breached, and regulators find inconsistent documentation.

---

## 2. Solution

VIGIL is a risk-based AML compliance screening and decision management platform that:
- Auto-screens customers against 8 parameters
- Auto-closes LOW risk alerts (no analyst needed)
- Routes HIGH/CRITICAL alerts to analysts with full context
- Enforces four-eyes approval workflow
- Generates immutable audit trail

**Result:** 70-80% reduction in analyst workload with full regulatory defensibility.

---

## 3. Target Users

| Role | Description | Primary Need |
|------|-------------|--------------|
| Analyst | Reviews alerts, investigates cases | Fast alert context, clear workflow |
| Compliance Officer (CO) | Final decision authority | Approval queue, SAR filing |
| Checker | Second review layer | Four-eyes enforcement |
| Admin | System configuration | Rule management, user access |

---

## 4. Core Features

### 4.1 Screening Engine
- 8-parameter screening (Name, DOB, ID, Nationality, Occupation, Adverse Media, PEP, Watchlist)
- RapidFuzz fuzzy name matching (85% threshold)
- Weighted risk scoring (0-100)
- Explainability engine with reason codes

### 4.2 Risk Classification
| Risk Level | Score | Action |
|------------|-------|--------|
| LOW | 0-29 | Auto-close |
| MEDIUM | 30-49 | Analyst review (48hr SLA) |
| HIGH | 50-74 | Priority review (24hr SLA) |
| CRITICAL | 75-100 | Immediate CO action (4hr SLA) |

### 4.3 Compliance Workflow
- Alert → Investigation → Recommendation → CO Decision → Closure
- Four-eyes enforcement (analyst recommends, CO approves)
- Decision locking (immutable after CO decision)
- SAR flagging for FIU-IND reporting

### 4.4 Internal Watchlist
- State-based risk override (not linear points)
- FRAUD_CONFIRMED → score = max(score, 90)
- SAR_FILED → score = max(score, 75)
- UNDER_INVESTIGATION → score = max(score, 50) + 10

### 4.5 Rule Engine
- DB-stored configurable rules
- Maker-checker approval pattern
- Immutable rule version snapshots
- Every alert stores rule_version_used

### 4.6 Reporting
- PDF: SAR draft, case closure, audit export
- CSV: Alert export with customer details
- Audit trail: Immutable compliance log

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| API Response Time | < 2 seconds |
| Screening Time | < 5 seconds per customer |
| Availability | 99.9% uptime |
| Data Retention | 7 years (RBI requirement) |
| Audit Trail | Immutable, tamper-proof |
| Authentication | JWT with role-based access |

---

## 6. Compliance Standards

- RBI AML/KYC Guidelines 2023
- PMLA 2002 (India)
- FIU-IND reporting requirements
- FATF Recommendations
- Basel III compliance framework

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Alert auto-closure rate | > 60% |
| Analyst time per alert | < 5 minutes |
| False positive rate | < 20% |
| SLA compliance | > 95% |
| Audit trail completeness | 100% |

---

## 8. Out of Scope (v1.0)

- Real-time transaction monitoring
- Mobile application
- Direct FIU-IND API integration
- Customer communication portal
- Machine learning risk scoring