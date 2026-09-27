import pytest

def test_skill_master_list(client):
    """Test retrieving skills master list."""
    res = client.get("/api/skills")
    assert res.status_code == 200
    skills = res.json()
    assert len(skills) > 0
    names = [s["name"] for s in skills]
    assert "Python" in names

def test_assessment_questionnaire_and_submission(client, student_auth):
    """Test questionnaire fetching and submission scoring logic."""
    # 1. Fetch questions
    q_res = client.get("/api/skills/questionnaire")
    assert q_res.status_code == 200
    questions = q_res.json()
    assert len(questions) > 0

    # 2. Submit answers
    answers = [
        {"question_id": 1, "skill_id": 1, "selected_option": "A"}, # Correct (Python -> 85.0)
        {"question_id": 2, "skill_id": 1, "selected_option": "A"}, # Correct (Python -> 85.0)
        {"question_id": 54, "skill_id": 3, "selected_option": "B"}  # Incorrect (Cloud Computing -> 35.0, Gap)
    ]
    sub_res = client.post(
        "/api/skills/assessments",
        json={"assessment_type": "diagnostic", "answers": answers},
        headers=student_auth["headers"]
    )
    assert sub_res.status_code == 200
    result = sub_res.json()
    assert "scores_per_skill" in result
    assert "Python" in result["scores_per_skill"]
    assert result["scores_per_skill"]["Python"] == 85.0
    assert len(result["gaps_detected"]) > 0

def test_student_skill_profile_view(client, student_auth):
    """Test student-facing view of strengths, gaps, and overall readiness."""
    res = client.get("/api/skills/profile/me", headers=student_auth["headers"])
    assert res.status_code == 200
    profile = res.json()
    assert "top_strengths" in profile
    assert "critical_gaps" in profile
    assert "overall_readiness_score" in profile

def test_industry_skill_demand_and_curriculum_feedback(client, academician_auth, industry_auth):
    """
    Test ⭐ USP: Industry skill-demand aggregation and academician curriculum gap report & action logging.
    """
    # 1. Industry demand aggregation
    demand_res = client.get("/api/skills/industry-demand")
    assert demand_res.status_code == 200
    demand_data = demand_res.json()
    assert "top_demanded_skills" in demand_data
    assert len(demand_data["top_demanded_skills"]) > 0

    # 2. Academician accesses curriculum gap report
    report_res = client.get("/api/skills/curriculum-gap-report", headers=academician_auth["headers"])
    assert report_res.status_code == 200
    reports = report_res.json()
    assert len(reports) > 0
    first_report = reports[0]
    assert "gap_score" in first_report
    assert "industry_benchmark" in first_report

    # 3. Academician logs a curriculum action (syllabus update)
    action_payload = {
        "action_type": "update_syllabus",
        "course_name": "CS402: Cloud Native Microservices",
        "action_notes": "Integrated hands-on containerized lab assignments to close cloud computing gap."
    }
    action_res = client.post(
        f"/api/skills/curriculum-reports/{first_report['id']}/actions",
        json=action_payload,
        headers=academician_auth["headers"]
    )
    assert action_res.status_code == 201
    action_data = action_res.json()
    assert action_data["course_name"] == "CS402: Cloud Native Microservices"
    assert action_data["report_id"] == first_report["id"]

    # 4. Verify action appears in report action history
    history_res = client.get(
        f"/api/skills/curriculum-reports/{first_report['id']}/actions",
        headers=academician_auth["headers"]
    )
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1
