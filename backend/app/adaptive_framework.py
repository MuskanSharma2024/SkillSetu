"""
SkillSetu — Adaptive Career Assessment Framework Engine
Implements Path A (Career Discovery) & Path B (Desired Career Gap Analysis)
with 6D Skill Vector [COG, MAT, ANA, CRE, TEC, SOF] and RIASEC Interest Profile.
"""

from typing import Dict, List, Any

MAJOR_FIELDS = {
    "engineering": {
        "id": "engineering",
        "name": "Engineering & Technology",
        "icon": "⚡",
        "description": "Software, AI, Data Science, Cybersecurity, and Embedded Hardware",
        "weights": {"COG": 15, "MAT": 20, "ANA": 20, "CRE": 10, "TEC": 25, "SOF": 10},
        "riasec_emphasis": ["I", "R", "C"],
        "subfields": [
            {
                "id": "software_eng",
                "name": "Software Engineering",
                "roles": ["Software Developer", "Full Stack Engineer", "Backend Developer"],
                "profile": {"COG": 75, "MAT": 75, "ANA": 80, "CRE": 60, "TEC": 90, "SOF": 70},
                "riasec": {"primary": "I", "secondary": "C"}
            },
            {
                "id": "ai_ml",
                "name": "Artificial Intelligence & Machine Learning",
                "roles": ["AI Engineer", "ML Researcher", "Computer Vision Specialist"],
                "profile": {"COG": 85, "MAT": 90, "ANA": 90, "CRE": 70, "TEC": 85, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "R/C"}
            },
            {
                "id": "data_science",
                "name": "Data Science & Analytics",
                "roles": ["Data Scientist", "Data Analyst", "BI Developer"],
                "profile": {"COG": 80, "MAT": 85, "ANA": 90, "CRE": 65, "TEC": 80, "SOF": 75},
                "riasec": {"primary": "I", "secondary": "C"}
            },
            {
                "id": "cybersecurity",
                "name": "Cybersecurity",
                "roles": ["Security Analyst", "Ethical Hacker", "SOC Engineer"],
                "profile": {"COG": 80, "MAT": 75, "ANA": 85, "CRE": 60, "TEC": 90, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "R/C"}
            },
            {
                "id": "electronics_embedded",
                "name": "Electronics & Embedded Systems",
                "roles": ["Embedded Firmware Engineer", "IoT Specialist", "Hardware Designer"],
                "profile": {"COG": 80, "MAT": 85, "ANA": 80, "CRE": 65, "TEC": 90, "SOF": 65},
                "riasec": {"primary": "R/I", "secondary": "C"}
            }
        ]
    },
    "business": {
        "id": "business",
        "name": "Business, Management & Finance",
        "icon": "📈",
        "description": "Business Strategy, Marketing, Corporate Finance, and Entrepreneurship",
        "weights": {"COG": 15, "MAT": 10, "ANA": 15, "CRE": 15, "TEC": 10, "SOF": 35},
        "riasec_emphasis": ["E", "S", "C"],
        "subfields": [
            {
                "id": "business_mgmt",
                "name": "Business Management",
                "roles": ["Product Manager", "Operations Manager", "Strategy Consultant"],
                "profile": {"COG": 75, "MAT": 65, "ANA": 75, "CRE": 75, "TEC": 60, "SOF": 90},
                "riasec": {"primary": "E", "secondary": "S/C"}
            },
            {
                "id": "marketing",
                "name": "Marketing & Digital Marketing",
                "roles": ["Marketing Manager", "Growth Lead", "Brand Strategist"],
                "profile": {"COG": 70, "MAT": 55, "ANA": 70, "CRE": 85, "TEC": 60, "SOF": 90},
                "riasec": {"primary": "E", "secondary": "A/S"}
            },
            {
                "id": "finance",
                "name": "Finance & Investment",
                "roles": ["Financial Analyst", "Investment Banker", "Risk Officer"],
                "profile": {"COG": 80, "MAT": 90, "ANA": 90, "CRE": 60, "TEC": 70, "SOF": 75},
                "riasec": {"primary": "C/E", "secondary": "I"}
            },
            {
                "id": "biz_analytics",
                "name": "Business/Data Analytics",
                "roles": ["Business Intelligence Analyst", "Analytics Consultant"],
                "profile": {"COG": 80, "MAT": 80, "ANA": 90, "CRE": 70, "TEC": 80, "SOF": 70},
                "riasec": {"primary": "I/C", "secondary": "E"}
            },
            {
                "id": "entrepreneurship",
                "name": "Entrepreneurship",
                "roles": ["Startup Founder", "Venture Builder", "Innovation Lead"],
                "profile": {"COG": 80, "MAT": 65, "ANA": 75, "CRE": 85, "TEC": 60, "SOF": 90},
                "riasec": {"primary": "E", "secondary": "A/S"}
            }
        ]
    },
    "science": {
        "id": "science",
        "name": "Science & Research",
        "icon": "🔬",
        "description": "Mathematics, Physics, Chemistry, Life Sciences, and Scientific Inquiry",
        "weights": {"COG": 20, "MAT": 20, "ANA": 25, "CRE": 10, "TEC": 15, "SOF": 10},
        "riasec_emphasis": ["I", "C", "R"],
        "subfields": [
            {
                "id": "math_stats",
                "name": "Mathematics & Statistics",
                "roles": ["Statistician", "Quantitative Analyst", "Actuary"],
                "profile": {"COG": 90, "MAT": 95, "ANA": 90, "CRE": 60, "TEC": 65, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "C"}
            },
            {
                "id": "physics",
                "name": "Physics",
                "roles": ["Research Physicist", "Nanotechnology Specialist"],
                "profile": {"COG": 85, "MAT": 90, "ANA": 90, "CRE": 70, "TEC": 75, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "R"}
            },
            {
                "id": "chemistry",
                "name": "Chemistry",
                "roles": ["Chemical Researcher", "Materials Scientist"],
                "profile": {"COG": 80, "MAT": 80, "ANA": 90, "CRE": 70, "TEC": 80, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "R"}
            },
            {
                "id": "life_sciences",
                "name": "Life Sciences & Biotechnology",
                "roles": ["Bioinformatician", "Geneticist", "Pharma Researcher"],
                "profile": {"COG": 80, "MAT": 75, "ANA": 90, "CRE": 70, "TEC": 85, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "R"}
            },
            {
                "id": "sci_research",
                "name": "Scientific/Data Research",
                "roles": ["R&D Scientist", "Research Associate"],
                "profile": {"COG": 85, "MAT": 85, "ANA": 95, "CRE": 70, "TEC": 75, "SOF": 65},
                "riasec": {"primary": "I", "secondary": "C"}
            }
        ]
    },
    "design": {
        "id": "design",
        "name": "Design & Creative Arts",
        "icon": "🎨",
        "description": "UI/UX Design, Visual Arts, Fashion, Animation, and Digital Media",
        "weights": {"COG": 10, "MAT": 5, "ANA": 10, "CRE": 40, "TEC": 15, "SOF": 20},
        "riasec_emphasis": ["A"],
        "subfields": [
            {
                "id": "ui_ux",
                "name": "UI/UX & Product Design",
                "roles": ["UX Designer", "Product Designer", "Interaction Architect"],
                "profile": {"COG": 70, "MAT": 55, "ANA": 75, "CRE": 90, "TEC": 75, "SOF": 80},
                "riasec": {"primary": "A", "secondary": "I/S"}
            },
            {
                "id": "graphic_design",
                "name": "Graphic & Visual Design",
                "roles": ["Visual Communication Designer", "Art Director"],
                "profile": {"COG": 65, "MAT": 50, "ANA": 65, "CRE": 95, "TEC": 70, "SOF": 75},
                "riasec": {"primary": "A", "secondary": "C"}
            },
            {
                "id": "fashion_design",
                "name": "Fashion & Textile Design",
                "roles": ["Apparel Designer", "Textile Stylist"],
                "profile": {"COG": 65, "MAT": 50, "ANA": 65, "CRE": 95, "TEC": 75, "SOF": 70},
                "riasec": {"primary": "A", "secondary": "R/E"}
            },
            {
                "id": "animation",
                "name": "Animation & Digital Media",
                "roles": ["3D Animator", "VFX Artist", "Motion Designer"],
                "profile": {"COG": 65, "MAT": 50, "ANA": 65, "CRE": 90, "TEC": 80, "SOF": 70},
                "riasec": {"primary": "A", "secondary": "I"}
            },
            {
                "id": "content_media",
                "name": "Content & Creative Media",
                "roles": ["Creative Writer", "Multimedia Content Lead"],
                "profile": {"COG": 70, "MAT": 50, "ANA": 65, "CRE": 90, "TEC": 65, "SOF": 85},
                "riasec": {"primary": "A", "secondary": "E/S"}
            }
        ]
    },
    "social": {
        "id": "social",
        "name": "Social, Education & Communication",
        "icon": "🤝",
        "description": "Teaching, Psychology, Human Resources, Media, and Community Development",
        "weights": {"COG": 15, "MAT": 5, "ANA": 10, "CRE": 15, "TEC": 5, "SOF": 50},
        "riasec_emphasis": ["S", "E", "A"],
        "subfields": [
            {
                "id": "education",
                "name": "Education & Teaching",
                "roles": ["Educator", "Instructional Designer", "Academic Mentor"],
                "profile": {"COG": 75, "MAT": 50, "ANA": 65, "CRE": 75, "TEC": 55, "SOF": 95},
                "riasec": {"primary": "S", "secondary": "A"}
            },
            {
                "id": "psychology",
                "name": "Psychology & Counselling",
                "roles": ["Counselor", "Behavioral Researcher", "Org Psychologist"],
                "profile": {"COG": 80, "MAT": 50, "ANA": 75, "CRE": 70, "TEC": 55, "SOF": 95},
                "riasec": {"primary": "S", "secondary": "I"}
            },
            {
                "id": "hr",
                "name": "Human Resources",
                "roles": ["Talent Acquisition Lead", "HR Business Partner"],
                "profile": {"COG": 75, "MAT": 55, "ANA": 75, "CRE": 65, "TEC": 55, "SOF": 95},
                "riasec": {"primary": "S/E", "secondary": "C"}
            },
            {
                "id": "media_comm",
                "name": "Media & Communication",
                "roles": ["PR Manager", "Corporate Communications Officer"],
                "profile": {"COG": 70, "MAT": 50, "ANA": 65, "CRE": 80, "TEC": 55, "SOF": 90},
                "riasec": {"primary": "A/E", "secondary": "S"}
            },
            {
                "id": "social_dev",
                "name": "Social/Community Development",
                "roles": ["NGO Program Director", "Community Strategist"],
                "profile": {"COG": 75, "MAT": 50, "ANA": 70, "CRE": 75, "TEC": 55, "SOF": 90},
                "riasec": {"primary": "S", "secondary": "E/A"}
            }
        ]
    }
}

