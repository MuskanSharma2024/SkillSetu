from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, StudentProfile, Company, AcademicianProfile, Institution, SkillProfile, Opportunity
from app.schemas import DashboardShellResponse
from app.dependencies import (
    require_student, require_industry, require_academician, require_institution_admin
)

router = APIRouter(prefix="/dashboards", tags=["Dashboards (Base Shells)"])

@router.get("/student", response_model=DashboardShellResponse)
def get_student_dashboard(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Base student dashboard shell with role verification and summary metrics."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    skills_count = db.query(SkillProfile).filter(SkillProfile.user_id == current_user.id).count()

    return DashboardShellResponse(
        role="student",
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title="Student Innovation & Placement Hub",
        summary={
            "degree": profile.degree if profile else "Not Set",
            "branch": profile.branch if profile else "Not Set",
            "grad_year": profile.grad_year if profile else 2026,
            "resume_uploaded": bool(profile and profile.resume_url),
            "assessed_skills": skills_count,
            "profile_completed": bool(profile and profile.degree and profile.branch)
        },
        available_modules=[
            "Profile Management",
            "Skill Assessment Questionnaire",
            "Skill Gap & Benchmark Radar",
            "Smart Opportunity Recommendations",
            "Live Application Tracker",
            "Verified Portfolio Builder"
        ]
    )

@router.get("/industry", response_model=DashboardShellResponse)
def get_industry_dashboard(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Base industry partner dashboard shell with recruitment & skill demand summary."""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    postings_count = 0
    if company:
        postings_count = db.query(Opportunity).filter(Opportunity.company_id == company.id).count()

    return DashboardShellResponse(
        role="industry",
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title="Industry Partner Talent & Curriculum Console",
        summary={
            "company_name": company.name if company else "Enterprise Profile",
            "sector": company.industry_sector if company else "Technology",
            "active_postings": postings_count,
            "talent_pipeline_active": True
        },
        available_modules=[
            "Enterprise Profile",
            "Opportunity & Internship Posting",
            "Candidate Shortlisting & Scoring",
            "Industry Skill-Demand Aggregator",
            "Learning & Mentorship Programs",
            "Curriculum Advisory Engagement"
        ]
    )

@router.get("/academician", response_model=DashboardShellResponse)
def get_academician_dashboard(
    current_user: User = Depends(require_academician),
    db: Session = Depends(get_db)
):
    """Base academician dashboard shell with curriculum feedback loop highlights."""
    profile = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
    inst_name = "Independent"
    if profile and profile.institution_id:
        inst = db.query(Institution).filter(Institution.id == profile.institution_id).first()
        if inst:
            inst_name = inst.name

    return DashboardShellResponse(
        role="academician",
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title="Faculty Academic & Curriculum Feedback Dashboard",
        summary={
            "department": profile.department if profile else "CSE",
            "designation": profile.designation if profile else "Faculty",
            "institution": inst_name,
            "curriculum_feedback_loop_ready": True
        },
        available_modules=[
            "Faculty Profile & Affiliation",
            "⭐ Curriculum Gap-vs-Demand Reports",
            "⭐ Action Logging & Syllabus Upgrades",
            "Student Cohort Skill Analytics",
            "Faculty Internship & FDP Exchange",
            "Industry Advisory Feedback"
        ]
    )

@router.get("/institution", response_model=DashboardShellResponse)
def get_institution_dashboard(
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """Base institution admin dashboard shell with macro institutional stats."""
    total_students = db.query(StudentProfile).count()
    total_faculty = db.query(AcademicianProfile).count()

    return DashboardShellResponse(
        role="institution_admin",
        user_id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        title="Institution Governance & Placement Intelligence",
        summary={
            "total_registered_students": total_students,
            "total_faculty_members": total_faculty,
            "curriculum_alignment_system": "Operational",
            "sih_evaluator_ready": True
        },
        available_modules=[
            "Institution Setup & Accreditation Code",
            "Student Cohort Progress Roster",
            "Faculty Directory",
            "⭐ Macro Curriculum Feedback View",
            "Placement & Skill Trends Overview",
            "Audit Logs & Compliance"
        ]
    )
