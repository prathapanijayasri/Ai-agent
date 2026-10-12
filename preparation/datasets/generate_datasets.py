import json
import os

datasets_dir = "/Users/jayasri/Desktop/Ai-agent/Ai-agent/preparation/datasets"

def write_json(filename, data):
    with open(os.path.join(datasets_dir, filename), "w") as f:
        json.dump(data, f, indent=4)

write_json("attendance_questions.json", [
    {
        "id": "ATT001",
        "question": "What happens if my attendance is below 75%?",
        "category": "attendance",
        "expected_source": "Academic Regulations",
        "expected_behavior": "Explain FAT debarment rules.",
        "requires_tool": "rag_search",
        "data_type": "synthetic"
    }
])

write_json("academic_questions.json", [
    {
        "id": "ACA001",
        "question": "How many credits are required for a B.Tech CSE degree?",
        "category": "academics",
        "expected_source": "B.Tech Curriculum",
        "expected_behavior": "State total credits required.",
        "requires_tool": "rag_search",
        "data_type": "synthetic"
    }
])

write_json("examination_questions.json", [
    {
        "id": "EXA001",
        "question": "What is the passing criteria for a CAT exam?",
        "category": "examinations",
        "expected_source": "Academic Regulations",
        "expected_behavior": "Explain internal assessment passing rules.",
        "requires_tool": "rag_search",
        "data_type": "synthetic"
    }
])

write_json("placement_questions.json", [
    {
        "id": "PLA001",
        "question": "What is the minimum CGPA for dream companies?",
        "category": "placements",
        "expected_source": "Placement Guidelines",
        "expected_behavior": "State the standard minimum CGPA (e.g., 7.0).",
        "requires_tool": "rag_search",
        "data_type": "synthetic"
    }
])

write_json("certificate_questions.json", [
    {
        "id": "CER001",
        "question": "How do I apply for a bonafide certificate?",
        "category": "certificates",
        "expected_source": "Student Handbook",
        "expected_behavior": "List steps to apply via VTOP.",
        "requires_tool": "rag_search",
        "data_type": "synthetic"
    }
])

write_json("faculty_questions.json", [
    {
        "id": "FAC001",
        "question": "Which department does Professor Demo teach in?",
        "category": "faculty",
        "expected_source": "Faculty DB",
        "expected_behavior": "Return department based on tool output.",
        "requires_tool": "faculty_search",
        "data_type": "synthetic"
    }
])

write_json("student_questions.json", [
    {
        "id": "STU001",
        "question": "How many backlogs does DEMO001 have?",
        "category": "student",
        "expected_source": "Student DB",
        "expected_behavior": "Return structured backlog count.",
        "requires_tool": "student_info_lookup",
        "data_type": "synthetic"
    }
])

write_json("tool_selection.json", [
    {
        "id": "TS001",
        "question": "Calculate how many classes I need to attend to get 75%. I have attended 20 out of 40.",
        "expected_tool": "attendance_calculator",
        "data_type": "synthetic"
    }
])

write_json("conversations.json", [
    {
        "id": "CONV001",
        "messages": [
            {"role": "user", "content": "What is the placement eligibility?"},
            {"role": "assistant", "content": "Usually a CGPA of 7.0 with no backlogs."},
            {"role": "user", "content": "What if my CGPA is 7.8?"}
        ],
        "expected_behavior": "Recognize the user meets the 7.0 criteria.",
        "data_type": "synthetic"
    }
])
