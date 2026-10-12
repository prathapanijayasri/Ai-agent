from typing import Dict, Any, List

class DatabaseInterface:
    """
    Interface for querying structured VIT-AP relational data via PostgreSQL.
    Provides methods to query students, faculty, and placements.
    """

    def get_student_profile(self, student_id: str) -> Dict[str, Any]:
        """
        Retrieves public or authorized student information.
        """
        raise NotImplementedError("DB interface not implemented yet")

    def get_student_attendance(self, student_id: str, course_code: str = None) -> Dict[str, Any]:
        """
        Retrieves attendance records for a student.
        """
        raise NotImplementedError("DB interface not implemented yet")

    def get_placement_eligibility(self, company_id: str, student_id: str) -> bool:
        """
        Checks if a student meets the company's CGPA, backlog, and branch requirements.
        """
        raise NotImplementedError("DB interface not implemented yet")

    def search_faculty(self, name: str = None, department: str = None) -> List[Dict[str, Any]]:
        """
        Finds faculty members by name or department.
        """
        raise NotImplementedError("DB interface not implemented yet")

    def get_course_details(self, course_code: str) -> Dict[str, Any]:
        """
        Retrieves course syllabus, credits, and prerequisites.
        """
        raise NotImplementedError("DB interface not implemented yet")
