from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Company
from app.schemas import CompanyResponse, CompanyUpdate
from app.dependencies import require_industry

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/profile", response_model=CompanyResponse)
def get_my_company_profile(
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Retrieve company profile of the authenticated industry partner."""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        company = Company(
            user_id=current_user.id,
            name=f"{current_user.full_name}'s Organization",
            industry_sector="Information Technology"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
    return company

@router.put("/profile", response_model=CompanyResponse)
def update_my_company_profile(
    update_data: CompanyUpdate,
    current_user: User = Depends(require_industry),
    db: Session = Depends(get_db)
):
    """Update company details for the logged-in industry user."""
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        company = Company(
            user_id=current_user.id,
            name=update_data.name or f"{current_user.full_name}'s Organization",
            industry_sector=update_data.industry_sector or "Information Technology"
        )
        db.add(company)

    if update_data.name is not None:
        company.name = update_data.name
    if update_data.industry_sector is not None:
        company.industry_sector = update_data.industry_sector
    if update_data.website is not None:
        company.website = update_data.website
    if update_data.description is not None:
        company.description = update_data.description
    if update_data.location is not None:
        company.location = update_data.location

    db.commit()
    db.refresh(company)
    return company

@router.get("", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    """List all registered industry partner companies."""
    return db.query(Company).all()

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company_by_id(company_id: int, db: Session = Depends(get_db)):
    """Get details of a specific company by id."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found."
        )
    return company
