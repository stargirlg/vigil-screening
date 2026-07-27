"""
VIGIL — Demo data seeder

Creates realistic AML screening demo data:
- Customers with varied risk profiles
- Mix of clean, suspicious, and confirmed matches
- Realistic Indian/BFSI names and occupations
"""

import random
from datetime import date, timedelta


from app.db.database import SessionLocal
from app.models.customer import Customer


# High risk names (partial matches with known lists)
HIGH_RISK_CUSTOMERS = [
    {"full_name": "Raza Khan",        "dob": date(1955, 12, 26), "nationality": "Pakistani",  "occupation": "Arms Dealer",     "pan": "RZAKHN1234A"},
    {"full_name": "Mohammad Tariq",   "dob": date(1962, 3, 15),  "nationality": "Pakistani",  "occupation": "Hawala Operator", "pan": "MHTQR2345B"},
    {"full_name": "Abdul Karim",      "dob": date(1970, 7, 22),  "nationality": "Afghan",     "occupation": "Money Changer",   "pan": "ABDKRM3456C"},
    {"full_name": "Ali Hassan",       "dob": date(1968, 11, 5),  "nationality": "Iranian",    "occupation": "Bullion Trader",  "pan": "ALHSN4567D"},
    {"full_name": "Wang Fang",        "dob": date(1975, 4, 18),  "nationality": "Chinese",    "occupation": "Trade Finance",   "pan": "WNGFNG5678E"},
    {"full_name": "Ibrahim Al-Qosi",  "dob": date(1960, 8, 12),  "nationality": "Yemeni",     "occupation": "Unknown",         "pan": "IBMQS6789F"},
    {"full_name": "Dawood Merchant",  "dob": date(1955, 1, 1),   "nationality": "Pakistani",  "occupation": "Trader",          "pan": "DWDMRC7890G"},
    {"full_name": "Khalid Mahmood",   "dob": date(1972, 6, 30),  "nationality": "Pakistani",  "occupation": "Hawala Operator", "pan": "KHLDMM8901H"},
    {"full_name": "Tariq Anwar",      "dob": date(1965, 9, 25),  "nationality": "Pakistani",  "occupation": "Arms Dealer",     "pan": "TRQANW9012I"},
    {"full_name": "Hassan Al-Turki",  "dob": date(1958, 3, 14),  "nationality": "Saudi",      "occupation": "Financier",       "pan": "HSNTRK0123J"},
]

# Medium risk (PEP - politically exposed)
PEP_CUSTOMERS = [
    {"full_name": "Rajan Kumar Singh",   "dob": date(1965, 4, 12), "nationality": "Indian", "occupation": "State Official",    "pan": "RJNKSG1234K"},
    {"full_name": "Priya Mehta Sharma",  "dob": date(1970, 8, 22), "nationality": "Indian", "occupation": "Member of Parliament","pan": "PRYMHT2345L"},
    {"full_name": "Arvind Nath Tiwari",  "dob": date(1968, 2, 15), "nationality": "Indian", "occupation": "Government Official","pan": "ARVNTH3456M"},
    {"full_name": "Sunita Devi Pandey",  "dob": date(1972, 11, 5), "nationality": "Indian", "occupation": "IAS Officer",       "pan": "SNTPDV4567N"},
    {"full_name": "Mohd Farouk Ansari",  "dob": date(1960, 7, 18), "nationality": "Indian", "occupation": "Minister",          "pan": "MHDFNK5678O"},
]

