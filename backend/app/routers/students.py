from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import (
    User, StudentProfile, Institution, SkillAssessment, SkillProfile, 
    Application, StudentConsent, PortfolioItem, SkillProfileSnapshot
)
from app.schemas import StudentProfileResponse, StudentProfileUpdate
from app.dependencies import require_student, require_all_authenticated

router = APIRouter(prefix="/students", tags=["Students"])

def build_student_response(profile: StudentProfile, user: User, db: Session) -> StudentProfileResponse:
    inst_name = None
    if profile.institution_id:
        inst = db.query(Institution).filter(Institution.id == profile.institution_id).first()
        if inst:
            inst_name = inst.name

    interests = []
    if profile.career_interests:
        try:
            interests = json.loads(profile.career_interests)
            if not isinstance(interests, list):
                interests = [str(profile.career_interests)]
        except Exception:
            interests = [i.strip() for i in profile.career_interests.split(",") if i.strip()]

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=user.full_name,
        email=user.email,
        institution_id=profile.institution_id,
        institution_name=inst_name,
        enrollment_no=profile.enrollment_no,
        degree=profile.degree,
        branch=profile.branch,
        grad_year=profile.grad_year,
        career_interests=interests,
        resume_url=profile.resume_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )

@router.get("/profile", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Retrieve the profile of the currently logged-in student."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return build_student_response(profile, current_user, db)

@router.put("/profile", response_model=StudentProfileResponse)
def update_my_profile(
    update_data: StudentProfileUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Update profile attributes for the logged-in student."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    if update_data.institution_id is not None:
        inst = db.query(Institution).filter(Institution.id == update_data.institution_id).first()
        if not inst:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found."
            )
        profile.institution_id = update_data.institution_id

    if update_data.enrollment_no is not None:
        profile.enrollment_no = update_data.enrollment_no
    if update_data.degree is not None:
        profile.degree = update_data.degree
    if update_data.branch is not None:
        profile.branch = update_data.branch
    if update_data.grad_year is not None:
        profile.grad_year = update_data.grad_year
    if update_data.career_interests is not None:
        profile.career_interests = json.dumps(update_data.career_interests)
    if update_data.resume_url is not None:
        profile.resume_url = update_data.resume_url

    db.commit()
    db.refresh(profile)

    return build_student_response(profile, current_user, db)

@router.get("/profile/{user_id}", response_model=StudentProfileResponse)
def get_student_profile_by_id(
    user_id: int,
    current_user: User = Depends(require_all_authenticated),
    db: Session = Depends(get_db)
):
    """
    Retrieve any student's public profile.
    Accessible to authenticated recruiters, academicians, and admins.
    """
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found."
        )

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile data not initialized."
        )

    return build_student_response(profile, user, db)

# --- Task B4: Data Access & Deletion Request ---
@router.get("/me/data-export")
def export_my_data(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Task B4: Student-facing action to request a full copy of their assessment & profile data.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    assessments = db.query(SkillAssessment).filter(SkillAssessment.user_id == current_user.id).all()
    skills = db.query(SkillProfile).filter(SkillProfile.user_id == current_user.id).all()
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    consent = db.query(StudentConsent).filter(StudentConsent.user_id == current_user.id).first()

    return {
        "user_info": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat()
        },
        "academic_profile": {
            "degree": profile.degree if profile else None,
            "branch": profile.branch if profile else None,
            "grad_year": profile.grad_year if profile else None,
            "resume_url": profile.resume_url if profile else None
        } if profile else None,
        "consent_record": {
            "consent_given": consent.consent_given if consent else False,
            "consented_at": consent.consented_at.isoformat() if consent and consent.consented_at else None
        } if consent else None,
        "skill_profiles": [{"skill_id": s.skill_id, "score": s.proficiency_score, "is_verified": s.is_verified} for s in skills],
        "assessments_count": len(assessments),
        "applications_count": len(applications)
    }

@router.post("/me/data-deletion-request")
def request_data_deletion(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Task B4: Student-facing action to request deletion of assessment data,
    subject to institutional retention rules while retaining anonymized aggregate stats.
    """
    # Anonymize/soft-delete individual assessment records
    assessments = db.query(SkillAssessment).filter(SkillAssessment.user_id == current_user.id).all()
    for a in assessments:
        a.responses = "[ANONYMIZED_DATA_DELETION]"

    # Clear personal profiles
    skills = db.query(SkillProfile).filter(SkillProfile.user_id == current_user.id).all()
    for s in skills:
        db.delete(s)

    db.commit()
    return {"status": "success", "message": "Personal assessment data deleted and anonymized for curriculum statistics."}

