import pytest

def test_student_rbac(client, student_auth):
    """Student can access student routes, but forbidden from others."""
    # Student route -> 200
    res_student = client.get("/api/dashboards/student", headers=student_auth["headers"])
    assert res_student.status_code == 200
    assert res_student.json()["role"] == "student"

    # Industry route -> 403
    res_ind = client.get("/api/dashboards/industry", headers=student_auth["headers"])
    assert res_ind.status_code == 403
    assert "Access forbidden" in res_ind.json()["detail"]

    # Academician route -> 403
    res_acad = client.get("/api/dashboards/academician", headers=student_auth["headers"])
    assert res_acad.status_code == 403

    # Institution admin route -> 403
    res_admin = client.get("/api/dashboards/institution", headers=student_auth["headers"])
    assert res_admin.status_code == 403

def test_industry_rbac(client, industry_auth):
    """Industry partner can access industry routes, forbidden from student/admin routes."""
    # Industry route -> 200
    res_ind = client.get("/api/dashboards/industry", headers=industry_auth["headers"])
    assert res_ind.status_code == 200
    assert res_ind.json()["role"] == "industry"

    # Student route -> 403
    res_stu = client.get("/api/dashboards/student", headers=industry_auth["headers"])
    assert res_stu.status_code == 403

    # Academician route -> 403
    res_acad = client.get("/api/dashboards/academician", headers=industry_auth["headers"])
    assert res_acad.status_code == 403

def test_academician_rbac(client, academician_auth):
    """Academician can access academician routes and curriculum report, forbidden from industry."""
    # Academician route -> 200
    res_acad = client.get("/api/dashboards/academician", headers=academician_auth["headers"])
    assert res_acad.status_code == 200
    assert res_acad.json()["role"] == "academician"

    # Industry route -> 403
    res_ind = client.get("/api/dashboards/industry", headers=academician_auth["headers"])
    assert res_ind.status_code == 403

def test_institution_admin_rbac(client, admin_auth, student_auth):
    """Institution admin can create institutions; students cannot."""
    # Admin route -> 200
    res_admin = client.get("/api/dashboards/institution", headers=admin_auth["headers"])
    assert res_admin.status_code == 200
    assert res_admin.json()["role"] == "institution_admin"

    # Admin creates institution -> 201
    create_payload = {
        "name": "Apex University of Technology",
        "code": "AUT-999",
        "contact_email": "apex@aut.edu"
    }
    res_create = client.post("/api/institutions", json=create_payload, headers=admin_auth["headers"])
    assert res_create.status_code == 201

    # Student attempts to create institution -> 403
    res_forbidden = client.post("/api/institutions", json=create_payload, headers=student_auth["headers"])
    assert res_forbidden.status_code == 403

def test_unauthenticated_access(client):
    """Unauthenticated access to any protected route returns 401."""
    protected_endpoints = [
        "/api/dashboards/student",
        "/api/dashboards/industry",
        "/api/dashboards/academician",
        "/api/dashboards/institution",
        "/api/students/profile",
        "/api/companies/profile",
        "/api/institutions/academicians/profile"
    ]
    for ep in protected_endpoints:
        res = client.get(ep)
        assert res.status_code == 401, f"Expected 401 for {ep}, got {res.status_code}"