QUESTION_BANK_ADAPTIVE = [
    # 6D Skill Vector Questions
    {
        "id": 101,
        "dimension": "COG",
        "question": "When faced with an unfamiliar system, how do you diagnose root causes?",
        "options": [
            {"id": "A", "text": "Deconstruct into logical modules and trace dependencies methodically", "score": 90},
            {"id": "B", "text": "Search for standard error patterns and documentation fixes", "score": 75},
            {"id": "C", "text": "Trial multiple quick tweaks until behavior changes", "score": 55},
            {"id": "D", "text": "Ask peers for assistance immediately without inspecting logs", "score": 40}
        ]
    },
    {
        "id": 102,
        "dimension": "COG",
        "question": "How quickly can you learn and adopt a completely new conceptual framework?",
        "options": [
            {"id": "A", "text": "Synthesize core paradigms rapidly through practical experiments", "score": 95},
            {"id": "B", "text": "Follow structured tutorials and reproduce sample projects", "score": 80},
            {"id": "C", "text": "Understand basics but struggle with complex edge cases", "score": 60},
            {"id": "D", "text": "Require extensive step-by-step guidance and handholding", "score": 45}
        ]
    },
    {
        "id": 103,
        "dimension": "MAT",
        "question": "Which approach best describes your proficiency with quantitative models and statistics?",
        "options": [
            {"id": "A", "text": "Comfortable with probability distributions, linear algebra, and statistical hypothesis testing", "score": 90},
            {"id": "B", "text": "Can apply formulas, calculate variance, mean, and basic regressions accurately", "score": 75},
            {"id": "C", "text": "Understand high-level charts and basic percentage calculations", "score": 60},
            {"id": "D", "text": "Avoid mathematical and quantitative analysis whenever possible", "score": 40}
        ]
    },
    {
        "id": 104,
        "dimension": "ANA",
        "question": "When analyzing a set of conflicting metric reports, what is your first step?",
        "options": [
            {"id": "A", "text": "Audit data lineage, sample distributions, and underlying assumptions", "score": 95},
            {"id": "B", "text": "Compare top-level totals and look for obvious outliers", "score": 75},
            {"id": "C", "text": "Select the report matching your initial intuition", "score": 50},
            {"id": "D", "text": "Wait for senior team members to reconcile data", "score": 35}
        ]
    },
    {
        "id": 105,
        "dimension": "CRE",
        "question": "How do you approach solving a problem when conventional solutions have failed?",
        "options": [
            {"id": "A", "text": "Brainstorm lateral, out-of-the-box approaches combining cross-domain insights", "score": 95},
            {"id": "B", "text": "Adapt existing solutions with slight design modifications", "score": 75},
            {"id": "C", "text": "Re-execute standard procedures hoping for different results", "score": 50},
            {"id": "D", "text": "Stall until alternative explicit instructions are given", "score": 35}
        ]
    },
    {
        "id": 106,
        "dimension": "TEC",
        "question": "What is your level of practical technical execution (code, tools, domain platforms)?",
        "options": [
            {"id": "A", "text": "Architect and build full production-grade applications/systems end-to-end", "score": 90},
            {"id": "B", "text": "Write clean scripts and configure standard industry tools confidently", "score": 75},
            {"id": "C", "text": "Modify existing boilerplate templates with basic tweaks", "score": 60},
            {"id": "D", "text": "Rely entirely on visual no-code tools or non-technical interfaces", "score": 40}
        ]
    },
    {
        "id": 107,
        "dimension": "SOF",
        "question": "How do you navigate high-stakes cross-functional team collaborations?",
        "options": [
            {"id": "A", "text": "Lead discussions, align diverse stakeholders, and resolve conflicts constructively", "score": 95},
            {"id": "B", "text": "Communicate clearly, deliver commitments on time, and support teammates", "score": 80},
            {"id": "C", "text": "Participate when prompted but rarely initiate or facilitate", "score": 60},
            {"id": "D", "text": "Prefer isolated individual tasks and avoid group dialogue", "score": 40}
        ]
    },

    # RIASEC Interest Profile Questions
    {
        "id": 201,
        "riasec": "R",
        "question": "How much do you enjoy hands-on work, operating equipment, or physical systems?",
        "options": [
            {"id": "A", "text": "Extremely — I love tinkering with hardware, tools, and tangible components", "score": 95},
            {"id": "B", "text": "Moderately — I enjoy occasional practical hands-on tasks", "score": 70},
            {"id": "C", "text": "Slightly — Preferred only if necessary", "score": 45},
            {"id": "D", "text": "Not at all — I prefer purely digital or conceptual tasks", "score": 20}
        ]
    },
    {
        "id": 202,
        "riasec": "I",
        "question": "How strongly are you driven to research, analyze data, and solve intellectual puzzles?",
        "options": [
            {"id": "A", "text": "Deeply driven — I thrive on deep research, theories, and complex problem-solving", "score": 95},
            {"id": "B", "text": "Quite interested in investigation when topics are relevant", "score": 75},
            {"id": "C", "text": "Neutral — I prefer executing set instructions", "score": 50},
            {"id": "D", "text": "Low interest — I prefer immediate practical or social tasks", "score": 25}
        ]
    },
    {
        "id": 203,
        "riasec": "A",
        "question": "How important is artistic expression, design aesthetics, and creative freedom to you?",
        "options": [
            {"id": "A", "text": "Essential — I constantly create, design, or express visual/written ideas", "score": 95},
            {"id": "B", "text": "Important — I appreciate aesthetics and enjoy creative flair", "score": 75},
            {"id": "C", "text": "Minor — Functionality is far more important than design", "score": 50},
            {"id": "D", "text": "Not important — I dislike unstructured creative activities", "score": 20}
        ]
    },
    {
        "id": 204,
        "riasec": "S",
        "question": "How motivated are you by helping, teaching, mentoring, or empowering people?",
        "options": [
            {"id": "A", "text": "Highly motivated — My primary fulfillment comes from positive human impact", "score": 95},
            {"id": "B", "text": "Enthusiastic about assisting colleagues and sharing knowledge", "score": 75},
            {"id": "C", "text": "Neutral — I help when asked", "score": 50},
            {"id": "D", "text": "Low motivation — I prefer task completion over interpersonal coaching", "score": 25}
        ]
    },
    {
        "id": 205,
        "riasec": "E",
        "question": "How excited are you by leading initiatives, pitching ideas, and negotiating business deals?",
        "options": [
            {"id": "A", "text": "Thrilled — I love driving strategy, persuading audiences, and taking calculated risks", "score": 95},
            {"id": "B", "text": "Comfortable taking initiative and presenting to groups", "score": 75},
            {"id": "C", "text": "Prefer supporting roles rather than public leadership", "score": 50},
            {"id": "D", "text": "Dislike sales, pitching, or organizational management", "score": 20}
        ]
    },
    {
        "id": 206,
        "riasec": "C",
        "question": "How much do you value structured procedures, data accuracy, and organized systems?",
        "options": [
            {"id": "A", "text": "Extremely — I take pride in precision, thorough documentation, and clean order", "score": 95},
            {"id": "B", "text": "Appreciate clear guidelines and organized workflows", "score": 75},
            {"id": "C", "text": "Somewhat flexible with rules and organization", "score": 50},
            {"id": "D", "text": "Thrive in chaotic, unstructured environments without guidelines", "score": 25}
        ]
    }
]

