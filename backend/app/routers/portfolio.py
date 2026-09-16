from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.models import (
    User, PortfolioItem, StudentProfile, SkillProfile, Skill, Institution
)
from app.schemas import (
    PortfolioItemResponse, PortfolioPublicView, SkillItemScore
)
from app.dependencies import get_current_user, require_student

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/me", response_model=List[PortfolioItemResponse])
def get_my_portfolio(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """Retrieves the current student's portfolio items (skills, internships, certifications)."""
    items = db.query(PortfolioItem).filter(PortfolioItem.user_id == current_user.id).order_by(desc(PortfolioItem.created_at)).all()
    return items

@router.get("/{user_id}/public", response_model=PortfolioPublicView)
def get_public_portfolio(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Publicly accessible portfolio endpoint for sharing (shareable link).
    Combines verified skills and portfolio items.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "student":
        raise HTTPException(status_code=404, detail="Student profile not found")

    sp = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    inst_name = None
    if sp and sp.institution_id:
        inst = db.query(Institution).filter(Institution.id == sp.institution_id).first()
        inst_name = inst.name if inst else None

    # Fetch verified skills
    skill_profiles = db.query(SkillProfile).filter(SkillProfile.user_id == user_id, SkillProfile.is_verified == True).all()
    verified_skills = []
    for p in skill_profiles:
        sk = db.query(Skill).filter(Skill.id == p.skill_id).first()
        if sk:
            verified_skills.append(SkillItemScore(
                skill_id=sk.id,
                skill_name=sk.name,
                category=sk.category,
                proficiency_score=p.proficiency_score,
                industry_benchmark=sk.industry_benchmark,
                gap_score=0.0,
                is_gap=False,
                is_verified=True
            ))

    # Fetch portfolio items
    p_items = db.query(PortfolioItem).filter(PortfolioItem.user_id == user_id).order_by(desc(PortfolioItem.created_at)).all()

    return PortfolioPublicView(
        user_id=user.id,
        full_name=user.full_name,
        degree=sp.degree if sp else None,
        branch=sp.branch if sp else None,
        institution_name=inst_name,
        verified_skills=verified_skills,
        portfolio_items=p_items
    )
