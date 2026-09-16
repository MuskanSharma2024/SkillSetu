from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import User, StudentProfile, Institution
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
