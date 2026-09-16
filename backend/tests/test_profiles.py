import pytest

def test_student_profile_crud(client, student_auth):
    """Test reading and updating student profile."""
    # Read current profile
    get_res = client.get("/api/students/profile", headers=student_auth["headers"])
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["user_id"] == student_auth["user"].id

    # Update profile
    update_payload = {
        "degree": "M.Tech",
        "branch": "Artificial Intelligence",
        "enrollment_no": "AI-2026-99",
        "grad_year": 2027,
        "career_interests": ["Deep Learning", "Robotics", "NLP"]
    }
    put_res = client.put("/api/students/profile", json=update_payload, headers=student_auth["headers"])
    assert put_res.status_code == 200
    updated_data = put_res.json()
    assert updated_data["degree"] == "M.Tech"
    assert updated_data["branch"] == "Artificial Intelligence"
    assert updated_data["enrollment_no"] == "AI-2026-99"
    assert "Deep Learning" in updated_data["career_interests"]

def test_company_profile_crud(client, industry_auth):
    """Test reading and updating company profile."""
    # Read profile
    get_res = client.get("/api/companies/profile", headers=industry_auth["headers"])
    assert get_res.status_code == 200
    assert get_res.json()["user_id"] == industry_auth["user"].id

    # Update profile
    update_payload = {
        "name": "Tata Digital Innovations",
        "industry_sector": "Digital Engineering & Cloud",
        "website": "https://www.tatadigital.com",
        "location": "Mumbai, Maharashtra",
        "description": "Leading digital transformation for enterprises worldwide."
    }
    put_res = client.put("/api/companies/profile", json=update_payload, headers=industry_auth["headers"])
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["name"] == "Tata Digital Innovations"
    assert data["location"] == "Mumbai, Maharashtra"

def test_academician_profile_and_institution(client, academician_auth):
    """Test academician profile retrieval and updates."""
    # Read institutions list
    inst_res = client.get("/api/institutions")
    assert inst_res.status_code == 200
    inst_list = inst_res.json()
    assert len(inst_list) > 0
    target_inst_id = inst_list[0]["id"]

    # Read academician profile
    prof_res = client.get("/api/institutions/academicians/profile", headers=academician_auth["headers"])
    assert prof_res.status_code == 200

    # Update academician profile
    put_res = client.put("/api/institutions/academicians/profile", json={
        "institution_id": target_inst_id,
        "department": "Department of Artificial Intelligence",
        "designation": "Head of Department (HOD)",
        "faculty_id": "HOD-AI-01"
    }, headers=academician_auth["headers"])
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["department"] == "Department of Artificial Intelligence"
    assert data["designation"] == "Head of Department (HOD)"
    assert data["institution_id"] == target_inst_id
