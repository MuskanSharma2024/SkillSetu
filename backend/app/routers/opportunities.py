from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
import datetime

from app.database import get_db
from app.models import (
    User, Company, Opportunity, OpportunitySkill, Skill, Application, 
    StudentProfile, SkillProfile, LearningProgram, ProgramSkill, 
    ProgramEnrollment, AcademicianProfile, Notification, AuditLog, PortfolioItem, HireOutcome
)
from app.schemas import (
    OpportunityCreate, OpportunityResponse, RequiredSkillDetail,
    ApplicationCreate, ApplicationResponse, ApplicationStatusUpdate, MentorFeedbackSubmit,
    LearningProgramCreate, LearningProgramResponse, ProgramEnrollmentResponse,
    HireOutcomeCreate, HireOutcomeResponse, ExternalApplicationCreate
)
from app.dependencies import (
    get_current_user, require_industry, require_student, 
    require_student_or_academician, require_all_authenticated
)
from app.routers.skills import refresh_curriculum_gap_reports_internal

router = APIRouter(prefix="/opportunities", tags=["Opportunities & Programs"])

# ==========================================
# 1. Opportunity Management
# ==========================================

@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opp_in: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Industry (or Institution Admin/Faculty) posts an opportunity with required skills."""
    
    # Identify company or institution for the user
    company_id = None
    if current_user.role == "industry":
        comp = db.query(Company).filter(Company.user_id == current_user.id).first()
        if not comp:
            raise HTTPException(status_code=400, detail="Company profile required to post opportunities.")
        company_id = comp.id
    elif current_user.role in ["academician", "institution_admin"]:
        # We can map them to a pseudo-company or link to institution if we want to expand models
        # For simplicity in this schema, we require 'industry' to have a Company.
        # But we also have "faculty" opportunities. We'll map them to a generic company or create one if missing
        comp = db.query(Company).filter(Company.user_id == current_user.id).first()
        if not comp:
            comp = Company(
                user_id=current_user.id,
                name=f"{current_user.full_name} (Academic Rep)",
                industry_sector="Education / Research"
            )
            db.add(comp)
            db.commit()
            db.refresh(comp)
        company_id = comp.id
    else:
        raise HTTPException(status_code=403, detail="Students cannot post opportunities.")

    new_opp = Opportunity(
        company_id=company_id,
        title=opp_in.title,
        opportunity_type=opp_in.opportunity_type,
        target_role=opp_in.target_role,
        description=opp_in.description,
        location=opp_in.location,
        stipend_salary=opp_in.stipend_salary,
        deadline=opp_in.deadline,
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)

    # Add required skills
    for req_skill in opp_in.required_skills:
        skill = db.query(Skill).filter(Skill.id == req_skill.skill_id).first()
        if skill:
            os_link = OpportunitySkill(
                opportunity_id=new_opp.id,
                skill_id=skill.id,
                min_proficiency=req_skill.min_proficiency,
                importance_weight=req_skill.importance_weight
            )
            db.add(os_link)
    db.commit()
    db.refresh(new_opp)
    
    return _format_opportunity(new_opp, db)

@router.get("", response_model=List[OpportunityResponse])
def browse_opportunities(
    search: Optional[str] = None,
    skill_id: Optional[int] = None,
    opportunity_type: Optional[str] = None,
    target_role: Optional[str] = None,
    location: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Student/Faculty browse & search opportunities with filters."""
    query = db.query(Opportunity).filter(Opportunity.is_active == True)
    
    # Filter by target role (student vs faculty)
    if target_role:
        query = query.filter(Opportunity.target_role == target_role)
    else:
        # Defaults based on role
        if current_user.role == "student":
            query = query.filter(Opportunity.target_role == "student")
        elif current_user.role == "academician":
            query = query.filter(Opportunity.target_role == "faculty")
    
    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)
        
    if location:
        query = query.filter(Opportunity.location.ilike(f"%{location}%"))
        
    if search:
        query = query.filter(
            or_(
                Opportunity.title.ilike(f"%{search}%"),
                Opportunity.description.ilike(f"%{search}%")
            )
        )
        
    if skill_id:
        query = query.join(OpportunitySkill).filter(OpportunitySkill.skill_id == skill_id)

    opps = query.order_by(Opportunity.created_at.desc()).all()
    
    results = []
    for opp in opps:
        formatted = _format_opportunity(opp, db)
        formatted.applicant_match_score = _calculate_match_score(current_user, opp, db)
        results.append(formatted)
        
    return results

