from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    program = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)
    backlogs = Column(Integer, default=0)
    data_type = Column(String, default="synthetic")

class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    courses = Column(JSON, default=list)
    official_email = Column(String, nullable=False)
    source = Column(String, default="synthetic")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=False)
    minimum_cgpa = Column(Float, nullable=False)
    maximum_backlogs = Column(Integer, default=0)
    eligible_programs = Column(JSON, default=list)
    minimum_10th_percentage = Column(Float, nullable=False)
    minimum_12th_percentage = Column(Float, nullable=False)
    other_requirements = Column(String, nullable=True)
    source = Column(String, default="synthetic")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True, nullable=False)
    course_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=True)
    source = Column(String, default="synthetic")
