import pytest
from fastapi.testclient import TestClient

def test_industry_post_opportunity(client, industry_auth):
    payload = {
        "title": "Backend Intern",
        "opportunity_type": "internship",
        "target_role": "student",
        "description": "Python FastAPI",
        "location": "Remote",
        "required_skills": [
            {"skill_id": 1, "min_proficiency": 70, "importance_weight": 1.0}
        ]
    }
    response = client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Backend Intern"
    assert len(data["skills"]) == 1

def test_browse_and_filter_opportunities(client, industry_auth, student_auth):
    payload = {
        "title": "Backend Intern 2",
        "opportunity_type": "internship",
        "target_role": "student",
        "required_skills": []
    }
    client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    
    response = client.get("/api/opportunities?opportunity_type=internship", headers=student_auth["headers"])
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert "applicant_match_score" in response.json()[0]

def test_student_apply_flow(client, student_auth, industry_auth):
    payload = {
        "title": "New Grad SDE",
        "opportunity_type": "job",
        "target_role": "student",
        "required_skills": []
    }
    resp = client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    opp_id = resp.json()["id"]
    
    app_payload = {"cover_note": "I love coding"}
    resp2 = client.post(f"/api/opportunities/{opp_id}/apply", json=app_payload, headers=student_auth["headers"])
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "applied"

def test_student_application_tracking(client, student_auth, industry_auth):
    # Ensure apply flow ran first
    payload = {
        "title": "Tracking Opp",
        "opportunity_type": "job",
        "target_role": "student",
        "required_skills": []
    }
    resp = client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    client.post(f"/api/opportunities/{resp.json()['id']}/apply", json={"cover_note": "Hi"}, headers=student_auth["headers"])
    
    resp = client.get("/api/opportunities/applications/me", headers=student_auth["headers"])
    assert resp.status_code == 200
    assert len(resp.json()) > 0

def test_candidate_shortlisting_and_pipeline(client, industry_auth, student_auth):
    payload = {
        "title": "Funnel Opp",
        "opportunity_type": "job",
        "target_role": "student",
        "required_skills": []
    }
    resp_opp = client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    
    client.post(f"/api/opportunities/{resp_opp.json()['id']}/apply", json={}, headers=student_auth["headers"])
    
    resp = client.get(f"/api/opportunities/company/applicants?opportunity_id={resp_opp.json()['id']}", headers=industry_auth["headers"])
    assert resp.status_code == 200
    apps = resp.json()
    assert len(apps) > 0
    app_id = apps[0]["id"]
    
    resp2 = client.patch(f"/api/opportunities/applications/{app_id}/status", json={"status": "shortlisted"}, headers=industry_auth["headers"])
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "shortlisted"

def test_mentor_feedback_submission(client, industry_auth, student_auth):
    payload = {
        "title": "Mentor Opp",
        "opportunity_type": "internship",
        "target_role": "student",
        "required_skills": []
    }
    resp_opp = client.post("/api/opportunities", json=payload, headers=industry_auth["headers"])
    client.post(f"/api/opportunities/{resp_opp.json()['id']}/apply", json={}, headers=student_auth["headers"])
    
    resp = client.get(f"/api/opportunities/company/applicants?opportunity_id={resp_opp.json()['id']}", headers=industry_auth["headers"])
    app_id = resp.json()[0]["id"]
    
    resp2 = client.post(f"/api/opportunities/applications/{app_id}/feedback", json={"mentor_rating": 4.5, "mentor_feedback": "Great job!"}, headers=industry_auth["headers"])
    assert resp2.status_code == 200
    assert resp2.json()["mentor_rating"] == 4.5
    assert resp2.json()["status"] == "completed"

def test_learning_program_flow(client, industry_auth, student_auth):
    payload = {
        "title": "Python Bootcamp",
        "program_type": "certification",
        "duration_weeks": 4,
        "skills_covered": [{"skill_id": 1, "granted_proficiency": 90.0}]
    }
    resp = client.post("/api/opportunities/programs", json=payload, headers=industry_auth["headers"])
    assert resp.status_code == 201
    prog_id = resp.json()["id"]
    
    resp2 = client.post(f"/api/opportunities/programs/{prog_id}/enroll", headers=student_auth["headers"])
    assert resp2.status_code == 201
    enrollment_id = resp2.json()["id"]
    
    resp3 = client.get("/api/opportunities/programs/my-enrollments", headers=student_auth["headers"])
    assert resp3.status_code == 200
    assert len(resp3.json()) > 0
    
    resp4 = client.post(f"/api/opportunities/programs/enrollments/{enrollment_id}/complete", headers=industry_auth["headers"])
    assert resp4.status_code == 200
    assert resp4.json()["status"] == "completed"

def test_academician_faculty_opportunities(client, academician_auth, industry_auth):
    payload = {
        "title": "AI Research Collab",
        "opportunity_type": "research_collab",
        "target_role": "faculty",
        "required_skills": []
    }
    resp = client.post("/api/opportunities", json=payload, headers=academician_auth["headers"])
    assert resp.status_code == 201
    opp_id = resp.json()["id"]
    
    resp2 = client.post(f"/api/opportunities/{opp_id}/apply", json={"cover_note": "Interested"}, headers=academician_auth["headers"])
    assert resp2.status_code == 201
    
    resp3 = client.get("/api/opportunities?target_role=faculty", headers=academician_auth["headers"])
    assert resp3.status_code == 200
    assert len(resp3.json()) > 0
