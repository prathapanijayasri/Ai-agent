from pydantic import BaseModel, Field
from typing import Optional, List
from ..registry import BaseTool
import math

from ...core.database import SessionLocal
from ...models.schema import Student, Company, Faculty
from ...rag.retriever import PGVectorRetriever

class AttendanceCalculatorInput(BaseModel):
    current_attended: int = Field(..., description="Number of classes attended so far")
    current_total: int = Field(..., description="Total number of classes conducted so far")
    target_percentage: float = Field(default=75.0, description="Target attendance percentage")

class AttendanceCalculatorTool(BaseTool):
    name = "attendance_calculator"
    description = "Calculates current attendance and how many more classes a student needs to attend to reach a target attendance percentage."
    input_schema = AttendanceCalculatorInput

    def execute(self, current_attended: int, current_total: int, target_percentage: float = 75.0, **kwargs) -> dict:
        if current_total == 0:
            return {"error": "Total classes cannot be 0."}
        
        current_percent = (current_attended / current_total) * 100
        
        if current_percent >= target_percentage:
            return {
                "current_percentage": round(current_percent, 2),
                "status": f"Target already achieved. You can miss some classes.",
                "classes_needed": 0
            }
            
        # Formula: (attended + x) / (total + x) = target / 100
        # attended + x = (target/100) * total + (target/100) * x
        # x * (1 - target/100) = (target/100) * total - attended
        
        ratio = target_percentage / 100.0
        classes_needed = math.ceil((ratio * current_total - current_attended) / (1 - ratio))
        
        return {
            "current_percentage": round(current_percent, 2),
            "classes_needed": classes_needed,
            "target_percentage": target_percentage
        }

class RAGSearchInput(BaseModel):
    query: str = Field(..., description="The semantic query to search the knowledge base for")
    category: str = Field(default=None, description="Optional category filter (e.g. 'examinations', 'placements')")

class RAGSearchTool(BaseTool):
    name = "rag_search"
    description = "Searches the official VIT-AP university unstructured knowledge base for regulations, policies, and documents."
    input_schema = RAGSearchInput

    def execute(self, query: str, category: str = None, **kwargs) -> dict:
        db = SessionLocal()
        try:
            retriever = PGVectorRetriever(db)
            chunks = retriever.search(query, category=category, top_k=3)
            
            if not chunks:
                return {"result": "No sufficiently relevant verified VIT-AP information was found."}
                
            results = []
            for c in chunks:
                results.append({
                    "content": c.content,
                    "source": c.metadata.source,
                    "page": c.metadata.page,
                    "category": c.metadata.category
                })
            return {"retrieved_chunks": results}
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            db.close()

class StudentInfoLookupInput(BaseModel):
    student_id: str = Field(..., description="The ID of the student")

class StudentInfoLookupTool(BaseTool):
    name = "student_info_lookup"
    description = "Retrieves structured student data such as branch, CGPA, and backlog count from the database."
    input_schema = StudentInfoLookupInput

    def execute(self, student_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            if not student:
                return {"error": f"Student with ID {student_id} not found."}
            return {
                "student_id": student.student_id,
                "name": student.name,
                "program": student.program,
                "branch": student.branch,
                "year": student.year,
                "cgpa": student.cgpa,
                "backlogs": student.backlogs,
                "data_type": student.data_type
            }
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            db.close()

class PlacementEligibilityInput(BaseModel):
    company_id: str = Field(..., description="The ID of the company")
    student_id: str = Field(..., description="The ID of the student")

class PlacementEligibilityTool(BaseTool):
    name = "placement_eligibility_check"
    description = "Checks if a specific student is eligible for a specific company's placement drive."
    input_schema = PlacementEligibilityInput

    def execute(self, company_id: str, student_id: str, **kwargs) -> dict:
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.student_id == student_id).first()
            company = db.query(Company).filter(Company.company_id == company_id).first()
            
            if not student:
                return {"error": f"Student {student_id} not found."}
            if not company:
                return {"error": f"Company {company_id} not found."}
                
            eligible = True
            reasons = []
            
            if student.cgpa < company.minimum_cgpa:
                eligible = False
                reasons.append(f"Student CGPA ({student.cgpa}) is below company minimum ({company.minimum_cgpa}).")
                
            if student.backlogs > company.maximum_backlogs:
                eligible = False
                reasons.append(f"Student has {student.backlogs} backlogs, which exceeds maximum allowed ({company.maximum_backlogs}).")
                
            program_branch = f"{student.program} {student.branch}"
            if program_branch not in company.eligible_programs:
                eligible = False
                reasons.append(f"Program/Branch '{program_branch}' is not in the eligible list: {company.eligible_programs}.")
                
            if eligible:
                return {"eligible": "YES", "reason": "Student meets all criteria.", "company": company.company_name}
            else:
                return {"eligible": "NO", "reason": "; ".join(reasons), "company": company.company_name}
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            db.close()

