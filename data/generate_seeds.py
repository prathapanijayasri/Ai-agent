import json
import os

data_dir = "/Users/jayasri/Desktop/Ai-agent/Ai-agent/data"

def write_json(folder, filename, data):
    path = os.path.join(data_dir, folder, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

write_json("students", "seed.json", [
    {
        "student_id": "DEMO001",
        "name": "Demo Student 1",
        "program": "B.Tech",
        "branch": "CSE",
        "year": 3,
        "cgpa": 8.5,
        "backlogs": 0,
        "data_type": "synthetic"
    },
    {
        "student_id": "DEMO002",
        "name": "Demo Student 2",
        "program": "B.Tech",
        "branch": "ECE",
        "year": 4,
        "cgpa": 6.8,
        "backlogs": 2,
        "data_type": "synthetic"
    }
])

write_json("faculty", "seed.json", [
    {
        "faculty_id": "FAC001",
        "name": "Prof. Synthetic AI",
        "department": "SCOPE",
        "designation": "Associate Professor",
        "courses": ["CSE3001"],
        "official_email": "synthetic.ai@vitap.ac.in",
        "source": "synthetic"
    }
])

write_json("companies", "seed.json", [
    {
        "company_id": "COMP001",
        "company_name": "DemoTech Corp",
        "minimum_cgpa": 7.0,
        "maximum_backlogs": 0,
        "eligible_programs": ["B.Tech CSE", "B.Tech ECE"],
        "minimum_10th_percentage": 60,
        "minimum_12th_percentage": 60,
        "other_requirements": "None",
        "source": "synthetic"
    }
])
