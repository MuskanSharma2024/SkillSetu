import pytest
from app.models import (
    SkillAssessment, IntegrityFlag, StudentConsent, CareerCluster, 
    HireOutcome, SkillProfileSnapshot, SyllabusRevisionProposal
)

def test_assessment_integrity_flags(client, student_auth, admin_auth):
    """Test logging tab-switch telemetry, timing anomaly detection, and data minimization purge."""
    # 1. Fetch questionnaire
    q_res = client.get("/api/skills/questionnaire")
    assert q_res.status_code == 200

    # 2. Submit assessment
    answers = [
        {"question_id": 1, "skill_id": 1, "selected_option": "A"},
        {"question_id": 2, "skill_id": 1, "selected_option": "B"}
    ]
    sub_res = client.post(
        "/api/skills/assessments",
        json={"assessment_type": "diagnostic", "answers": answers},
        headers=student_auth["headers"]
    )
    assert sub_res.status_code == 200

    # 3. Log tab switch flag
    flag_res = client.post(
        "/api/skills/assessments/1/flags",
        json={"flag_type": "tab_switch", "raw_signal": "Window blur event logged at 00:01:05"},
        headers=student_auth["headers"]
    )
    assert flag_res.status_code == 201
    assert flag_res.json()["flag_type"] == "tab_switch"

    # 4. Data minimization purge
    purge_res = client.post("/api/skills/integrity-flags/purge-signals?retention_days=0", headers=admin_auth["headers"])
    assert purge_res.status_code == 200
    assert "purged_records" in purge_res.json()

def test_consent_gating_and_minor_lock(client, student_auth, admin_auth):
    """Test opt-in consent recording and minor guardian consent gate toggle."""
    # 1. Submit consent
    res = client.post(
        "/api/skills/consent",
        json={"consent_given": True, "consent_version": "1.0"},
        headers=student_auth["headers"]
    )
    assert res.status_code == 200
    assert res.json()["has_consented"] is True

    # 2. Check consent status
    status_res = client.get("/api/skills/consent/status", headers=student_auth["headers"])
    assert status_res.status_code == 200
    assert status_res.json()["can_take_assessment"] is True

    # 3. Update guardian consent as institution admin
    student_id = student_auth["user"].id
    gate_res = client.patch(
        f"/api/institutions/students/{student_id}/guardian-consent",
        json={"status": "approved"},
        headers=admin_auth["headers"]
    )
    assert gate_res.status_code == 200
    assert gate_res.json()["guardian_consent_status"] == "approved"

def test_career_clusters_and_fit_computation(client, student_auth):
    """Test listing career clusters and computing student cluster fit percentage with plain-language explanation."""
    # List clusters
    clusters_res = client.get("/api/skills/career-clusters")
    assert clusters_res.status_code == 200
    clusters = clusters_res.json()
    assert len(clusters) > 0

    # Compute fit for student
    fit_res = client.get("/api/skills/career-clusters/me", headers=student_auth["headers"])
    assert fit_res.status_code == 200
    fits = fit_res.json()
    assert len(fits) > 0
    assert "fit_percentage" in fits[0]
    assert "explanation" in fits[0]

def test_hire_outcomes_and_posting_trust_score(client, industry_auth, student_auth):
    """Test post-hire outcome reporting (3/6-month) and posting trust score generation."""
    # 1. Create opportunity and apply
    opp_payload = {
        "title": "Trust Score Opp",
        "opportunity_type": "job",
        "target_role": "student",
        "required_skills": []
    }
    opp_resp = client.post("/api/opportunities", json=opp_payload, headers=industry_auth["headers"])
    opp_id = opp_resp.json()["id"]

    # Verify trust_score is present
    assert "trust_score" in opp_resp.json()

    # Apply
    app_resp = client.post(f"/api/opportunities/{opp_id}/apply", json={}, headers=student_auth["headers"])
    app_id = app_resp.json()["id"]

    # 2. Submit post-hire outcome
    outcome_payload = {
        "interval": "3_month",
        "retained": True,
        "performance_rating": 4.8
    }
    outcome_res = client.post(
        f"/api/opportunities/applications/{app_id}/hire-outcome",
        json=outcome_payload,
        headers=industry_auth["headers"]
    )
    assert outcome_res.status_code == 201
    data = outcome_res.json()
    assert data["interval"] == "3_month"
    assert data["performance_rating"] == 4.8

def test_skill_profile_snapshots_and_growth_trends(client, student_auth):
    """Test longitudinal skill growth snapshots and trend view endpoint."""
    res = client.get("/api/skills/growth-trends/me", headers=student_auth["headers"])
    assert res.status_code == 200
    trends = res.json()
    assert "skills_trends" in trends

def test_syllabus_revision_proposal_workflow(client, academician_auth, admin_auth):
    """Test academician syllabus proposal submission and institution admin approval workflow."""
    # 1. Academician submits proposal for gap report #1
    proposal_payload = {
        "course_code": "CS501",
        "proposed_change": "Introduce hands-on Kubernetes and Terraform lab modules."
    }
    prop_res = client.post(
        "/api/skills/curriculum-reports/1/proposals",
        json=proposal_payload,
        headers=academician_auth["headers"]
    )
    assert prop_res.status_code == 201
    prop_data = prop_res.json()
    assert prop_data["course_code"] == "CS501"
    assert prop_data["status"] == "submitted"

    proposal_id = prop_data["id"]

    # 2. Academician views their submitted proposals
    my_props = client.get("/api/skills/curriculum-proposals/me", headers=academician_auth["headers"])
    assert my_props.status_code == 200
    assert len(my_props.json()) > 0

    # 3. Institution admin lists and approves proposal
    admin_list = client.get("/api/institutions/curriculum-proposals", headers=admin_auth["headers"])
    assert admin_list.status_code == 200
    assert len(admin_list.json()) > 0

    approve_res = client.patch(
        f"/api/institutions/curriculum-proposals/{proposal_id}/status",
        json={"status": "approved", "institution_admin_notes": "Approved for upcoming academic semester."},
        headers=admin_auth["headers"]
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

def test_data_export_and_deletion(client, student_auth):
    """Test GDPR/Privacy data export and deletion request endpoints."""
    # Export
    exp_res = client.get("/api/students/me/data-export", headers=student_auth["headers"])
    assert exp_res.status_code == 200
    assert "user_info" in exp_res.json()

    # Deletion request
    del_res = client.post("/api/students/me/data-deletion-request", headers=student_auth["headers"])
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"
