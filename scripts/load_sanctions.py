from app.db.database import SessionLocal
from app.models.sanction_entry import SanctionEntry
from datetime import date

db = SessionLocal()

entries = [
    SanctionEntry(
        source='OFAC', source_id='1',
        full_name='Raza Khan',
        aliases=['Raza Ahmed Khan'],
        dob=date(1955, 12, 26),
        nationality='Pakistani',
        occupation='Arms Dealer',
        program='SDGT',
        is_active='true'
    ),
    SanctionEntry(
        source='OFAC', source_id='2',
        full_name='Mohammad Tariq',
        aliases=['M Tariq'],
        dob=date(1968, 7, 15),
        nationality='Pakistani',
        occupation='Terrorist',
        program='SDGT',
        is_active='true'
    ),
    SanctionEntry(
        source='OFAC', source_id='3',
        full_name='Abdul Karim',
        aliases=['A Karim'],
        dob=date(1972, 4, 18),
        nationality='Pakistani',
        occupation='Arms Trader',
        program='SDGT',
        is_active='true'
    ),
    SanctionEntry(
        source='OFAC', source_id='4',
        full_name='Ali Hassan',
        aliases=['Ali H'],
        dob=date(1972, 8, 19),
        nationality='Pakistani',
        occupation='Hawala Dealer',
        program='SDGT',
        is_active='true'
    ),
    SanctionEntry(
        source='UN', source_id='5',
        full_name='Wang Fang',
        aliases=[],
        dob=date(1984, 1, 8),
        nationality='Chinese',
        occupation='Money Changer',
        program='DPRK',
        is_active='true'
    ),
]

for e in entries:
    db.add(e)
db.commit()
print(f'Loaded {len(entries)} sanction entries')
db.close()