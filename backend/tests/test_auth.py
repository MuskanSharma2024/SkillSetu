import pytest

def test_signup_all_four_roles(client):
    """Test registration endpoint for all 4 roles."""
    roles_data = [
        {
            "email": "new_student@test.com",
            "password": "Password123!",
            "full_name": "New Student",
            "role": "student",
            "degree": "B.Tech",
            "branch": "CSE"
        },
        {
            "email": "new_industry@test.com",
            "password": "Password123!",
            "full_name": "New Recruiter",
            "role": "industry",
            "company_name": "Acme Innovations",
            "industry_sector": "Fintech"
        },
        {
            "email": "new_faculty@test.com",
            "password": "Password123!",
            "full_name": "Dr. Raman",
            "role": "academician",
            "department": "CSE",
            "designation": "Professor"
        },
        {
            "email": "new_admin@test.com",
            "password": "Password123!",
            "full_name": "College Registrar",
            "role": "institution_admin",
            "institution_name": "Global Tech University",
            "institution_code": "GTU-2026"
        }
    ]

    for payload in roles_data:
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201, f"Failed for role {payload['role']}: {resp.text}"
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["role"] == payload["role"]
        assert data["email"] == payload["email"]

def test_signup_duplicate_email(client):
    """Test that duplicate email registration returns 409 Conflict."""
    payload = {
        "email": "duplicate@test.com",
        "password": "Password123!",
        "full_name": "Original User",
        "role": "student"
    }
    resp1 = client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"].lower()

def test_login_success_and_failure(client):
    """Test login with valid and invalid credentials."""
    # Register user
    signup_payload = {
        "email": "login_test@test.com",
        "password": "CorrectPassword123!",
        "full_name": "Login User",
        "role": "student"
    }
    client.post("/api/auth/register", json=signup_payload)

    # Valid login
    resp = client.post("/api/auth/login", json={
        "email": "login_test@test.com",
        "password": "CorrectPassword123!"
    })
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Invalid password
    bad_resp = client.post("/api/auth/login", json={
        "email": "login_test@test.com",
        "password": "WrongPassword!"
    })
    assert bad_resp.status_code == 401

    # Non-existent user
    notfound_resp = client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "CorrectPassword123!"
    })
    assert notfound_resp.status_code == 401

def test_refresh_token_flow(client):
    """Test token refresh issuance."""
    signup_payload = {
        "email": "refresh_test@test.com",
        "password": "Password123!",
        "full_name": "Refresh User",
        "role": "student"
    }
    reg_resp = client.post("/api/auth/register", json=signup_payload)
    tokens = reg_resp.json()
    refresh_token = tokens["refresh_token"]

    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "student"

def test_get_current_user_me(client, student_auth):
    """Test /auth/me with valid Bearer token and invalid token."""
    # Valid
    resp = client.get("/api/auth/me", headers=student_auth["headers"])
    assert resp.status_code == 200
    assert resp.json()["email"] == student_auth["user"].email

    # Invalid
    resp_invalid = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert resp_invalid.status_code == 401
