from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Institution, AcademicianProfile
from app.schemas import (
    InstitutionResponse, InstitutionCreate,
    AcademicianProfileResponse, AcademicianProfileUpdate
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

@router.get("/{institution_id}", response_model=InstitutionResponse)
def get_institution_by_id(institution_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific institution."""
    inst = db.query(Institution).filter(Institution.id == institution_id).first()
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institution not found."
        )
    return inst
