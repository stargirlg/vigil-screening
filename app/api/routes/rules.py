"""
VIGIL — Rule Engine Routes
Maker-checker pattern:
  Admin creates rule (DRAFT)
  CO approves or rejects
  Only ACTIVE rules affect screening

GET  /rules              → list all rules
POST /rules              → admin creates rule (DRAFT)
PATCH /rules/{id}        → admin updates rule (resets to DRAFT)
POST /rules/{id}/approve → CO approves or rejects
GET  /rules/{id}/versions → version history
GET  /rules/active       → currently active rules (used by engine)
"""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.rule import Rule, RuleVersion, RuleStatus
from app.models.audit_log import AuditLog
from app.schemas.rule import RuleCreate, RuleUpdate, RuleApproval, RuleOut, RuleVersionOut
from app.dependencies import get_current_user
from app.auth.rbac import require_admin, require_co
from app.models.user import User

router = APIRouter(prefix="/rules", tags=["Rule Engine"])


def _snapshot(rule: Rule) -> dict:
    return {
        "id":           str(rule.id),
        "name":         rule.name,
        "param":        rule.param,
        "weight":       rule.weight,
        "enabled":      rule.enabled,
        "threshold":    rule.threshold,
        "status":       rule.status,
        "version":      rule.version,
        "rule_set_version": rule.rule_set_version,
    }


@router.get("/active")
def get_active_rules(db: Session = Depends(get_db)):
    """
    Returns currently active rule weights.
    Used by the screening engine to get live configuration.
    """
    rules = db.query(Rule).filter(
        Rule.status == RuleStatus.ACTIVE,
        Rule.enabled == True,
    ).all()

    if not rules:
        # Fall back to defaults if no rules configured
        return {
            "rule_set_version": "1.0 (default)",
            "source": "default",
            "weights": {
                "name":          25,
                "dob":           15,
                "id":            20,
                "nationality":   10,
                "occupation":    5,
                "adverse_media": 10,
                "pep":           15,
            },
            "thresholds": {
                "name_fuzzy":    85,
                "score_high":    50,
            }
        }

    weights = {r.param: r.weight for r in rules}
    versions = list(set(r.rule_set_version for r in rules))

    return {
        "rule_set_version": versions[0] if versions else "1.0",
        "source": "database",
        "weights": weights,
        "thresholds": {
            r.param: r.threshold
            for r in rules if r.threshold is not None
        }
    }


@router.get("", response_model=list[RuleOut])
def list_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rules = db.query(Rule).order_by(Rule.created_at.desc()).all()
    return [RuleOut.model_validate(r) for r in rules]


@router.post("", response_model=RuleOut)
def create_rule(
    payload: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin creates a rule — starts as DRAFT, needs CO approval."""
    existing = db.query(Rule).filter(Rule.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rule name already exists")

    rule = Rule(
        name=payload.name,
        param=payload.param,
        weight=payload.weight,
        enabled=payload.enabled,
        threshold=payload.threshold,
        description=payload.description,
        status=RuleStatus.DRAFT,
        version=1,
        created_by=current_user.id,
        created_by_email=current_user.email,
    )
    db.add(rule)
    db.flush()

    # Version snapshot
    version = RuleVersion(
        rule_id=rule.id,
        version=1,
        rule_set_version=rule.rule_set_version,
        snapshot=_snapshot(rule),
        changed_by=current_user.id,
        changed_by_email=current_user.email,
        change_reason="Initial creation",
    )
    db.add(version)

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="RULE_CREATED",
        entity_type="RULE",
        entity_id=str(rule.id),
        details={"name": rule.name, "param": rule.param, "weight": rule.weight},
    ))
    db.commit()
    db.refresh(rule)
    return RuleOut.model_validate(rule)


@router.patch("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: UUID,
    payload: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Admin updates a rule — resets to DRAFT for re-approval."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if payload.weight is not None:   rule.weight    = payload.weight
    if payload.enabled is not None:  rule.enabled   = payload.enabled
    if payload.threshold is not None: rule.threshold = payload.threshold
    if payload.description is not None: rule.description = payload.description

    rule.status  = RuleStatus.DRAFT
    rule.version += 1
    rule.approved_by = None
    rule.approved_at = None

    version = RuleVersion(
        rule_id=rule.id,
        version=rule.version,
        rule_set_version=rule.rule_set_version,
        snapshot=_snapshot(rule),
        changed_by=current_user.id,
        changed_by_email=current_user.email,
        change_reason="Rule updated — pending re-approval",
    )
    db.add(version)
    db.commit()
    db.refresh(rule)
    return RuleOut.model_validate(rule)


@router.post("/{rule_id}/approve", response_model=RuleOut)
def approve_rule(
    rule_id: UUID,
    payload: RuleApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_co),
):
    """
    CO approves or rejects a rule.
    Maker-checker: CO cannot approve their own rule.
    """
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if rule.status != RuleStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only DRAFT rules can be approved")

    # Maker-checker: CO cannot approve own rule
    if str(rule.created_by) == str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Maker-checker violation: you cannot approve your own rule"
        )

    rule.status           = RuleStatus.ACTIVE if payload.approved else RuleStatus.REJECTED
    rule.approved_by      = current_user.id
    rule.approved_by_email = current_user.email
    rule.approved_at      = datetime.utcnow()
    rule.approval_notes   = payload.notes

    db.add(AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="RULE_APPROVED" if payload.approved else "RULE_REJECTED",
        entity_type="RULE",
        entity_id=str(rule_id),
        details={
            "approved": payload.approved,
            "notes": payload.notes,
            "rule_name": rule.name,
        },
    ))
    db.commit()
    db.refresh(rule)
    return RuleOut.model_validate(rule)


@router.get("/{rule_id}/versions", response_model=list[RuleVersionOut])
def get_rule_versions(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Full version history for a rule — auditor view."""
    versions = db.query(RuleVersion).filter(
        RuleVersion.rule_id == rule_id
    ).order_by(RuleVersion.version.desc()).all()
    return [RuleVersionOut.model_validate(v) for v in versions]