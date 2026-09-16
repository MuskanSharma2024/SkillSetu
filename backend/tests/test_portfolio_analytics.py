import pytest
from fastapi.testclient import TestClient

def test_portfolio_me(client, student_auth):
    # Should be empty initially
    res = client.get("/api/portfolio/me", headers=student_auth["headers"])
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_student_analytics(client, student_auth):
    res = client.get("/api/analytics/student", headers=student_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert "total_applications" in data
    assert "verified_skills_count" in data

def test_industry_skill_trends(client, industry_auth):
    res = client.get("/api/analytics/industry/skill-trends", headers=industry_auth["headers"])
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_industry_funnel(client, industry_auth):
    res = client.get("/api/analytics/industry/funnel", headers=industry_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert "total_postings" in data
    assert "funnel" in data

def test_institution_summary(client, admin_auth):
    res = client.get("/api/analytics/institution/summary", headers=admin_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert "total_students" in data
    assert "internships_applied" in data

def test_audit_logs(client, admin_auth):
    res = client.get("/api/analytics/admin/audit-logs", headers=admin_auth["headers"])
    assert res.status_code == 200
    assert isinstance(res.json(), list)
