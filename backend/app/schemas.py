from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    full_name: str
    email: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Minimum 6 characters")
    
    # Optional role-specific initialization data
    # Student
    institution_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    career_interests: Optional[List[str]] = None

    # Industry
    company_name: Optional[str] = None
    industry_sector: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None

    # Academician
    department: Optional[str] = None
    designation: Optional[str] = None
    faculty_id: Optional[str] = None

    # Institution Admin
    institution_name: Optional[str] = None
    institution_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Student Profile Schemas ---
class StudentProfileBase(BaseModel):
    institution_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    career_interests: Optional[List[str]] = None
    resume_url: Optional[str] = None

class StudentProfileUpdate(BaseModel):
    institution_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    career_interests: Optional[List[str]] = None
    resume_url: Optional[str] = None

class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    institution_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Company Profile Schemas ---
class CompanyBase(BaseModel):
    name: str
    industry_sector: str
    website: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry_sector: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Institution Schemas ---
class InstitutionBase(BaseModel):
    name: str
    code: str
    website: Optional[str] = None
    address: Optional[str] = None
    contact_email: EmailStr

class InstitutionCreate(InstitutionBase):
    pass

class InstitutionResponse(InstitutionBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Academician Profile Schemas ---
class AcademicianProfileBase(BaseModel):
    institution_id: Optional[int] = None
    department: str
    designation: str
    faculty_id: Optional[str] = None

class AcademicianProfileUpdate(BaseModel):
    institution_id: Optional[int] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    faculty_id: Optional[str] = None

class AcademicianProfileResponse(AcademicianProfileBase):
    id: int
    user_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    institution_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Document Schemas ---
class DocumentResponse(BaseModel):
    id: int
    user_id: int
    document_type: str
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    download_url: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# --- Dashboard Shell Schemas ---
class DashboardShellResponse(BaseModel):
    role: str
    user_id: int
    full_name: str
    email: str
    title: str
    summary: dict
    available_modules: List[str]
