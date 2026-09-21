from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import (
    User, Institution, AcademicianProfile, StudentProfile, SkillAssessment, 
    IntegrityFlag, SyllabusRevisionProposal, CurriculumGapReport, Skill, Notification
)
from app.schemas import (
    InstitutionResponse, InstitutionCreate,
    AcademicianProfileResponse, AcademicianProfileUpdate,
    IntegrityReviewSummary, IntegrityFlagResponse, GuardianConsentUpdate,
    SyllabusProposalResponse, SyllabusProposalStatusUpdate
)
from app.dependencies import require_institution_admin, require_academician

router = APIRouter(prefix="/institutions", tags=["Institutions & Academicians"])

@router.get("", response_model=List[InstitutionResponse])
def list_institutions(db: Session = Depends(get_db)):
    """List all registered institutions for selection."""
    return db.query(Institution).all()

@router.post("", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
def create_institution(
    inst_in: InstitutionCreate,
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """Register a new institution (restricted to institution admins)."""
    existing = db.query(Institution).filter(
        (Institution.code == inst_in.code) | (Institution.name == inst_in.name)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An institution with this code or name already exists."
        )

    inst = Institution(
        name=inst_in.name,
        code=inst_in.code,
        website=inst_in.website,
        address=inst_in.address,
        contact_email=inst_in.contact_email
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst

@router.get("/academicians/profile", response_model=AcademicianProfileResponse)
def get_my_academician_profile(
    current_user: User = Depends(require_academician),
    db: Session = Depends(get_db)
):
    """Retrieve academician profile of the authenticated faculty member."""
    profile = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
    if not profile:
        default_inst = db.query(Institution).first()
        profile = AcademicianProfile(
            user_id=current_user.id,
            institution_id=default_inst.id if default_inst else None,
            department="Computer Science & Engineering",
            designation="Assistant Professor"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    inst_name = None
    if profile.institution_id:
        inst = db.query(Institution).filter(Institution.id == profile.institution_id).first()
        if inst:
            inst_name = inst.name

    return AcademicianProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        institution_id=profile.institution_id,
        institution_name=inst_name,
        department=profile.department,
        designation=profile.designation,
        faculty_id=profile.faculty_id,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.put("/academicians/profile", response_model=AcademicianProfileResponse)
def update_my_academician_profile(
    update_data: AcademicianProfileUpdate,
    current_user: User = Depends(require_academician),
    db: Session = Depends(get_db)
):
    """Update academician profile and institution linkage."""
    profile = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
    if not profile:
        profile = AcademicianProfile(user_id=current_user.id)
        db.add(profile)

    if update_data.institution_id is not None:
        inst = db.query(Institution).filter(Institution.id == update_data.institution_id).first()
        if not inst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found."
            )
        profile.institution_id = update_data.institution_id

    if update_data.department is not None:
        profile.department = update_data.department
    if update_data.designation is not None:
        profile.designation = update_data.designation
    if update_data.faculty_id is not None:
        profile.faculty_id = update_data.faculty_id

    db.commit()
    db.refresh(profile)

    inst_name = None
    if profile.institution_id:
        inst = db.query(Institution).filter(Institution.id == profile.institution_id).first()
        if inst:
            inst_name = inst.name

    return AcademicianProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        institution_id=profile.institution_id,
        institution_name=inst_name,
        department=profile.department,
        designation=profile.designation,
        faculty_id=profile.faculty_id,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

    return inst

# ==========================================
# SRS Delta Institution Admin Endpoints
# ==========================================

# --- Task A5: Assessment Integrity Review Dashboard ---
@router.get("/integrity-flags", response_model=List[IntegrityReviewSummary])
def get_integrity_flag_reviews(
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """
    Task A5: Institution Admin view listing flagged assessments for review.
    Does not expose raw behavioural signal beyond derived flag counts & flag list.
    """
    flags = db.query(IntegrityFlag).all()
    by_assessment = {}
    for f in flags:
        if f.assessment_id not in by_assessment:
            by_assessment[f.assessment_id] = []
        by_assessment[f.assessment_id].append(f)

    results = []
    for aid, flist in by_assessment.items():
        assessment = db.query(SkillAssessment).filter(SkillAssessment.id == aid).first()
        if not assessment:
            continue
        student_user = db.query(User).filter(User.id == assessment.user_id).first()

        counts = {}
        for f in flist:
            counts[f.flag_type] = counts.get(f.flag_type, 0) + 1

        flag_responses = [
            IntegrityFlagResponse(
                id=f.id,
                assessment_id=f.assessment_id,
                flag_type=f.flag_type,
                raw_signal=f.raw_signal,
                created_at=f.created_at
            ) for f in flist
        ]

        results.append(IntegrityReviewSummary(
            assessment_id=aid,
            student_id=assessment.user_id,
            student_name=student_user.full_name if student_user else "Student",
            assessment_completed_at=assessment.completed_at,
            flag_counts=counts,
            total_flags=len(flist),
            flags=flag_responses
        ))

    results.sort(key=lambda x: x.total_flags, reverse=True)
    return results

# --- Task B3: Guardian Consent Gate Management ---
@router.patch("/students/{student_id}/guardian-consent")
def update_student_guardian_consent(
    student_id: int,
    update_in: GuardianConsentUpdate,
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """
    Task B3: Institution Admin updates guardian/institutional consent status for minor students.
    """
    sp = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
    if not sp:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    sp.guardian_consent_status = update_in.status
    db.commit()
    return {"status": "success", "user_id": student_id, "guardian_consent_status": sp.guardian_consent_status}

# --- Task F3: Institution Admin Review/Approval Flow ---
@router.get("/curriculum-proposals", response_model=List[SyllabusProposalResponse])
def list_curriculum_proposals(
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """
    Task F3: List all syllabus revision proposals submitted by academicians for review.
    """
    proposals = db.query(SyllabusRevisionProposal).order_by(SyllabusRevisionProposal.created_at.desc()).all()
    results = []

    for p in proposals:
        submitter = db.query(User).filter(User.id == p.submitted_by).first()
        report = db.query(CurriculumGapReport).filter(CurriculumGapReport.id == p.curriculum_report_id).first()
        skill = db.query(Skill).filter(Skill.id == report.skill_id).first() if report else None

        results.append(SyllabusProposalResponse(
            id=p.id,
            curriculum_report_id=p.curriculum_report_id,
            skill_name=skill.name if skill else "Skill",
            submitted_by=p.submitted_by,
            academician_name=submitter.full_name if submitter else "Faculty Member",
            course_code=p.course_code,
            proposed_change=p.proposed_change,
            status=p.status,
            institution_admin_notes=p.institution_admin_notes,
            created_at=p.created_at,
            updated_at=p.updated_at
        ))
    return results

@router.patch("/curriculum-proposals/{proposal_id}/status", response_model=SyllabusProposalResponse)
def update_curriculum_proposal_status(
    proposal_id: int,
    status_in: SyllabusProposalStatusUpdate,
    current_user: User = Depends(require_institution_admin),
    db: Session = Depends(get_db)
):
    """
    Task F3: Approve or reject a submitted syllabus revision proposal and notify the submitting academician.
    """
    p = db.query(SyllabusRevisionProposal).filter(SyllabusRevisionProposal.id == proposal_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Syllabus proposal not found.")

    p.status = status_in.status
    if status_in.institution_admin_notes is not None:
        p.institution_admin_notes = status_in.institution_admin_notes

    # Send Notification to submitting academician
    db.add(Notification(
        user_id=p.submitted_by,
        title=f"Syllabus Proposal {status_in.status.upper()}",
        message=f"Your syllabus proposal for '{p.course_code}' was marked as '{status_in.status}' by Institution Admin.",
        category="curriculum_alert"
    ))

    db.commit()
    db.refresh(p)

    submitter = db.query(User).filter(User.id == p.submitted_by).first()
    report = db.query(CurriculumGapReport).filter(CurriculumGapReport.id == p.curriculum_report_id).first()
    skill = db.query(Skill).filter(Skill.id == report.skill_id).first() if report else None

    return SyllabusProposalResponse(
        id=p.id,
        curriculum_report_id=p.curriculum_report_id,
        skill_name=skill.name if skill else "Skill",
        submitted_by=p.submitted_by,
        academician_name=submitter.full_name if submitter else "Faculty Member",
        course_code=p.course_code,
        proposed_change=p.proposed_change,
        status=p.status,
        institution_admin_notes=p.institution_admin_notes,
        created_at=p.created_at,
        updated_at=p.updated_at
    )
