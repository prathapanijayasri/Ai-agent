import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
from app.core.database import SessionLocal, engine, Base
from app.models.schema import Student, Faculty, Company

# Create tables
Base.metadata.create_all(bind=engine)

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def load_json(folder, filename):
    path = os.path.join(data_dir, folder, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def main():
    db = SessionLocal()
    try:
        print("Loading synthetic students...")
        students = load_json("students", "seed.json")
        for s in students:
            # Check if exists
            if not db.query(Student).filter(Student.student_id == s['student_id']).first():
                db_student = Student(**s)
                db.add(db_student)
                
        print("Loading synthetic faculty...")
        faculty = load_json("faculty", "seed.json")
        for f in faculty:
            if not db.query(Faculty).filter(Faculty.faculty_id == f['faculty_id']).first():
                db_faculty = Faculty(**f)
                db.add(db_faculty)
                
        print("Loading synthetic companies...")
        companies = load_json("companies", "seed.json")
        for c in companies:
            if not db.query(Company).filter(Company.company_id == c['company_id']).first():
                db_company = Company(**c)
                db.add(db_company)
                
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding db: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