@router.get("/company/my-postings", response_model=List[OpportunityResponse])
def get_company_postings(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Industry partner view of their own active/past postings."""
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        return []
    opps = db.query(Opportunity).filter(Opportunity.company_id == comp.id).order_by(desc(Opportunity.created_at)).all()
    return [_format_opportunity(o, db) for o in opps]

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    formatted = _format_opportunity(opp, db)
    formatted.applicant_match_score = _calculate_match_score(current_user, opp, db)
    return formatted

def _format_opportunity(opp: Opportunity, db: Session) -> OpportunityResponse:
    company = db.query(Company).filter(Company.id == opp.company_id).first()
    skills_linked = db.query(OpportunitySkill).filter(OpportunitySkill.opportunity_id == opp.id).all()
    
    skills_detail = []
    for link in skills_linked:
        sk = db.query(Skill).filter(Skill.id == link.skill_id).first()
        if sk:
            skills_detail.append(RequiredSkillDetail(
                skill_id=sk.id,
                skill_name=sk.name,
                category=sk.category,
                min_proficiency=link.min_proficiency,
                importance_weight=link.importance_weight
            ))
            
    # Need to convert SQLAlchemy objects to Pydantic format correctly using dict
    # Calculate trust score for company
    trust_score = _calculate_trust_score(opp.company_id, db)

    return OpportunityResponse(
        id=opp.id,
        company_id=opp.company_id,
        company_name=company.name if company else "Unknown",
        title=opp.title,
        opportunity_type=opp.opportunity_type,
        target_role=opp.target_role,
        description=opp.description,
        location=opp.location,
        stipend_salary=opp.stipend_salary,
        deadline=opp.deadline,
        is_active=opp.is_active,
        skills=skills_detail,
        trust_score=trust_score,
        created_at=opp.created_at
    )

def _calculate_trust_score(company_id: int, db: Session) -> float:
    # Task D3: Posting Trust Score = f(historical conversion rate, average response time, hire outcome ratings & retention)
    opps = db.query(Opportunity).filter(Opportunity.company_id == company_id).all()
    opp_ids = [o.id for o in opps]
    if not opp_ids:
        return 85.0

    apps = db.query(Application).filter(Application.opportunity_id.in_(opp_ids)).all()
    if not apps:
        return 85.0

    total_apps = len(apps)
    successful_apps = sum(1 for a in apps if a.status in ["offered", "completed", "shortlisted"])
    conversion_rate = (successful_apps / total_apps) if total_apps > 0 else 0.5

    app_ids = [a.id for a in apps]
    outcomes = db.query(HireOutcome).filter(HireOutcome.application_id.in_(app_ids)).all()

    if outcomes:
        avg_rating = sum(o.performance_rating for o in outcomes) / len(outcomes)
        retention = sum(1 for o in outcomes if o.retained) / len(outcomes)
    else:
        avg_rating = 4.2
        retention = 0.85

    trust = round((0.4 * (conversion_rate * 100)) + (0.3 * (avg_rating / 5.0 * 100)) + (0.3 * (retention * 100)), 1)
    return max(50.0, min(99.0, trust))

def _calculate_match_score(user: User, opp: Opportunity, db: Session) -> float:
    req_skills = db.query(OpportunitySkill).filter(OpportunitySkill.opportunity_id == opp.id).all()
    if not req_skills:
        return 70.0 # Default if no specific skills tagged
        
    user_skills = {
        sp.skill_id: sp.proficiency_score
        for sp in db.query(SkillProfile).filter(SkillProfile.user_id == user.id).all()
    }
    
    total_weight = sum(rs.importance_weight for rs in req_skills)
    weighted_score = 0.0
    
    for rs in req_skills:
        user_score = user_skills.get(rs.skill_id, 0.0)
        if user_score >= rs.min_proficiency:
            weighted_score += rs.importance_weight * 1.0
        elif user_score > 0:
            ratio = user_score / rs.min_proficiency
            weighted_score += rs.importance_weight * ratio
            
    return round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 50.0

# ==========================================
# 2. Applications Flow
# ==========================================

@router.post("/{opportunity_id}/apply", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_opportunity(
    opportunity_id: int,
    app_in: ApplicationCreate,
    current_user: User = Depends(require_student_or_academician),
    db: Session = Depends(get_db)
):
    """Student or Academician applies to an opportunity."""
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
        
    if opp.target_role == "student" and current_user.role != "student":
        raise HTTPException(status_code=403, detail="This opportunity is targeted for students.")
    if opp.target_role == "faculty" and current_user.role not in ["academician", "institution_admin"]:
        raise HTTPException(status_code=403, detail="This opportunity is targeted for faculty.")
        
    if not opp.is_active:
        raise HTTPException(status_code=400, detail="This opportunity is no longer active.")
        
    existing = db.query(Application).filter(Application.user_id == current_user.id, Application.opportunity_id == opp.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You have already applied to this opportunity.")
        
    match_score = _calculate_match_score(current_user, opp, db)
    
    # Retrieve resume
    resume_link = None
    if current_user.role == "student":
        sp = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
        if sp:
            resume_link = sp.resume_url
            
    new_app = Application(
        opportunity_id=opp.id,
        user_id=current_user.id,
        match_score=match_score,
        status="applied",
        cover_note=app_in.cover_note,
        resume_link=resume_link,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    # Audit Log
    db.add(AuditLog(
        user_id=current_user.id,
        action_type="opportunity_applied",
        details=f"Applied to opportunity {opp.id} ({opp.title})"
    ))
    db.commit()
    
    # Notify company owner
    comp = db.query(Company).filter(Company.id == opp.company_id).first()
    if comp:
        db.add(Notification(
            user_id=comp.user_id,
            title="New Candidate Application",
            message=f"{current_user.full_name} applied to {opp.title} with a match score of {match_score}%.",
            category="application"
        ))
        db.commit()
        
    return _format_application(new_app, db)

@router.post("/external/track", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def track_external_opportunity(
    track_in: ExternalApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Student applies to real internet posting and tracks application in SkillSetu."""
    # Find or create company
    comp = db.query(Company).filter(Company.name == track_in.company_name).first()
    if not comp:
        comp = Company(
            user_id=current_user.id,
            name=track_in.company_name,
            industry_sector="Technology & Software",
            website=track_in.url,
            location=track_in.location or "Global"
        )
        db.add(comp)
        db.commit()
        db.refresh(comp)

    # Find or create opportunity
    opp = db.query(Opportunity).filter(
        Opportunity.title == track_in.title,
        Opportunity.company_id == comp.id
    ).first()
    if not opp:
        opp = Opportunity(
            company_id=comp.id,
            title=track_in.title,
            opportunity_type=track_in.opportunity_type,
            target_role="student",
            description=f"External opportunity sourced live from internet: {track_in.url}",
            location=track_in.location or "Remote",
            stipend_salary=track_in.stipend_salary,
            is_active=True,
            created_at=datetime.datetime.utcnow()
        )
        db.add(opp)
        db.commit()
        db.refresh(opp)

    # Check if existing application
    existing = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.opportunity_id == opp.id
    ).first()
    if existing:
        return _format_application(existing, db)

    # Retrieve student resume
    sp = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    resume_link = sp.resume_url if sp else None

    new_app = Application(
        opportunity_id=opp.id,
        user_id=current_user.id,
        match_score=track_in.match_score or 85.0,
        status="applied",
        cover_note=track_in.cover_note or f"Applied via live portal: {track_in.url}",
        resume_link=resume_link,
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Audit log
    db.add(AuditLog(
        user_id=current_user.id,
        action_type="external_opportunity_tracked",
        details=f"Tracked external job application: {track_in.title} at {track_in.company_name}"
    ))
    db.commit()

    return _format_application(new_app, db)

@router.get("/company/applicants", response_model=List[ApplicationResponse])
def get_company_applicants(
    opportunity_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Industry views applicants, sorted by match score + eligibility."""
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        return []
        
    query = db.query(Application).join(Opportunity).filter(Opportunity.company_id == comp.id)
    
    if opportunity_id:
        query = query.filter(Application.opportunity_id == opportunity_id)
    if status:
        query = query.filter(Application.status == status)
        
    apps = query.order_by(desc(Application.match_score), desc(Application.created_at)).all()
    return [_format_application(a, db) for a in apps]

@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Industry updates application status (shortlisted, interview, offered, etc)."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    opp = db.query(Opportunity).filter(Opportunity.id == app.opportunity_id).first()
    
    if not comp or opp.company_id != comp.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this application.")
        
    app.status = status_update.status
    app.updated_at = datetime.datetime.utcnow()
    
    # Send notification to applicant
    db.add(Notification(
        user_id=app.user_id,
        title="Application Status Update",
        message=f"Your application for '{opp.title}' has been moved to status: {status_update.status}.",
        category="application"
    ))
    
    # Audit Log
    db.add(AuditLog(
        user_id=current_user.id,
        action_type="application_status_updated",
        details=f"Updated application {app.id} to {status_update.status}"
    ))
    
    db.commit()
    db.refresh(app)
    return _format_application(app, db)

@router.post("/applications/{application_id}/feedback", response_model=ApplicationResponse)
def submit_mentor_feedback(
    application_id: int,
    feedback: MentorFeedbackSubmit,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Mentor submits feedback and rating on completion of internship/project."""
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    app.mentor_rating = feedback.mentor_rating
    app.mentor_feedback = feedback.mentor_feedback
    app.completion_date = datetime.datetime.utcnow()
    app.status = "completed"
    app.updated_at = datetime.datetime.utcnow()
    
    # Notify student
    db.add(Notification(
        user_id=app.user_id,
        title="Mentor Feedback Received!",
        message=f"You received a mentor rating of {feedback.mentor_rating}/5.0 for '{app.opportunity.title}'.",
        category="portfolio"
    ))
    
    # Portfolio Item for Internship Completion
    db.add(PortfolioItem(
        user_id=app.user_id,
        item_type="internship_completion",
        title=f"Completed: {app.opportunity.title}",
        description=f"Received a mentor rating of {feedback.mentor_rating}/5.0. Feedback: {feedback.mentor_feedback}",
        reference_id=app.id
    ))
    
    # Audit Log
    db.add(AuditLog(
        user_id=current_user.id,
        action_type="feedback_submitted",
        details=f"Submitted mentor feedback for application {app.id}"
    ))
    
    db.commit()
    db.refresh(app)
    return _format_application(app, db)

# --- Tasks D1 & D2: Post-Hire Outcome Reporting ---
@router.post("/applications/{application_id}/hire-outcome", response_model=HireOutcomeResponse, status_code=status.HTTP_201_CREATED)
def submit_hire_outcome(
    application_id: int,
    outcome_in: HireOutcomeCreate,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """
    Task D2: Industry partner submits 3-month or 6-month post-hire outcome report.
    """
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application record not found.")

    outcome = HireOutcome(
        application_id=application_id,
        reported_by_user_id=current_user.id,
        interval=outcome_in.interval,
        retained=outcome_in.retained,
        performance_rating=outcome_in.performance_rating,
        reported_at=datetime.datetime.utcnow()
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    student_user = db.query(User).filter(User.id == app.user_id).first()
    comp = db.query(Company).filter(Company.id == app.opportunity.company_id).first() if app.opportunity else None

    return HireOutcomeResponse(
        id=outcome.id,
        application_id=application_id,
        opportunity_title=app.opportunity.title if app.opportunity else "Placement",
        student_name=student_user.full_name if student_user else "Student Candidate",
        company_name=comp.name if comp else "Industry Partner",
        interval=outcome.interval,
        retained=outcome.retained,
        performance_rating=outcome.performance_rating,
        reported_at=outcome.reported_at
    )

@router.get("/company/hire-outcomes/pending", response_model=List[ApplicationResponse])
def get_pending_hire_outcome_reminders(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """
    Task D2: Lists selections eligible for 3-month or 6-month outcome reporting reminders.
    """
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        return []

    opp_ids = [o.id for o in db.query(Opportunity).filter(Opportunity.company_id == comp.id).all()]
    apps = db.query(Application).filter(
        Application.opportunity_id.in_(opp_ids),
        Application.status.in_(["offered", "completed"])
    ).all()

    return [_format_application(a, db) for a in apps]

@router.get("/applications/me", response_model=List[ApplicationResponse])
def get_my_applications(
    current_user: User = Depends(require_student_or_academician),
    db: Session = Depends(get_db)
):
    """Student/Faculty view of their own applications."""
    apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(desc(Application.updated_at)).all()
    return [_format_application(a, db) for a in apps]

def _format_application(app: Application, db: Session) -> ApplicationResponse:
    opp = db.query(Opportunity).filter(Opportunity.id == app.opportunity_id).first()
    comp = db.query(Company).filter(Company.id == opp.company_id).first() if opp else None
    user = db.query(User).filter(User.id == app.user_id).first()
    
    return ApplicationResponse(
        id=app.id,
        opportunity_id=app.opportunity_id,
        opportunity_title=opp.title if opp else "Unknown",
        company_name=comp.name if comp else "Unknown",
        user_id=app.user_id,
        applicant_name=user.full_name if user else "Unknown",
        applicant_email=user.email if user else "Unknown",
        applicant_role=user.role if user else "Unknown",
        match_score=app.match_score,
        status=app.status,
        cover_note=app.cover_note,
        resume_link=app.resume_link,
        mentor_rating=app.mentor_rating,
        mentor_feedback=app.mentor_feedback,
        created_at=app.created_at,
        updated_at=app.updated_at
    )

# ==========================================
# 3. Learning Programs Flow
# ==========================================

@router.post("/programs", response_model=LearningProgramResponse, status_code=status.HTTP_201_CREATED)
def create_learning_program(
    prog_in: LearningProgramCreate,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Company publishes training/certification program with skills covered."""
    comp = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not comp:
        raise HTTPException(status_code=400, detail="Company profile required")
        
    prog = LearningProgram(
        company_id=comp.id,
        title=prog_in.title,
        program_type=prog_in.program_type,
        description=prog_in.description,
        duration_weeks=prog_in.duration_weeks,
        is_active=True,
        created_at=datetime.datetime.utcnow()
    )
    db.add(prog)
    db.commit()
    db.refresh(prog)
    
    for ps in prog_in.skills_covered:
        sk = db.query(Skill).filter(Skill.id == ps.skill_id).first()
        if sk:
            db.add(ProgramSkill(
                program_id=prog.id,
                skill_id=sk.id,
                granted_proficiency=ps.granted_proficiency
            ))
    db.commit()
    db.refresh(prog)
    return _format_program(prog, current_user.id, db)

@router.get("/programs", response_model=List[LearningProgramResponse])
def get_learning_programs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Students browse learning programs."""
    progs = db.query(LearningProgram).filter(LearningProgram.is_active == True).order_by(desc(LearningProgram.created_at)).all()
    return [_format_program(p, current_user.id, db) for p in progs]

@router.post("/programs/{program_id}/enroll", response_model=ProgramEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_program(
    program_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Student enrolls in a learning program."""
    prog = db.query(LearningProgram).filter(LearningProgram.id == program_id).first()
    if not prog or not prog.is_active:
        raise HTTPException(status_code=404, detail="Program not found or inactive")
        
    existing = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.program_id == prog.id,
        ProgramEnrollment.user_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this program")
        
    enrollment = ProgramEnrollment(
        program_id=prog.id,
        user_id=current_user.id,
        status="enrolled",
        enrolled_at=datetime.datetime.utcnow()
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return _format_enrollment(enrollment, db)

@router.get("/programs/my-enrollments", response_model=List[ProgramEnrollmentResponse])
def get_my_enrollments(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Student tracking of enrollment status."""
    enrollments = db.query(ProgramEnrollment).filter(ProgramEnrollment.user_id == current_user.id).order_by(desc(ProgramEnrollment.enrolled_at)).all()
    return [_format_enrollment(e, db) for e in enrollments]

@router.post("/programs/enrollments/{enrollment_id}/complete", response_model=ProgramEnrollmentResponse)
def complete_program_enrollment(
    enrollment_id: int,
    current_user: User = Depends(require_all_authenticated),
    db: Session = Depends(get_db)
):
    """
    Task 11: On program completion, update the student's `skill_profiles` with newly verified skills.
    Can be triggered by Industry (certifying) or Student (self-certifying for demo purposes).
    """
    enrollment = db.query(ProgramEnrollment).filter(ProgramEnrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    prog = db.query(LearningProgram).filter(LearningProgram.id == enrollment.program_id).first()
    
    # Mark completed
    enrollment.status = "completed"
    enrollment.completed_at = datetime.datetime.utcnow()
    
    # Update Skill Profiles
    prog_skills = db.query(ProgramSkill).filter(ProgramSkill.program_id == prog.id).all()
    verified_skills = []
    
    for ps in prog_skills:
        skill = db.query(Skill).filter(Skill.id == ps.skill_id).first()
        if not skill: continue
        
        prof = db.query(SkillProfile).filter(
            SkillProfile.user_id == enrollment.user_id,
            SkillProfile.skill_id == skill.id
        ).first()
        
        if prof:
            prof.proficiency_score = max(prof.proficiency_score, ps.granted_proficiency)
            prof.is_verified = True
            prof.last_assessed_at = datetime.datetime.utcnow()
        else:
            prof = SkillProfile(
                user_id=enrollment.user_id,
                skill_id=skill.id,
                proficiency_score=ps.granted_proficiency,
                is_verified=True,
                last_assessed_at=datetime.datetime.utcnow()
            )
            db.add(prof)
        verified_skills.append(skill.name)
            
    # Notify Student
    if verified_skills:
        db.add(Notification(
            user_id=enrollment.user_id,
            title="🎉 Program Completed & Skills Verified!",
            message=f"You successfully completed '{prog.title}'. Verified skills added to your profile: {', '.join(verified_skills)}.",
            category="portfolio"
        ))
        
    # Portfolio Item
    db.add(PortfolioItem(
        user_id=enrollment.user_id,
        item_type="program_completion",
        title=f"Certified: {prog.title}",
        description=f"Completed {prog.duration_weeks}-week {prog.program_type}. Verified skills: {', '.join(verified_skills)}",
        reference_id=prog.id
    ))
    
    # Audit Log
    db.add(AuditLog(
        user_id=current_user.id,
        action_type="program_completed",
        details=f"Completed program {prog.id} for user {enrollment.user_id}"
    ))
        
    db.commit()
    db.refresh(enrollment)
    
    # If the student's institution is tied to a curriculum report, trigger a refresh
    student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == enrollment.user_id).first()
    if student_prof and student_prof.institution_id:
        refresh_curriculum_gap_reports_internal(student_prof.institution_id, db)
        db.commit()
        
    return _format_enrollment(enrollment, db)

def _format_program(prog: LearningProgram, user_id: int, db: Session) -> LearningProgramResponse:
    comp = db.query(Company).filter(Company.id == prog.company_id).first()
    pskills = db.query(ProgramSkill).filter(ProgramSkill.program_id == prog.id).all()
    
    skills_list = []
    for ps in pskills:
        sk = db.query(Skill).filter(Skill.id == ps.skill_id).first()
        if sk:
            skills_list.append({
                "skill_id": sk.id,
                "skill_name": sk.name,
                "granted_proficiency": ps.granted_proficiency
            })
            
    # Check enrollment
    enrollment = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.program_id == prog.id,
        ProgramEnrollment.user_id == user_id
    ).first()
    
    return LearningProgramResponse(
        id=prog.id,
        company_id=prog.company_id,
        company_name=comp.name if comp else "Unknown",
        title=prog.title,
        program_type=prog.program_type,
        description=prog.description,
        duration_weeks=prog.duration_weeks,
        is_active=prog.is_active,
        skills=skills_list,
        is_enrolled=bool(enrollment),
        enrollment_status=enrollment.status if enrollment else None,
        created_at=prog.created_at
    )

def _format_enrollment(enr: ProgramEnrollment, db: Session) -> ProgramEnrollmentResponse:
    prog = db.query(LearningProgram).filter(LearningProgram.id == enr.program_id).first()
    return ProgramEnrollmentResponse(
        id=enr.id,
        program_id=enr.program_id,
        program_title=prog.title if prog else "Unknown",
        user_id=enr.user_id,
        status=enr.status,
        enrolled_at=enr.enrolled_at,
        completed_at=enr.completed_at
    )
