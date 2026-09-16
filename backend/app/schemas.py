from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
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
    institution_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    grad_year: Optional[int] = None
    career_interests: Optional[List[str]] = None

    company_name: Optional[str] = None
    industry_sector: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None

    department: Optional[str] = None
    designation: Optional[str] = None
    faculty_id: Optional[str] = None

    institution_name: Optional[str] = None
    institution_code: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

# --- Skill Schemas ---
class SkillBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    industry_benchmark: float = 75.0

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# --- Skill Assessment & Questionnaires ---
class AssessmentQuestion(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    question_text: str
    category: str
    difficulty: str
    options: List[Dict[str, str]]

class AssessmentAnswerSubmission(BaseModel):
    question_id: int
    skill_id: int
    selected_option: str

class AssessmentSubmission(BaseModel):
    assessment_type: str = "diagnostic"
    answers: List[AssessmentAnswerSubmission]

class AssessmentResult(BaseModel):
    assessment_id: int
    user_id: int
    scores_per_skill: Dict[str, float]
    gaps_detected: List[Dict[str, Any]]
    completed_at: datetime.datetime

# --- Student Skill Profile & Gap View ---
class SkillItemScore(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    proficiency_score: float
    industry_benchmark: float
    gap_score: float
    is_gap: bool
    is_verified: bool

class StudentSkillProfileView(BaseModel):
    user_id: int
    full_name: str
    total_skills_assessed: int
    top_strengths: List[SkillItemScore]
    critical_gaps: List[SkillItemScore]
    all_skills: List[SkillItemScore]
    overall_readiness_score: float

# --- Recommendation Schemas ---
class OpportunityRecommendation(BaseModel):
    opportunity_id: int
    title: str
    company_name: str
    opportunity_type: str
    location: Optional[str]
    stipend_salary: Optional[str]
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]

# --- Industry Demand Aggregation ---
class SkillDemandItem(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    frequency_count: int
    companies_requesting: int
    trend: str
    benchmark_score: float

class IndustryDemandDataset(BaseModel):
    total_postings: int
    total_companies: int
    top_demanded_skills: List[SkillDemandItem]
    updated_at: datetime.datetime

# --- Curriculum Feedback Loop ---
class CurriculumGapReportItem(BaseModel):
    id: int
    institution_id: int
    institution_name: str
    skill_id: int
    skill_name: str
    category: str
    student_cohort_avg: float
    industry_benchmark: float
    gap_score: float
    demand_frequency: int
    trend: str
    recommendation_text: Optional[str]
    status: str
    actions_count: int
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class CurriculumActionCreate(BaseModel):
    action_type: str = Field(..., description="e.g. update_syllabus, workshop_planned, guest_lecture, lab_module")
    course_name: str
    action_notes: str

class CurriculumActionResponse(BaseModel):
    id: int
    report_id: int
    user_id: int
    faculty_name: Optional[str]
    action_type: str
    course_name: str
    action_notes: str
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# --- Opportunities (03-tasks-opportunities) ---
class RequiredSkillItem(BaseModel):
    skill_id: int
    min_proficiency: float = 70.0
    importance_weight: float = 1.0

class RequiredSkillDetail(BaseModel):
    skill_id: int
    skill_name: str
    category: str
    min_proficiency: float
    importance_weight: float

class OpportunityCreate(BaseModel):
    title: str
    opportunity_type: str # internship, job, apprenticeship, project, fdp, consultancy, sabbatical, research_collab
    target_role: str = "student" # student or faculty
    description: Optional[str] = None
    location: Optional[str] = "Hybrid"
    stipend_salary: Optional[str] = None
    deadline: Optional[datetime.datetime] = None
    required_skills: List[RequiredSkillItem] = []

class OpportunityResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    title: str
    opportunity_type: str
    target_role: str
    description: Optional[str]
    location: Optional[str]
    stipend_salary: Optional[str]
    deadline: Optional[datetime.datetime]
    is_active: bool
    skills: List[RequiredSkillDetail] = []
    applicant_match_score: Optional[float] = None
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# --- Applications ---
class ApplicationCreate(BaseModel):
    cover_note: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: int
    opportunity_id: int
    opportunity_title: str
    company_name: str
    user_id: int
    applicant_name: str
    applicant_email: str
    applicant_role: str
    match_score: float
    status: str
    cover_note: Optional[str]
    resume_link: Optional[str]
    mentor_rating: Optional[float]
    mentor_feedback: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class ApplicationStatusUpdate(BaseModel):
    status: str # applied, shortlisted, interview, offered, rejected, completed

class MentorFeedbackSubmit(BaseModel):
    mentor_rating: float = Field(..., ge=1.0, le=5.0)
    mentor_feedback: str

# --- Learning Programs ---
class ProgramSkillItem(BaseModel):
    skill_id: int
    granted_proficiency: float = 85.0

class LearningProgramCreate(BaseModel):
    title: str
    program_type: str = "certification" # training, certification, workshop, mentorship
    description: Optional[str] = None
    duration_weeks: int = 4
    skills_covered: List[ProgramSkillItem] = []

class LearningProgramResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    title: str
    program_type: str
    description: Optional[str]
    duration_weeks: int
    is_active: bool
    skills: List[Dict[str, Any]] = []
    is_enrolled: Optional[bool] = False
    enrollment_status: Optional[str] = None
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

class ProgramEnrollmentResponse(BaseModel):
    id: int
    program_id: int
    program_title: str
    user_id: int
    status: str
    enrolled_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    model_config = ConfigDict(from_attributes=True)

# --- Notifications & Documents ---
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    category: str
    is_read: bool
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

class DashboardShellResponse(BaseModel):
    role: str
    user_id: int
    full_name: str
    email: str
    title: str
    summary: Dict[str, Any]
    available_modules: List[str]
