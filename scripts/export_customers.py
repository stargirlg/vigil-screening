import csv
from app.db.database import SessionLocal
from app.models.customer import Customer

db = SessionLocal()
customers = db.query(Customer).all()

with open("export_customers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "full_name", "dob", "pan", "aadhaar",
        "passport", "nationality", "occupation", "source"
    ])
    for c in customers:
        writer.writerow([
            c.full_name or "",
            str(c.dob) if c.dob else "",
            c.pan or "",
            c.aadhaar or "",
            c.passport or "",
            c.nationality or "",
            c.occupation or "",
            c.source or "",
        ])

db.close()
print(f"Exported {len(customers)} customers to export_customers.csv")