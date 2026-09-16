from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import json
import datetime

from app.database import get_db
from app.models import (
    User, Skill, SkillAssessment, SkillProfile, Opportunity, OpportunitySkill,
    CurriculumGapReport, CurriculumAction, Notification, StudentProfile, Institution, Company,
    AcademicianProfile
)
from app.schemas import (
    SkillResponse, SkillCreate, AssessmentQuestion, AssessmentSubmission,
    AssessmentResult, StudentSkillProfileView, SkillItemScore, OpportunityRecommendation,
    IndustryDemandDataset, SkillDemandItem, CurriculumGapReportItem, CurriculumActionCreate,
    CurriculumActionResponse, NotificationResponse
)
from app.dependencies import (
    get_current_user, require_student, require_academician, require_staff, require_all_authenticated
)

router = APIRouter(prefix="/skills", tags=["Skill Engine & Curriculum Feedback Loop"])

# In-memory question bank for Task 2 (Seedable questionnaire)
ASSESSMENT_QUESTIONS = [
    {
        "id": 1,
        "skill_name": "Python",
        "question_text": "What is the time complexity of looking up a key in a standard Python dictionary on average?",
        "category": "technical",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "O(1)"},
            {"id": "B", "text": "O(n)"},
            {"id": "C", "text": "O(log n)"},
            {"id": "D", "text": "O(n^2)"}
        ],
        "correct_option": "A",
        "points": 25.0
    },
    {
        "id": 2,
        "skill_name": "Python",
        "question_text": "Which built-in Python module provides tools for working with asynchronous event loops?",
        "category": "technical",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "threading"},
            {"id": "B", "text": "asyncio"},
            {"id": "C", "text": "multiprocessing"},
            {"id": "D", "text": "concurrent"}
        ],
        "correct_option": "B",
        "points": 25.0
    },
    {
        "id": 3,
        "skill_name": "SQL & Relational Databases",
        "question_text": "Which SQL clause is used to filter groups of rows after an aggregate function has been applied?",
        "category": "technical",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "WHERE"},
            {"id": "B", "text": "GROUP BY"},
            {"id": "C", "text": "HAVING"},
            {"id": "D", "text": "ORDER BY"}
        ],
        "correct_option": "C",
        "points": 25.0
    },
    {
        "id": 4,
        "skill_name": "Data Structures & Algorithms",
        "question_text": "Which data structure follows the LIFO (Last In First Out) principle?",
        "category": "technical",
        "difficulty": "beginner",
        "options": [
            {"id": "A", "text": "Queue"},
            {"id": "B", "text": "Stack"},
            {"id": "C", "text": "Heap"},
            {"id": "D", "text": "Binary Search Tree"}
        ],
        "correct_option": "B",
        "points": 25.0
    },
    {
        "id": 5,
        "skill_name": "Cloud Computing (AWS/GCP)",
        "question_text": "Which type of cloud computing service provides virtual machines and raw compute resources without managing physical hardware?",
        "category": "technical",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "SaaS (Software as a Service)"},
            {"id": "B", "text": "IaaS (Infrastructure as a Service)"},
            {"id": "C", "text": "PaaS (Platform as a Service)"},
            {"id": "D", "text": "FaaS (Function as a Service)"}
        ],
        "correct_option": "B",
        "points": 25.0
    },
    {
        "id": 6,
        "skill_name": "Machine Learning & AI",
        "question_text": "Which optimization technique is commonly used to minimize loss functions in neural networks?",
        "category": "technical",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "Gradient Descent"},
            {"id": "B", "text": "Breadth First Search"},
            {"id": "C", "text": "K-Means Clustering"},
            {"id": "D", "text": "Dijkstra's Algorithm"}
        ],
        "correct_option": "A",
        "points": 25.0
    },
    {
        "id": 7,
        "skill_name": "Problem Solving & Critical Thinking",
        "question_text": "When approaching an ambiguous system failure, what is the recommended first troubleshooting principle?",
        "category": "soft",
        "difficulty": "intermediate",
        "options": [
            {"id": "A", "text": "Immediately rewrite the core service"},
            {"id": "B", "text": "Reproduce the issue and isolate symptoms with telemetry/logs"},
            {"id": "C", "text": "Restart the production database without investigation"},
            {"id": "D", "text": "Notify users that service is discontinued"}
        ],
        "correct_option": "B",
        "points": 25.0
    },
    {
        "id": 8,
        "skill_name": "Team Collaboration & Agile",
        "question_text": "In Scrum methodology, what is the main purpose of the daily stand-up meeting?",
        "category": "soft",
        "difficulty": "beginner",
        "options": [
            {"id": "A", "text": "To negotiate employee compensations"},
            {"id": "B", "text": "Synchronize progress, align on daily sprint goals, and surface blockers"},
            {"id": "C", "text": "Deliver long technical lectures"},
            {"id": "D", "text": "Sign customer procurement contracts"}
        ],
        "correct_option": "B",
        "points": 25.0
    }
]

