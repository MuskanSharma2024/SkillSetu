from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Union
import json

from app.database import get_db
from app.models import User, StudentProfile, Company, AcademicianProfile, Institution
from app.schemas import (
    UserCreate, UserResponse, Token, RefreshTokenRequest, UserLogin
)
from app.auth import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user under one of the 4 supported roles:
    'student', 'industry', 'academician', 'institution_admin'.
    Creates corresponding profile record in the same atomic transaction.
    """
    valid_roles = ["student", "industry", "academician", "institution_admin"]
    if user_in.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{user_in.role}'. Allowed roles: {', '.join(valid_roles)}"
        )

    # Check for existing email
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists."
        )

    # Create User
    new_user = User(
        email=user_in.email.lower(),
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    db.flush() # Populate new_user.id

    # Create Role-Specific Profile
    if user_in.role == "student":
        student_prof = StudentProfile(
            user_id=new_user.id,
            institution_id=user_in.institution_id,
            enrollment_no=user_in.enrollment_no,
            degree=user_in.degree or "B.Tech",
            branch=user_in.branch or "Computer Science",
            grad_year=user_in.grad_year or 2026,
            career_interests=json.dumps(user_in.career_interests or ["Software Engineering", "AI/ML"])
        )
        db.add(student_prof)

    elif user_in.role == "industry":
        company_prof = Company(
            user_id=new_user.id,
            name=user_in.company_name or f"{user_in.full_name}'s Enterprise",
            industry_sector=user_in.industry_sector or "Information Technology",
            website=user_in.website,
            location=user_in.location or "India"
        )
        db.add(company_prof)

    elif user_in.role == "academician":
        # Find default institution if not provided
        inst_id = user_in.institution_id
        if not inst_id:
            default_inst = db.query(Institution).first()
            inst_id = default_inst.id if default_inst else None

        acad_prof = AcademicianProfile(
            user_id=new_user.id,
            institution_id=inst_id,
            department=user_in.department or "Computer Science & Engineering",
            designation=user_in.designation or "Assistant Professor",
            faculty_id=user_in.faculty_id
        )
        db.add(acad_prof)

    elif user_in.role == "institution_admin":
        if user_in.institution_name and user_in.institution_code:
            existing_inst = db.query(Institution).filter(
                (Institution.code == user_in.institution_code) | 
                (Institution.name == user_in.institution_name)
            ).first()
            if not existing_inst:
                new_inst = Institution(
                    name=user_in.institution_name,
                    code=user_in.institution_code,
                    contact_email=user_in.email.lower()
                )
                db.add(new_inst)

    db.commit()
    db.refresh(new_user)

    # Issue JWT tokens
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})
    refresh_token = create_refresh_token(data={"sub": str(new_user.id), "role": new_user.role})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=new_user.role,
        user_id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email
    )

@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials and issues Access + Refresh tokens.
    """
    email = login_data.email.lower()
    password = login_data.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently deactivated."
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 password flow form handler for Swagger UI docs."""
    email = form_data.username.lower()
    password = form_data.password

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email
    )

@router.post("/refresh", response_model=dict)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Validates the refresh token and issues a new access token.
    """
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provided token is not a valid refresh token."
            )
        user_id = int(decoded.get("sub"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired refresh token: {str(e)}"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )

    new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "role": user.role
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    return current_user
