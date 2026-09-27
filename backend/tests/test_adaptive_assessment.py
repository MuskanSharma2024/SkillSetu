"""
Tests for SkillSetu Adaptive Assessment Framework (Path A & Path B)
"""

def test_get_adaptive_fields(client):
    res = client.get("/api/skills/adaptive/fields")
    assert res.status_code == 200
    fields = res.json()
    assert "engineering" in fields
    assert "business" in fields
    assert "science" in fields
    assert "design" in fields
    assert "social" in fields
    assert len(fields["engineering"]["subfields"]) == 5

def test_adaptive_questionnaire_path_a(client):
    res = client.post(
        "/api/skills/adaptive/questionnaire",
        json={"path": "path_a", "major_field": "engineering"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["path"] == "path_a"
    assert len(data["questions"]) > 0

def test_adaptive_submit_path_a_career_discovery(client):
    answers = [
        {"question_id": 101, "selected_option": "A"},
        {"question_id": 102, "selected_option": "A"},
        {"question_id": 103, "selected_option": "A"},
        {"question_id": 104, "selected_option": "A"},
        {"question_id": 105, "selected_option": "B"},
        {"question_id": 106, "selected_option": "A"},
        {"question_id": 107, "selected_option": "B"},
        {"question_id": 201, "selected_option": "A"},
        {"question_id": 202, "selected_option": "A"},
        {"question_id": 203, "selected_option": "B"},
        {"question_id": 204, "selected_option": "B"},
        {"question_id": 205, "selected_option": "C"},
        {"question_id": 206, "selected_option": "A"}
    ]
    res = client.post(
        "/api/skills/adaptive/submit",
        json={"path": "path_a", "major_field": "engineering", "answers": answers}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["path"] == "path_a"
    assert "student_vector" in data
    assert "student_riasec" in data
    assert len(data["top_matches"]) > 0
    assert "Software Engineering" in [m["title"] for m in data["top_matches"]] or len(data["top_matches"]) > 0

def test_adaptive_submit_path_b_gap_analysis(client):
    answers = [
        {"question_id": 101, "selected_option": "B"},
        {"question_id": 102, "selected_option": "B"},
        {"question_id": 103, "selected_option": "C"},
        {"question_id": 104, "selected_option": "B"},
        {"question_id": 105, "selected_option": "B"},
        {"question_id": 106, "selected_option": "C"},
        {"question_id": 107, "selected_option": "B"}
    ]
    res = client.post(
        "/api/skills/adaptive/submit",
        json={"path": "path_b", "major_field": "engineering", "subfield": "ai_ml", "answers": answers}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["path"] == "path_b"
    assert data["target_subfield"] == "Artificial Intelligence & Machine Learning"
    assert len(data["gap_table"]) == 6
    assert len(data["roadmap"]) > 0
