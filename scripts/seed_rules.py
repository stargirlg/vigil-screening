from app.db.database import SessionLocal
from app.models.rule import Rule, RuleStatus
from app.models.user import User

db = SessionLocal()
admin = db.query(User).filter(User.email == 'admin@vigil.com').first()

defaults = [
    ('Name match',    'name',          25, 85),
    ('Date of birth', 'dob',           15, None),
    ('ID document',   'id',            20, None),
    ('Nationality',   'nationality',   10, None),
    ('Occupation',    'occupation',     5, None),
    ('Adverse media', 'adverse_media', 10, None),
    ('PEP status',    'pep',           15, None),
]

for name, param, weight, threshold in defaults:
    existing = db.query(Rule).filter(Rule.param == param).first()
    if not existing:
        r = Rule(
            name=name, param=param, weight=weight,
            threshold=threshold, enabled=True,
            status=RuleStatus.ACTIVE,
            rule_set_version="1.0",
            version=1,
            created_by=admin.id,
            created_by_email=admin.email,
            approved_by=admin.id,
            approved_by_email=admin.email,
            description=f'Default weight for {param} parameter',
        )
        db.add(r)

db.commit()
print('Default rules seeded — 7 rules active!')
db.close()