class FacultyLookupInput(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the faculty")
    department: Optional[str] = Field(default=None, description="Department name")

class FacultyLookupTool(BaseTool):
    name = "faculty_lookup"
    description = "Search faculty information from PostgreSQL."
    input_schema = FacultyLookupInput

    def execute(self, name: str = None, department: str = None, **kwargs) -> dict:
        db = SessionLocal()
        try:
            query = db.query(Faculty)
            if name:
                query = query.filter(Faculty.name.ilike(f"%{name}%"))
            if department:
                query = query.filter(Faculty.department.ilike(f"%{department}%"))
                
            results = query.limit(5).all()
            if not results:
                return {"error": "No faculty found matching the criteria."}
                
            faculty_list = []
            for f in results:
                faculty_list.append({
                    "name": f.name,
                    "department": f.department,
                    "designation": f.designation,
                    "courses": f.courses,
                    "email": f.official_email
                })
            return {"faculty": faculty_list}
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            db.close()

from ...models.schema import Course

class CourseLookupInput(BaseModel):
    course_code: Optional[str] = Field(default=None, description="Code of the course (e.g. CSE1001)")
    course_name: Optional[str] = Field(default=None, description="Name of the course")

class CourseLookupTool(BaseTool):
    name = "course_lookup"
    description = "Search course information from PostgreSQL."
    input_schema = CourseLookupInput

    def execute(self, course_code: str = None, course_name: str = None, **kwargs) -> dict:
        db = SessionLocal()
        try:
            query = db.query(Course)
            if course_code:
                query = query.filter(Course.course_code.ilike(f"%{course_code}%"))
            if course_name:
                query = query.filter(Course.course_name.ilike(f"%{course_name}%"))
                
            results = query.limit(5).all()
            if not results:
                return {"error": "No courses found matching the criteria."}
                
            course_list = []
            for c in results:
                course_list.append({
                    "course_code": c.course_code,
                    "course_name": c.course_name,
                    "department": c.department,
                    "credits": c.credits,
                    "semester": c.semester
                })
            return {"courses": course_list}
        except Exception as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            db.close()

class CGPACalculatorInput(BaseModel):
    grades: List[str] = Field(..., description="List of grades (e.g. ['S', 'A', 'B'])")
    credits: List[int] = Field(..., description="List of credits corresponding to the grades")

class CGPACalculatorTool(BaseTool):
    name = "cgpa_calculator"
    description = "Calculates SGPA/CGPA based on letter grades and credits."
    input_schema = CGPACalculatorInput

    def execute(self, grades: List[str], credits: List[int], **kwargs) -> dict:
        if len(grades) != len(credits):
            return {"error": "Length of grades and credits must match."}
            
        grade_points = {"S": 10, "A": 9, "B": 8, "C": 7, "D": 6, "E": 5, "F": 0, "N": 0}
        
        total_points = 0
        total_credits = sum(credits)
        
        if total_credits == 0:
            return {"error": "Total credits cannot be zero."}
            
        for g, c in zip(grades, credits):
            g = g.upper()
            if g not in grade_points:
                return {"error": f"Invalid grade: {g}"}
            total_points += grade_points[g] * c
            
        sgpa = total_points / total_credits
        return {
            "total_credits": total_credits,
            "total_grade_points": total_points,
            "sgpa": round(sgpa, 2)
        }

# Instantiate and register tools
from ..registry import registry

attendance_calculator_tool = AttendanceCalculatorTool()
rag_search_tool = RAGSearchTool()
student_info_lookup_tool = StudentInfoLookupTool()
placement_eligibility_tool = PlacementEligibilityTool()
faculty_lookup_tool = FacultyLookupTool()
course_lookup_tool = CourseLookupTool()
cgpa_calculator_tool = CGPACalculatorTool()

registry.register(attendance_calculator_tool)
registry.register(rag_search_tool)
registry.register(student_info_lookup_tool)
registry.register(placement_eligibility_tool)
registry.register(faculty_lookup_tool)
registry.register(course_lookup_tool)
registry.register(cgpa_calculator_tool)
