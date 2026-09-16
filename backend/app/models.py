import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    # Roles: 'student', 'industry', 'academician', 'institution_admin'
    role = Column(String(50), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    company_profile = relationship("Company", back_populates="user", uselist=False, cascade="all, delete-orphan")
    academician_profile = relationship("AcademicianProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    skill_assessments = relationship("SkillAssessment", back_populates="user", cascade="all, delete-orphan")
    skill_profiles = relationship("SkillProfile", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    enrollments = relationship("ProgramEnrollment", back_populates="user", cascade="all, delete-orphan")

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True) # e.g. AISHE / Institute Code
    website = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    students = relationship("StudentProfile", back_populates="institution")
    academicians = relationship("AcademicianProfile", back_populates="institution")
    curriculum_reports = relationship("CurriculumGapReport", back_populates="institution")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True)
    enrollment_no = Column(String(100), nullable=True, index=True)
    degree = Column(String(100), nullable=True)     # e.g., B.Tech, M.Tech, MCA, BCA
    branch = Column(String(100), nullable=True)     # e.g., Computer Science, Data Science
    grad_year = Column(Integer, nullable=True)      # e.g., 2026
    career_interests = Column(Text, nullable=True)  # JSON-encoded array or comma-separated tags
    resume_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="student_profile")
    institution = relationship("Institution", back_populates="students")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    industry_sector = Column(String(100), nullable=False) # e.g. Information Technology, Manufacturing, Healthcare
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="company_profile")
    opportunities = relationship("Opportunity", back_populates="company", cascade="all, delete-orphan")
    learning_programs = relationship("LearningProgram", back_populates="company", cascade="all, delete-orphan")

class AcademicianProfile(Base):
    __tablename__ = "academician_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True)
    department = Column(String(100), nullable=False) # e.g., Computer Science & Engineering
    designation = Column(String(100), nullable=False) # e.g., Associate Professor, HOD
    faculty_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="academician_profile")
    institution = relationship("Institution", back_populates="academicians")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False) # technical, soft, domain, tools
    description = Column(Text, nullable=True)
    industry_benchmark = Column(Float, default=75.0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    skill_profiles = relationship("SkillProfile", back_populates="skill")
    opportunity_links = relationship("OpportunitySkill", back_populates="skill")
    curriculum_reports = relationship("CurriculumGapReport", back_populates="skill")
    program_skills = relationship("ProgramSkill", back_populates="skill")

class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assessment_type = Column(String(50), default="diagnostic", nullable=False)
    responses = Column(Text, nullable=False)
    score_summary = Column(Text, nullable=True)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="skill_assessments")

class SkillProfile(Base):
    __tablename__ = "skill_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_score = Column(Float, default=0.0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_assessed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="skill_profiles")
    skill = relationship("Skill", back_populates="skill_profiles")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    # Types: internship, job, apprenticeship, project, fdp, consultancy, sabbatical, research_collab
    opportunity_type = Column(String(50), nullable=False)
    # Target audience: 'student' or 'faculty'
    target_role = Column(String(20), default="student", nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    stipend_salary = Column(String(100), nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="opportunities")
    required_skills = relationship("OpportunitySkill", back_populates="opportunity", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="opportunity", cascade="all, delete-orphan")

class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    min_proficiency = Column(Float, default=70.0, nullable=False)
    importance_weight = Column(Float, default=1.0, nullable=False)

    opportunity = relationship("Opportunity", back_populates="required_skills")
    skill = relationship("Skill", back_populates="opportunity_links")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    match_score = Column(Float, default=0.0, nullable=False) # Computed snapshot match % at apply time
    # Statuses: applied, shortlisted, interview, offered, rejected, completed
    status = Column(String(50), default="applied", nullable=False, index=True)
    cover_note = Column(Text, nullable=True)
    resume_link = Column(String(500), nullable=True)
    
    # Task 8: Mentor feedback & completion record
    mentor_rating = Column(Float, nullable=True) # 1.0 to 5.0
    mentor_feedback = Column(Text, nullable=True)
    completion_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    opportunity = relationship("Opportunity", back_populates="applications")
    user = relationship("User", back_populates="applications")

class LearningProgram(Base):
    __tablename__ = "learning_programs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    # Types: training, certification, workshop, mentorship
    program_type = Column(String(50), default="certification", nullable=False)
    description = Column(Text, nullable=True)
    duration_weeks = Column(Integer, default=4, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="learning_programs")
    skills_covered = relationship("ProgramSkill", back_populates="program", cascade="all, delete-orphan")
    enrollments = relationship("ProgramEnrollment", back_populates="program", cascade="all, delete-orphan")

class ProgramSkill(Base):
    __tablename__ = "program_skills"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("learning_programs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    granted_proficiency = Column(Float, default=85.0, nullable=False) # Proficiency score awarded on completion

    program = relationship("LearningProgram", back_populates="skills_covered")
    skill = relationship("Skill", back_populates="program_skills")

class ProgramEnrollment(Base):
    __tablename__ = "program_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("learning_programs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Statuses: enrolled, in_progress, completed
    status = Column(String(50), default="enrolled", nullable=False)
    enrolled_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    program = relationship("LearningProgram", back_populates="enrollments")
    user = relationship("User", back_populates="enrollments")

class CurriculumGapReport(Base):
    __tablename__ = "curriculum_gap_reports"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    student_cohort_avg = Column(Float, default=0.0, nullable=False)
    industry_benchmark = Column(Float, default=75.0, nullable=False)
    gap_score = Column(Float, default=0.0, nullable=False)
    demand_frequency = Column(Integer, default=0, nullable=False)
    trend = Column(String(20), default="rising", nullable=False)
    recommendation_text = Column(Text, nullable=True)
    status = Column(String(50), default="open", nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="curriculum_reports")
    skill = relationship("Skill", back_populates="curriculum_reports")
    actions = relationship("CurriculumAction", back_populates="report", cascade="all, delete-orphan")

class CurriculumAction(Base):
    __tablename__ = "curriculum_actions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("curriculum_gap_reports.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(50), nullable=False)
    course_name = Column(String(255), nullable=False)
    action_notes = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    report = relationship("CurriculumGapReport", back_populates="actions")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    target_role = Column(String(50), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), default="curriculum_alert", nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="notifications")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents")