def generate_adaptive_questionnaire(path: str, major_field_id: str = "engineering", subfield_id: str = None) -> List[Dict[str, Any]]:
    """Generates tailored question sequence for Path A (Career Discovery) or Path B (Gap Analysis)."""
    field_info = MAJOR_FIELDS.get(major_field_id, MAJOR_FIELDS["engineering"])
    
    # 6D skill questions (ID 101 to 107) + RIASEC questions (201 to 206)
    questions = list(QUESTION_BANK_ADAPTIVE)
    return questions

def calculate_adaptive_results(path: str, major_field_id: str, subfield_id: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes student 6D Vector, RIASEC Profile, Career Clusters (Path A) or Skill Gap Matrix (Path B)."""
    
    # Map answers to scores
    q_map = {q["id"]: q for q in QUESTION_BANK_ADAPTIVE}
    
    vector_scores = {"COG": 70.0, "MAT": 70.0, "ANA": 70.0, "CRE": 70.0, "TEC": 70.0, "SOF": 70.0}
    vector_counts = {k: 0 for k in vector_scores}
    
    riasec_scores = {"R": 60.0, "I": 60.0, "A": 60.0, "S": 60.0, "E": 60.0, "C": 60.0}
    riasec_counts = {k: 0 for k in riasec_scores}

    for ans in answers:
        q_id = ans.get("question_id")
        opt_id = ans.get("selected_option")
        q = q_map.get(q_id)
        if not q:
            continue
            
        opt = next((o for o in q["options"] if o["id"] == opt_id), None)
        score = opt["score"] if opt else 60.0
        
        if "dimension" in q:
            dim = q["dimension"]
            vector_scores[dim] = vector_scores.get(dim, 0.0) + score
            vector_counts[dim] += 1
        elif "riasec" in q:
            r_key = q["riasec"]
            riasec_scores[r_key] = riasec_scores.get(r_key, 0.0) + score
            riasec_counts[r_key] += 1

    # Normalize 6D Vector to 0-100
    student_vector = {}
    for k, total in vector_scores.items():
        if vector_counts[k] > 0:
            student_vector[k] = round(total / vector_counts[k], 1)
        else:
            student_vector[k] = total  # fallback default

    # Normalize RIASEC to 0-100
    student_riasec = {}
    for k, total in riasec_scores.items():
        if riasec_counts[k] > 0:
            student_riasec[k] = round(total / riasec_counts[k], 1)
        else:
            student_riasec[k] = total

    field_data = MAJOR_FIELDS.get(major_field_id, MAJOR_FIELDS["engineering"])

    if path == "path_a":
        # Career Discovery Matching
        career_matches = []
        for field_key, f_val in MAJOR_FIELDS.items():
            for sf in f_val["subfields"]:
                target_prof = sf["profile"]
                
                # Match score calculation combining 6D vector distance and RIASEC alignment
                diff_sum = 0
                for d in ["COG", "MAT", "ANA", "CRE", "TEC", "SOF"]:
                    diff_sum += abs(student_vector[d] - target_prof[d])
                avg_diff = diff_sum / 6.0
                match_pct = max(35.0, round(100.0 - (avg_diff * 0.75), 1))
                
                # Reasons
                reasons = []
                if student_vector["ANA"] >= 75:
                    reasons.append("High Analytical problem-solving ability")
                if student_vector["TEC"] >= 75:
                    reasons.append("Strong Technical proficiency")
                if student_vector["SOF"] >= 75:
                    reasons.append("Excellent interpersonal & communication skills")
                if student_riasec.get("I", 0) >= 70:
                    reasons.append("Investigative research mindset")
                if student_riasec.get("A", 0) >= 70:
                    reasons.append("High Creative & visual interest")
                if not reasons:
                    reasons.append("Balanced foundational skill profile")

                career_matches.append({
                    "subfield_id": sf["id"],
                    "title": sf["name"],
                    "field_name": f_val["name"],
                    "match_percentage": match_pct,
                    "typical_roles": sf["roles"],
                    "reasons": reasons[:3],
                    "profile_required": target_prof
                })

        career_matches.sort(key=lambda x: x["match_percentage"], reverse=True)
        top_matches = career_matches[:4]

        return {
            "path": "path_a",
            "path_name": "Career Discovery",
            "major_field": field_data["name"],
            "student_vector": student_vector,
            "student_riasec": student_riasec,
            "top_strengths": sorted(student_vector.items(), key=lambda x: x[1], reverse=True)[:3],
            "top_matches": top_matches,
            "recommendation_summary": f"Based on your {field_data['name']} assessment, your top matched career path is '{top_matches[0]['title']}' with {top_matches[0]['match_percentage']}% alignment."
        }

    else:
        # Path B — Gap Analysis
        target_subfield = None
        for f_val in MAJOR_FIELDS.values():
            for sf in f_val["subfields"]:
                if sf["id"] == subfield_id:
                    target_subfield = sf
                    break
            if target_subfield:
                break
                
        if not target_subfield:
            target_subfield = field_data["subfields"][0]

        req_profile = target_subfield["profile"]
        gap_table = []
        priority_gaps = []

        dim_names = {
            "COG": "Cognitive Reasoning",
            "MAT": "Mathematical Thinking",
            "ANA": "Analytical Problem Solving",
            "CRE": "Creativity & Design",
            "TEC": "Technical Execution",
            "SOF": "Soft Skills & Communication"
        }

        for dim in ["COG", "MAT", "ANA", "CRE", "TEC", "SOF"]:
            current = student_vector[dim]
            required = req_profile[dim]
            gap = round(required - current, 1)

            if gap <= 0:
                status = "Strong"
                status_color = "success"
            elif gap <= 12:
                status = "Moderate Gap"
                status_color = "info"
            elif gap <= 25:
                status = "High Gap"
                status_color = "warning"
            else:
                status = "Critical Gap"
                status_color = "danger"

            if gap > 0:
                priority_gaps.append({"dim": dim, "name": dim_names[dim], "gap": gap, "status": status})

            gap_table.append({
                "dimension": dim,
                "dimension_name": dim_names[dim],
                "current": current,
                "required": required,
                "gap": gap if gap > 0 else 0,
                "status": status,
                "status_color": status_color
            })

        priority_gaps.sort(key=lambda x: x["gap"], reverse=True)

        roadmap = [
            f"Prioritize building foundational mastery in {priority_gaps[0]['name']}" if priority_gaps else "Maintain current excellence across technical dimensions",
            f"Complete targeted real-world projects in {target_subfield['name']}",
            "Participate in peer code reviews and industry mentoring webinars",
            "Re-assess your skill profile after 30 days of deliberate practice"
        ]

        return {
            "path": "path_b",
            "path_name": "Desired Career Gap Analysis",
            "major_field": field_data["name"],
            "target_subfield": target_subfield["name"],
            "roles": target_subfield["roles"],
            "student_vector": student_vector,
            "student_riasec": student_riasec,
            "gap_table": gap_table,
            "priority_gaps": priority_gaps,
            "roadmap": roadmap
        }
