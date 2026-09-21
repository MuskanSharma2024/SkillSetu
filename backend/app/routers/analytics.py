from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List

from app.database import get_db
from app.models import (
    User, Application, ProgramEnrollment, SkillProfile, Opportunity, Company,
    Institution, StudentProfile, CurriculumGapReport, AuditLog, OpportunitySkill, Skill
)
from app.schemas import (
    StudentDashboardAnalytics, ApplicantFunnelResponse, ApplicantFunnelItem,
    InstitutionAnalyticsSummary, AuditLogResponse
)
from app.dependencies import (
    get_current_user, require_student, require_industry, require_staff, require_institution_admin
)

router = APIRouter(prefix="/analytics", tags=["Dashboard Analytics"])

@router.get("/student", response_model=StudentDashboardAnalytics)
def get_student_analytics(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Analytics summary for Student dashboard."""
    total_apps = db.query(Application).filter(Application.user_id == current_user.id).count()
    active_apps = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.status.in_(["applied", "shortlisted", "interview", "offered"])
    ).count()
    
    enrolled_progs = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == current_user.id,
        ProgramEnrollment.status == "enrolled"
    ).count()
    
    completed_progs = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == current_user.id,
        ProgramEnrollment.status == "completed"
    ).count()
    
    verified_skills = db.query(SkillProfile).filter(
        SkillProfile.user_id == current_user.id,
        SkillProfile.is_verified == True
    ).count()

    return StudentDashboardAnalytics(
        total_applications=total_apps,
        active_applications=active_apps,
        enrolled_programs=enrolled_progs,
        completed_programs=completed_progs,
        verified_skills_count=verified_skills
    )

@router.get("/industry/funnel", response_model=ApplicantFunnelResponse)
def get_industry_applicant_funnel(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Visualizes applicant counts per stage per posting for Industry dashboard."""
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    opps = db.query(Opportunity).filter(Opportunity.company_id == comp.id).all()
    funnel_items = []
    
    for opp in opps:
        counts = db.query(Application.status, func.count(Application.id)).filter(
            Application.opportunity_id == opp.id
        ).group_by(Application.status).all()
        
        status_counts = {c[0]: c[1] for c in counts}
        funnel_items.append(ApplicantFunnelItem(
            opportunity_id=opp.id,
            title=opp.title,
            applied=status_counts.get("applied", 0),
            shortlisted=status_counts.get("shortlisted", 0),
            interview=status_counts.get("interview", 0),
            offered=status_counts.get("offered", 0),
            rejected=status_counts.get("rejected", 0)
        ))

    return ApplicantFunnelResponse(
        total_postings=len(opps),
        funnel=funnel_items
    )

@router.get("/industry/skill-trends")
def get_industry_skill_trends(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Trending skills required in the company's own postings."""
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")

    opps = db.query(Opportunity).filter(Opportunity.company_id == comp.id).all()
    opp_ids = [o.id for o in opps]
    
    if not opp_ids:
        return []

    # Get skill frequencies for these opportunities
    skills_freq = db.query(
        Skill.id, Skill.name, Skill.category, func.count(OpportunitySkill.id).label('freq')
    ).join(
        OpportunitySkill, OpportunitySkill.skill_id == Skill.id
    ).filter(
        OpportunitySkill.opportunity_id.in_(opp_ids)
    ).group_by(Skill.id).order_by(desc('freq')).all()

    trends = []
    for s in skills_freq:
        trends.append({
            "skill_id": s.id,
            "skill_name": s.name,
            "category": s.category,
            "frequency": s.freq,
            "trend": "rising" if s.freq > 1 else "stable"
        })

    return trends

@router.get("/institution/summary", response_model=InstitutionAnalyticsSummary)
def get_institution_summary(
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Participation and placement progress counts for Institution dashboard."""
    # Find institution ID based on staff role
    inst_id = None
    if current_user.role == "institution_admin":
        # Assume mapping logic; for demo, fetch first institution linked to them (or just the primary one)
        inst = db.query(Institution).first() # Simplified for demo
        inst_id = inst.id if inst else 1
    elif current_user.role == "academician":
        from app.models import AcademicianProfile
        acad = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
        inst_id = acad.institution_id if acad else 1

    student_ids = [s.user_id for s in db.query(StudentProfile).filter(StudentProfile.institution_id == inst_id).all()]
    
    if not student_ids:
        return InstitutionAnalyticsSummary(
            total_students=0, students_assessed=0, internships_applied=0, 
            internships_completed=0, active_gap_reports=0
        )

    total_students = len(student_ids)
    
    # Students who have at least one skill profile
    assessed_students = db.query(SkillProfile.user_id).filter(SkillProfile.user_id.in_(student_ids)).distinct().count()
    
    # Applications
    applied = db.query(Application).filter(Application.user_id.in_(student_ids)).count()
    completed = db.query(Application).filter(Application.user_id.in_(student_ids), Application.status == "completed").count()
    
    active_gaps = db.query(CurriculumGapReport).filter(
        CurriculumGapReport.institution_id == inst_id,
        CurriculumGapReport.status == "open",
        CurriculumGapReport.gap_score > 0
    ).count()

    return InstitutionAnalyticsSummary(
        total_students=total_students,
        students_assessed=assessed_students,
        internships_applied=applied,
        internships_completed=completed,
        active_gap_reports=active_gaps
    )

@router.get("/admin/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View key actions for accountability."""
    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    return logs

# --- Task E2: Academician Growth View ---
@router.get("/faculty/cohort-growth-trends")
def get_faculty_cohort_growth_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Task E2: Surface longitudinal skill growth trend data aggregated for an academician's student cohort.
    Task F4: Enforces minimum cohort size anonymization guarantee (min. 3 students required).
    """
    from app.models import AcademicianProfile, SkillProfileSnapshot
    acad = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
    inst_id = acad.institution_id if acad else 1

    students = db.query(StudentProfile).filter(StudentProfile.institution_id == inst_id).all()
    student_ids = [s.user_id for s in students]

    # Task F4 Anonymization Guarantee: Require minimum cohort size of 3
    if len(student_ids) < 3:
        return {
            "institution_id": inst_id,
            "cohort_student_count": len(student_ids),
            "anonymization_guarantee_met": False,
            "notice": "Cohort size must be at least 3 students to protect individual student privacy.",
            "aggregated_skills": []
        }

    snapshots = db.query(SkillProfileSnapshot).filter(
        SkillProfileSnapshot.user_id.in_(student_ids)
    ).all()

    skill_averages = {}
    for snap in snapshots:
        if snap.skill_id not in skill_averages:
            sk = db.query(Skill).filter(Skill.id == snap.skill_id).first()
            skill_averages[snap.skill_id] = {
                "skill_name": sk.name if sk else f"Skill #{snap.skill_id}",
                "scores": []
            }
        skill_averages[snap.skill_id]["scores"].append(snap.proficiency_score)

    results = []
    for sid, data in skill_averages.items():
        avg = sum(data["scores"]) / len(data["scores"])
        results.append({
            "skill_id": sid,
            "skill_name": data["skill_name"],
            "avg_proficiency": round(avg, 1),
            "total_assessments_logged": len(data["scores"])
        })

    return {
        "institution_id": inst_id,
        "cohort_student_count": len(student_ids),
        "anonymization_guarantee_met": True,
        "aggregated_skills": results
    }