# Task 1: Skill Master List
@router.get("", response_model=List[SkillResponse])
def list_skills(category: str = None, db: Session = Depends(get_db)):
    """Retrieve master list of technical and soft skills."""
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    return query.order_by(Skill.category, Skill.name).all()

# Task 2: Skill Assessment Questionnaire
@router.get("/questionnaire", response_model=List[AssessmentQuestion])
def get_assessment_questions(db: Session = Depends(get_db)):
    """Provides the questionnaire items for student skill assessment."""
    skills_map = {s.name: s.id for s in db.query(Skill).all()}
    questions = []
    for q in ASSESSMENT_QUESTIONS:
        skill_id = skills_map.get(q["skill_name"], 1)
        questions.append(AssessmentQuestion(
            id=q["id"],
            skill_id=skill_id,
            skill_name=q["skill_name"],
            question_text=q["question_text"],
            category=q["category"],
            difficulty=q["difficulty"],
            options=q["options"]
        ))
    return questions

# Task 3 & 4: Skill Scoring Logic & Gap Detection
@router.post("/assessments", response_model=AssessmentResult)
def submit_skill_assessment(
    submission: AssessmentSubmission,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Submits completed assessment responses, converts answers into proficiency scores (0-100),
    detects skill gaps against industry benchmarks, and persists to skill_profiles.
    """
    q_lookup = {q["id"]: q for q in ASSESSMENT_QUESTIONS}
    skill_scores: Dict[str, float] = {}
    skill_counts: Dict[str, int] = {}

    for ans in submission.answers:
        q = q_lookup.get(ans.question_id)
        if not q:
            continue
        skill_name = q["skill_name"]
        is_correct = (ans.selected_option.upper() == q["correct_option"].upper())
        score_add = 85.0 if is_correct else 35.0  # Base realistic proficiency calculation

        if skill_name not in skill_scores:
            skill_scores[skill_name] = score_add
            skill_counts[skill_name] = 1
        else:
            skill_scores[skill_name] += score_add
            skill_counts[skill_name] += 1

    # Average score per skill
    computed_scores: Dict[str, float] = {}
    for skill_name, total_score in skill_scores.items():
        computed_scores[skill_name] = round(total_score / skill_counts[skill_name], 1)

    # Detect gaps and update skill_profiles in DB
    gaps_detected = []
    for skill_name, prof_score in computed_scores.items():
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if not skill:
            skill = Skill(name=skill_name, category="technical", industry_benchmark=75.0)
            db.add(skill)
            db.flush()

        gap = round(skill.industry_benchmark - prof_score, 1)
        is_gap = prof_score < skill.industry_benchmark

        if is_gap:
            gaps_detected.append({
                "skill_name": skill_name,
                "score": prof_score,
                "benchmark": skill.industry_benchmark,
                "gap": gap
            })

        # Update or create SkillProfile
        existing_profile = db.query(SkillProfile).filter(
            SkillProfile.user_id == current_user.id,
            SkillProfile.skill_id == skill.id
        ).first()

        if existing_profile:
            existing_profile.proficiency_score = prof_score
            existing_profile.last_assessed_at = datetime.datetime.utcnow()
            existing_profile.is_verified = (prof_score >= skill.industry_benchmark)
        else:
            new_prof = SkillProfile(
                user_id=current_user.id,
                skill_id=skill.id,
                proficiency_score=prof_score,
                is_verified=(prof_score >= skill.industry_benchmark),
                last_assessed_at=datetime.datetime.utcnow()
            )
            db.add(new_prof)

    # Store raw assessment in skill_assessments
    assessment_record = SkillAssessment(
        user_id=current_user.id,
        assessment_type=submission.assessment_type,
        responses=json.dumps([a.model_dump() for a in submission.answers]),
        score_summary=json.dumps(computed_scores),
        completed_at=datetime.datetime.utcnow()
    )
    db.add(assessment_record)

    # Refresh curriculum gap reports for this student's institution
    student_profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if student_profile and student_profile.institution_id:
        refresh_curriculum_gap_reports_internal(student_profile.institution_id, db)

    db.commit()
    db.refresh(assessment_record)

    return AssessmentResult(
        assessment_id=assessment_record.id,
        user_id=current_user.id,
        scores_per_skill=computed_scores,
        gaps_detected=gaps_detected,
        completed_at=assessment_record.completed_at
    )

# Task 5: Skill Profile View
@router.get("/profile/me", response_model=StudentSkillProfileView)
def get_my_skill_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Student-facing view of their generated skill profile:
    Strengths, identified gaps against industry benchmarks, and overall career readiness.
    """
    profiles = db.query(SkillProfile).filter(SkillProfile.user_id == current_user.id).all()
    all_skills = []
    strengths = []
    gaps = []
    total_score = 0.0

    for sp in profiles:
        skill = db.query(Skill).filter(Skill.id == sp.skill_id).first()
        if not skill:
            continue
        gap_score = round(skill.industry_benchmark - sp.proficiency_score, 1)
        is_gap = sp.proficiency_score < skill.industry_benchmark

        item = SkillItemScore(
            skill_id=skill.id,
            skill_name=skill.name,
            category=skill.category,
            proficiency_score=sp.proficiency_score,
            industry_benchmark=skill.industry_benchmark,
            gap_score=gap_score,
            is_gap=is_gap,
            is_verified=sp.is_verified
        )
        all_skills.append(item)
        total_score += sp.proficiency_score

        if not is_gap:
            strengths.append(item)
        else:
            gaps.append(item)

    # Sort strengths and gaps
    strengths.sort(key=lambda x: x.proficiency_score, reverse=True)
    gaps.sort(key=lambda x: x.gap_score, reverse=True)

    readiness = round(total_score / len(all_skills), 1) if all_skills else 0.0

    return StudentSkillProfileView(
        user_id=current_user.id,
        full_name=current_user.full_name,
        total_skills_assessed=len(all_skills),
        top_strengths=strengths,
        critical_gaps=gaps,
        all_skills=all_skills,
        overall_readiness_score=readiness
    )

# Task 6 & 7: Recommendation Engine (v1) & Refresh Trigger
@router.get("/recommendations/me", response_model=List[OpportunityRecommendation])
def get_opportunity_recommendations(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Rule-based weighted recommendation engine:
    Matches student skill vector against active opportunities and computes match scores.
    """
    user_skills = {
        sp.skill_id: sp.proficiency_score
        for sp in db.query(SkillProfile).filter(SkillProfile.user_id == current_user.id).all()
    }

    opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    recommendations = []

    for opp in opportunities:
        company = db.query(Company).filter(Company.id == opp.company_id).first()
        company_name = company.name if company else "Tech Enterprise"

        req_skills = db.query(OpportunitySkill).filter(OpportunitySkill.opportunity_id == opp.id).all()
        if not req_skills:
            # Default fallback match if no specific skills tagged
            match_pct = 70.0
            matched = ["General Problem Solving"]
            missing = []
        else:
            total_weight = sum(rs.importance_weight for rs in req_skills)
            weighted_score = 0.0
            matched = []
            missing = []

            for rs in req_skills:
                skill = db.query(Skill).filter(Skill.id == rs.skill_id).first()
                sname = skill.name if skill else f"Skill #{rs.skill_id}"
                user_score = user_skills.get(rs.skill_id, 0.0)

                if user_score >= rs.min_proficiency:
                    weighted_score += rs.importance_weight * 1.0
                    matched.append(sname)
                elif user_score > 0:
                    ratio = user_score / rs.min_proficiency
                    weighted_score += rs.importance_weight * ratio
                    missing.append(f"{sname} (Current: {user_score}%, Need: {rs.min_proficiency}%)")
                else:
                    missing.append(f"{sname} (Not Assessed)")

            match_pct = round((weighted_score / total_weight) * 100, 1) if total_weight > 0 else 50.0

        recommendations.append(OpportunityRecommendation(
            opportunity_id=opp.id,
            title=opp.title,
            company_name=company_name,
            opportunity_type=opp.opportunity_type,
            location=opp.location,
            stipend_salary=opp.stipend_salary,
            match_percentage=match_pct,
            matched_skills=matched,
            missing_skills=missing
        ))

    recommendations.sort(key=lambda x: x.match_percentage, reverse=True)
    return recommendations

# Task 8: ⭐ Industry Skill-Demand Aggregation
@router.get("/industry-demand", response_model=IndustryDemandDataset)
def get_industry_skill_demand(db: Session = Depends(get_db)):
    """
    ⭐ USP Component:
    Aggregates required skills across all active postings into a live industry demand dataset.
    """
    total_postings = db.query(Opportunity).filter(Opportunity.is_active == True).count()
    total_companies = db.query(Company).count()

    skills = db.query(Skill).all()
    demand_items = []

    for skill in skills:
        links = db.query(OpportunitySkill).filter(OpportunitySkill.skill_id == skill.id).all()
        freq = len(links)
        comp_count = len(set(
            db.query(Opportunity.company_id).filter(Opportunity.id == l.opportunity_id).scalar()
            for l in links if l.opportunity_id
        ))

        # Determine trending based on frequency
        trend = "rising" if freq >= 2 else "stable"

        demand_items.append(SkillDemandItem(
            skill_id=skill.id,
            skill_name=skill.name,
            category=skill.category,
            frequency_count=freq,
            companies_requesting=comp_count,
            trend=trend,
            benchmark_score=skill.industry_benchmark
        ))

    demand_items.sort(key=lambda x: x.frequency_count, reverse=True)

    return IndustryDemandDataset(
        total_postings=total_postings,
        total_companies=total_companies,
        top_demanded_skills=demand_items,
        updated_at=datetime.datetime.utcnow()
    )

# Internal helper to refresh reports
def refresh_curriculum_gap_reports_internal(institution_id: int, db: Session):
    # Find all students of this institution
    student_user_ids = [
        s.user_id for s in db.query(StudentProfile).filter(StudentProfile.institution_id == institution_id).all()
    ]

    skills = db.query(Skill).all()
    for skill in skills:
        # Calculate cohort average score (default 40.0 if new cohort)
        scores = []
        if student_user_ids:
            scores = db.query(SkillProfile.proficiency_score).filter(
                SkillProfile.user_id.in_(student_user_ids),
                SkillProfile.skill_id == skill.id
            ).all()
        avg_score = round(sum(s[0] for s in scores) / len(scores), 1) if scores else 40.0

        # Frequency in industry
        freq = db.query(OpportunitySkill).filter(OpportunitySkill.skill_id == skill.id).count()
        gap = round(skill.industry_benchmark - avg_score, 1)

        recommendation = None
        if gap > 15:
            recommendation = f"High priority: Student cohort avg ({avg_score}%) is significantly below industry benchmark ({skill.industry_benchmark}%). Introduce hands-on lab modules and guest lectures."
        elif gap > 0:
            recommendation = f"Moderate gap: Align course assignments to current industry tools for {skill.name}."
        else:
            recommendation = f"Cohort exceeds industry benchmark ({avg_score}% vs {skill.industry_benchmark}%). Ready for advanced projects."

        report = db.query(CurriculumGapReport).filter(
            CurriculumGapReport.institution_id == institution_id,
            CurriculumGapReport.skill_id == skill.id
        ).first()

        if report:
            report.student_cohort_avg = avg_score
            report.industry_benchmark = skill.industry_benchmark
            report.gap_score = gap
            report.demand_frequency = freq
            report.recommendation_text = recommendation
            report.updated_at = datetime.datetime.utcnow()
        else:
            report = CurriculumGapReport(
                institution_id=institution_id,
                skill_id=skill.id,
                student_cohort_avg=avg_score,
                industry_benchmark=skill.industry_benchmark,
                gap_score=gap,
                demand_frequency=freq,
                trend="rising" if freq >= 2 else "stable",
                recommendation_text=recommendation,
                status="open"
            )
            db.add(report)

# Task 9 & 10: ⭐ Curriculum Feedback Reports & Actions
@router.get("/curriculum-gap-report", response_model=List[CurriculumGapReportItem])
def get_curriculum_gap_report(
    institution_id: int = None,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """
    ⭐ USP Primary Evaluator View:
    Produces a cross-referenced 'curriculum gap report' comparing student cohort weaknesses
    against high-demand industry skills.
    """
    # If no institution_id provided, default to user's linked institution
    target_inst_id = institution_id
    if not target_inst_id:
        if current_user.role == "academician":
            acad = db.query(AcademicianProfile).filter(AcademicianProfile.user_id == current_user.id).first()
            if acad and acad.institution_id:
                target_inst_id = acad.institution_id
        if not target_inst_id:
            first_inst = db.query(Institution).first()
            target_inst_id = first_inst.id if first_inst else 1

    refresh_curriculum_gap_reports_internal(target_inst_id, db)
    db.commit()

    reports = db.query(CurriculumGapReport).filter(CurriculumGapReport.institution_id == target_inst_id).all()
    inst = db.query(Institution).filter(Institution.id == target_inst_id).first()
    inst_name = inst.name if inst else "Engineering Institution"

    items = []
    for r in reports:
        skill = db.query(Skill).filter(Skill.id == r.skill_id).first()
        actions_cnt = db.query(CurriculumAction).filter(CurriculumAction.report_id == r.id).count()

        items.append(CurriculumGapReportItem(
            id=r.id,
            institution_id=r.institution_id,
            institution_name=inst_name,
            skill_id=r.skill_id,
            skill_name=skill.name if skill else "Skill",
            category=skill.category if skill else "technical",
            student_cohort_avg=r.student_cohort_avg,
            industry_benchmark=r.industry_benchmark,
            gap_score=r.gap_score,
            demand_frequency=r.demand_frequency,
            trend=r.trend,
            recommendation_text=r.recommendation_text,
            status=r.status,
            actions_count=actions_cnt,
            updated_at=r.updated_at
        ))

    # Sort by gap_score * demand_frequency (highest impact gaps first)
    items.sort(key=lambda x: (x.gap_score * max(1, x.demand_frequency)), reverse=True)
    return items

@router.post("/curriculum-reports/{report_id}/actions", response_model=CurriculumActionResponse, status_code=status.HTTP_201_CREATED)
def add_curriculum_action(
    report_id: int,
    action_in: CurriculumActionCreate,
    current_user: User = Depends(require_academician),
    db: Session = Depends(get_db)
):
    """
    ⭐ Closes the loop back into teaching:
    Allows academicians to log concrete course/syllabus actions to close detected skill gaps.
    """
    report = db.query(CurriculumGapReport).filter(CurriculumGapReport.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curriculum gap report not found."
        )

    action = CurriculumAction(
        report_id=report_id,
        user_id=current_user.id,
        action_type=action_in.action_type,
        course_name=action_in.course_name,
        action_notes=action_in.action_notes,
        created_at=datetime.datetime.utcnow()
    )
    db.add(action)
    report.status = "course_updated"
    db.commit()
    db.refresh(action)

    return CurriculumActionResponse(
        id=action.id,
        report_id=action.report_id,
        user_id=action.user_id,
        faculty_name=current_user.full_name,
        action_type=action.action_type,
        course_name=action.course_name,
        action_notes=action.action_notes,
        created_at=action.created_at
    )

@router.get("/curriculum-reports/{report_id}/actions", response_model=List[CurriculumActionResponse])
def get_curriculum_actions(
    report_id: int,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """List all corrective curriculum actions taken on a specific gap report."""
    actions = db.query(CurriculumAction).filter(CurriculumAction.report_id == report_id).all()
    results = []
    for a in actions:
        u = db.query(User).filter(User.id == a.user_id).first()
        results.append(CurriculumActionResponse(
            id=a.id,
            report_id=a.report_id,
            user_id=a.user_id,
            faculty_name=u.full_name if u else "Faculty Member",
            action_type=a.action_type,
            course_name=a.course_name,
            action_notes=a.action_notes,
            created_at=a.created_at
        ))
    return results

# Task 11: Feedback Loop Notifications
@router.get("/notifications", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve notifications regarding skill gaps and demand changes."""
    notifs = db.query(Notification).filter(
        (Notification.user_id == current_user.id) |
        (Notification.target_role == current_user.role)
    ).order_by(Notification.created_at.desc()).all()
    return notifs

@router.post("/notifications/{notification_id}/mark-read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notif.is_read = True
    db.commit()
    return {"status": "success", "message": "Notification marked as read."}
