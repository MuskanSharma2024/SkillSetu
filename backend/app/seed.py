import json
import datetime
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import (
    User, Institution, StudentProfile, Company, AcademicianProfile,
    Skill, Opportunity, OpportunitySkill, SkillProfile, CurriculumGapReport,
    CurriculumAction, Notification
)
from app.auth import get_password_hash

def seed_database():
    """Seeds the database with essential foundation and skill-engine demo data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # 1. Seed Institutions
        if db.query(Institution).count() == 0:
            dtu = Institution(
                name="Delhi Technological University",
                code="DTU-DEL-101",
                website="https://www.dtu.ac.in",
                address="Shahbad Daulatpur, Main Bawana Road, Delhi",
                contact_email="admin@dtu.ac.in"
            )
            anna = Institution(
                name="Anna University",
                code="AU-CHN-202",
                website="https://www.annauniv.edu",
                address="Sardar Patel Road, Guindy, Chennai",
                contact_email="admin@annauniv.edu"
            )
            nit = Institution(
                name="National Institute of Technology",
                code="NIT-TRICHY-303",
                website="https://www.nitt.edu",
                address="Tiruchirappalli, Tamil Nadu",
                contact_email="admin@nit.ac.in"
            )
            db.add_all([dtu, anna, nit])
            db.flush()
            print("Seeded institutions.")
        else:
            dtu = db.query(Institution).filter(Institution.code == "DTU-DEL-101").first()
            nit = db.query(Institution).filter(Institution.code == "NIT-TRICHY-303").first()

        # 2. Seed Skills (Master List with benchmarks)
        if db.query(Skill).count() == 0:
            skills_data = [
                # Technical
                {"name": "Python", "category": "technical", "description": "High-level programming language for backend, data science, and scripting.", "benchmark": 80.0},
                {"name": "SQL & Relational Databases", "category": "technical", "description": "Querying, schema design, and ACID transactions.", "benchmark": 75.0},
                {"name": "Data Structures & Algorithms", "category": "technical", "description": "Core computer science fundamentals: trees, graphs, sorting, searching.", "benchmark": 85.0},
                {"name": "Cloud Computing (AWS/GCP)", "category": "technical", "description": "Deploying, scaling, and managing cloud infrastructure.", "benchmark": 70.0},
                {"name": "Machine Learning & AI", "category": "technical", "description": "Supervised learning, neural networks, LLM integrations.", "benchmark": 75.0},
                {"name": "REST API Design & FastAPI", "category": "technical", "description": "Designing scalable RESTful web services with OpenAPI specs.", "benchmark": 80.0},
                {"name": "Web Frontend (HTML/CSS/JS)", "category": "technical", "description": "Responsive layout, modern CSS design systems, asynchronous JavaScript.", "benchmark": 75.0},
                {"name": "Git & CI/CD Pipelines", "category": "tools", "description": "Version control branching models and automated deployment workflows.", "benchmark": 70.0},
                {"name": "Docker & Containers", "category": "tools", "description": "Containerizing microservices and environment parity.", "benchmark": 65.0},
                # Soft
                {"name": "Problem Solving & Critical Thinking", "category": "soft", "description": "Structured root-cause diagnosis and algorithmic troubleshooting.", "benchmark": 80.0},
                {"name": "Team Collaboration & Agile", "category": "soft", "description": "Scrum methodology, cross-functional pair programming, and peer reviews.", "benchmark": 75.0},
                {"name": "Technical Communication", "category": "soft", "description": "Documenting architecture, presenting designs, and clear code comments.", "benchmark": 70.0},
            ]
            for s in skills_data:
                db.add(Skill(
                    name=s["name"],
                    category=s["category"],
                    description=s["description"],
                    industry_benchmark=s["benchmark"]
                ))
            db.flush()
            print("Seeded skills master list.")

        # 3. Seed Demo Users (Password: Password123!)
        demo_pwd = get_password_hash("Password123!")

        # Student Demo
        student_user = db.query(User).filter(User.email == "student@skillsetu.edu").first()
        if not student_user:
            student_user = User(
                email="student@skillsetu.edu",
                password_hash=demo_pwd,
                full_name="Aarav Sharma",
                role="student",
                is_active=True
            )
            db.add(student_user)
            db.flush()

            student_prof = StudentProfile(
                user_id=student_user.id,
                institution_id=dtu.id if dtu else 1,
                enrollment_no="DTU/2022/CS/104",
                degree="B.Tech",
                branch="Computer Science & Engineering",
                grad_year=2026,
                career_interests=json.dumps(["Full Stack Engineering", "AI & Data Systems", "Cloud Architecture"]),
                resume_url=None
            )
            db.add(student_prof)

            # Pre-populate sample skill profile for student
            py_skill = db.query(Skill).filter(Skill.name == "Python").first()
            sql_skill = db.query(Skill).filter(Skill.name == "SQL & Relational Databases").first()
            cloud_skill = db.query(Skill).filter(Skill.name == "Cloud Computing (AWS/GCP)").first()
            ml_skill = db.query(Skill).filter(Skill.name == "Machine Learning & AI").first()
            dsa_skill = db.query(Skill).filter(Skill.name == "Data Structures & Algorithms").first()

            if py_skill:
                db.add(SkillProfile(user_id=student_user.id, skill_id=py_skill.id, proficiency_score=85.0, is_verified=True))
            if sql_skill:
                db.add(SkillProfile(user_id=student_user.id, skill_id=sql_skill.id, proficiency_score=60.0, is_verified=False)) # Gap
            if cloud_skill:
                db.add(SkillProfile(user_id=student_user.id, skill_id=cloud_skill.id, proficiency_score=45.0, is_verified=False)) # Critical Gap
            if ml_skill:
                db.add(SkillProfile(user_id=student_user.id, skill_id=ml_skill.id, proficiency_score=78.0, is_verified=True))
            if dsa_skill:
                db.add(SkillProfile(user_id=student_user.id, skill_id=dsa_skill.id, proficiency_score=82.0, is_verified=True))

            print("Seeded student demo user.")

        # Industry Demo
        industry_user = db.query(User).filter(User.email == "industry@techcorp.com").first()
        if not industry_user:
            industry_user = User(
                email="industry@techcorp.com",
                password_hash=demo_pwd,
                full_name="Priya Patel",
                role="industry",
                is_active=True
            )
            db.add(industry_user)
            db.flush()

            company = Company(
                user_id=industry_user.id,
                name="Infosys NextGen Labs",
                industry_sector="Information Technology & Cloud Solutions",
                website="https://www.infosys.com",
                description="Global digital services and next-generation consulting enterprise.",
                location="Bengaluru, Karnataka"
            )
            db.add(company)
            db.flush()

            # Seed Opportunities with Required Skills
            opp1 = Opportunity(
                company_id=company.id,
                title="Cloud Backend Engineering Intern",
                opportunity_type="internship",
                description="Work on high-throughput microservices using Python, FastAPI, and Cloud infrastructure.",
                location="Hybrid - Bengaluru / Remote",
                stipend_salary="₹45,000 / month",
                is_active=True
            )
            opp2 = Opportunity(
                company_id=company.id,
                title="AI & Machine Learning Research Associate",
                opportunity_type="job",
                description="Design state-of-the-art predictive models and integrate multimodal APIs.",
                location="Bengaluru, Karnataka",
                stipend_salary="₹14,00,000 / annum",
                is_active=True
            )
            db.add_all([opp1, opp2])
            db.flush()

            py_skill = db.query(Skill).filter(Skill.name == "Python").first()
            cloud_skill = db.query(Skill).filter(Skill.name == "Cloud Computing (AWS/GCP)").first()
            ml_skill = db.query(Skill).filter(Skill.name == "Machine Learning & AI").first()
            sql_skill = db.query(Skill).filter(Skill.name == "SQL & Relational Databases").first()

            if py_skill and cloud_skill and sql_skill:
                db.add(OpportunitySkill(opportunity_id=opp1.id, skill_id=py_skill.id, min_proficiency=75.0, importance_weight=1.5))
                db.add(OpportunitySkill(opportunity_id=opp1.id, skill_id=cloud_skill.id, min_proficiency=70.0, importance_weight=2.0))
                db.add(OpportunitySkill(opportunity_id=opp1.id, skill_id=sql_skill.id, min_proficiency=65.0, importance_weight=1.0))

            if ml_skill and py_skill:
                db.add(OpportunitySkill(opportunity_id=opp2.id, skill_id=ml_skill.id, min_proficiency=75.0, importance_weight=2.0))
                db.add(OpportunitySkill(opportunity_id=opp2.id, skill_id=py_skill.id, min_proficiency=80.0, importance_weight=1.5))

            # Seed a Learning Program
            prog = LearningProgram(
                company_id=company.id,
                title="AWS Cloud Architecture Bootcamp",
                program_type="training",
                description="Intensive 4-week cloud training covering S3, EC2, VPCs, and IAM.",
                duration_weeks=4,
                is_active=True,
                created_at=datetime.datetime.utcnow()
            )
            db.add(prog)
            db.flush()

            if cloud_skill:
                db.add(ProgramSkill(
                    program_id=prog.id,
                    skill_id=cloud_skill.id,
                    granted_proficiency=85.0
                ))

            # Seed Application for student
            app1 = Application(
                opportunity_id=opp1.id,
                user_id=student_user.id,
                match_score=82.5,
                status="applied",
                cover_note="Highly interested in cloud backend roles.",
                resume_link=student_prof.resume_url,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
            db.add(app1)

            # Seed Enrollment for student
            enroll = ProgramEnrollment(
                program_id=prog.id,
                user_id=student_user.id,
                status="enrolled",
                enrolled_at=datetime.datetime.utcnow()
            )
            db.add(enroll)

            print("Seeded industry demo user, opportunities, learning programs and applications.")

        # Academician Demo
        acad_user = db.query(User).filter(User.email == "prof@dtu.ac.in").first()
        if not acad_user:
            acad_user = User(
                email="prof@dtu.ac.in",
                password_hash=demo_pwd,
                full_name="Dr. Rajesh Verma",
                role="academician",
                is_active=True
            )
            db.add(acad_user)
            db.flush()

            acad_prof = AcademicianProfile(
                user_id=acad_user.id,
                institution_id=dtu.id if dtu else 1,
                department="Computer Science & Engineering",
                designation="Associate Professor & Curriculum Chair",
                faculty_id="DTU-FAC-409"
            )
            db.add(acad_prof)
            print("Seeded academician demo user.")

        # Institution Admin Demo
        admin_user = db.query(User).filter(User.email == "admin@nit.ac.in").first()
        if not admin_user:
            admin_user = User(
                email="admin@nit.ac.in",
                password_hash=demo_pwd,
                full_name="Dean of Academic Affairs",
                role="institution_admin",
                is_active=True
            )
            db.add(admin_user)
            print("Seeded institution admin demo user.")

        # 4. Seed Curriculum Feedback Loop Reports & Notifications (⭐ USP)
        if db.query(CurriculumGapReport).count() == 0 and dtu:
            cloud_skill = db.query(Skill).filter(Skill.name == "Cloud Computing (AWS/GCP)").first()
            sql_skill = db.query(Skill).filter(Skill.name == "SQL & Relational Databases").first()

            if cloud_skill:
                report1 = CurriculumGapReport(
                    institution_id=dtu.id,
                    skill_id=cloud_skill.id,
                    student_cohort_avg=45.0,
                    industry_benchmark=70.0,
                    gap_score=25.0,
                    demand_frequency=5,
                    trend="rising",
                    recommendation_text="Urgent: Industry demand for Cloud Computing is surging (+40% across partner postings). Student cohort average is 45% (25pt gap). Integrate hands-on AWS/GCP lab modules into 6th semester Distributed Systems course.",
                    status="open"
                )
                db.add(report1)

            if sql_skill:
                report2 = CurriculumGapReport(
                    institution_id=dtu.id,
                    skill_id=sql_skill.id,
                    student_cohort_avg=60.0,
                    industry_benchmark=75.0,
                    gap_score=15.0,
                    demand_frequency=4,
                    trend="stable",
                    recommendation_text="Moderate gap in practical SQL indexing and query optimization. Recommend an industry guest lecture on production database tuning.",
                    status="course_updated"
                )
                db.add(report2)
                db.flush()

                # Add sample action logged by faculty
                action = CurriculumAction(
                    report_id=report2.id,
                    user_id=acad_user.id if acad_user else 3,
                    action_type="update_syllabus",
                    course_name="CS304: Database Management Systems",
                    action_notes="Added 3-week module on query plan inspection, B-Tree index analysis, and Postgres replication."
                )
                db.add(action)

            # Notifications
            db.add(Notification(
                user_id=acad_user.id if acad_user else None,
                target_role="academician",
                title="🚨 Significant Industry Skill Gap Detected",
                message="Cloud Computing (AWS/GCP) demand increased by 40% in recent partner job postings, while cohort proficiency shows a 25% gap. Review curriculum recommendations.",
                category="curriculum_alert"
            ))

            print("Seeded curriculum gap reports and notifications.")

        db.commit()
        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