# Clean customers (low risk)
CLEAN_NAMES = [
    "Arun Sharma", "Priya Patel", "Rahul Gupta", "Sunita Singh", "Amit Kumar",
    "Deepa Nair", "Vijay Menon", "Kavitha Reddy", "Suresh Iyer", "Meera Joshi",
    "Rajesh Verma", "Anita Desai", "Prakash Rao", "Lalitha Bhat", "Mohan Das",
    "Rekha Pillai", "Sanjay Mishra", "Uma Krishnan", "Vinod Tiwari", "Sarala Devi",
    "John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "James Wilson",
    "Jennifer Taylor", "Robert Anderson", "Lisa Thomas", "William Jackson", "Mary White",
    "Carlos Rodriguez", "Maria Garcia", "Juan Martinez", "Ana Lopez", "Pedro Sanchez",
    "Yuki Tanaka", "Kenji Yamamoto", "Akira Sato", "Hana Watanabe", "Taro Suzuki",
    "Wei Zhang", "Mei Li", "Jun Wang", "Ling Chen", "Bo Liu",
    "Ahmed Hassan", "Fatima Al-Rashid", "Omar Abdullah", "Layla Khalil", "Karim Nasser",
    "Ivan Petrov", "Natasha Ivanova", "Dmitri Sokolov", "Elena Popova", "Alexei Volkov",
    "Pierre Dubois", "Marie Laurent", "Jacques Bernard", "Sophie Martin", "Louis Leroy",
    "Hans Mueller", "Greta Schmidt", "Klaus Weber", "Ingrid Fischer", "Werner Braun",
    "Oluwaseun Adeyemi", "Chioma Okafor", "Emeka Nwosu", "Ngozi Obi", "Chidi Eze",
    "Aarav Patel", "Ishaan Shah", "Ananya Roy", "Vivaan Chatterjee", "Diya Mukherjee",
    "Rohan Mehta", "Pooja Kulkarni", "Arjun Nair", "Siya Jain", "Kabir Kapoor",
    "Aditya Malhotra", "Shreya Agarwal", "Kartik Bose", "Tanvi Ghosh", "Nikhil Das","Gayatri Jeon",
    "Riya Kulshreshtha","Manish Kulkarni", "Snehal Patil","Harshvardhan Deshmukh",
]

OCCUPATIONS_CLEAN = [
    "Software Engineer", "Doctor", "Teacher", "Accountant", "Lawyer",
    "Business Owner", "Engineer", "Nurse", "Professor", "Architect",
    "Pharmacist", "Dentist", "Journalist", "Designer", "Consultant",
    "Manager", "Director", "Analyst", "Developer", "Researcher",
]

NATIONALITIES = [
    "Indian", "Indian", "Indian", "Indian", "Indian",
    "American", "British", "Canadian", "Australian", "German",
    "French", "Japanese", "Chinese", "Brazilian", "South African",
]


def random_dob():
    start = date(1960, 1, 1)
    end = date(2000, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def random_pan():
    import string
    letters = string.ascii_uppercase
    return (
        "".join(random.choices(letters, k=5)) +
        "".join(random.choices("0123456789", k=4)) +
        random.choice(letters)
    )


def seed_demo_data():
    db = SessionLocal()
    created = 0

    print("=" * 50)
    print("VIGIL Demo Data Seeder")
    print("=" * 50)

    print("Seeding high-risk customers...")
    for c in HIGH_RISK_CUSTOMERS:
        if not db.query(Customer).filter(Customer.full_name == c["full_name"]).first():
            db.add(Customer(
                full_name=c["full_name"],
                dob=c["dob"],
                nationality=c["nationality"],
                occupation=c["occupation"],
                pan=c["pan"],
                source="OFAC_SEED",
            ))
            created += 1
            print(f"  ✓ {c['full_name']}")

    print("\nSeeding PEP customers...")
    for c in PEP_CUSTOMERS:
        if not db.query(Customer).filter(Customer.full_name == c["full_name"]).first():
            db.add(Customer(
                full_name=c["full_name"],
                dob=c["dob"],
                nationality=c["nationality"],
                occupation=c["occupation"],
                pan=c["pan"],
                source="PEP_SEED",
            ))
            created += 1
            print(f"  ✓ {c['full_name']}")

    print("\nSeeding clean customers...")
    for name in CLEAN_NAMES:
        if not db.query(Customer).filter(Customer.full_name == name).first():
            db.add(Customer(
                full_name=name,
                dob=random_dob(),
                nationality=random.choice(NATIONALITIES),
                occupation=random.choice(OCCUPATIONS_CLEAN),
                pan=random_pan(),
                source="KYC_SEED",
            ))
            created += 1

    db.commit()
    db.close()


    print(f"\n✅ Done! {created} customers created.")
    print("\nSummary")
    print("-" * 40)
    print(f"High Risk Customers : {len(HIGH_RISK_CUSTOMERS)}")
    print(f"PEP Customers       : {len(PEP_CUSTOMERS)}")
    print(f"Clean Customers     : {len(CLEAN_NAMES)}")
    print(f"Total Created       : {created}")
    print("-" * 40)
    print("Next Step: Run batch screening to generate alerts.")

if __name__ == "__main__":
    seed_demo_data()