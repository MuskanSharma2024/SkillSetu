import json

skills = [
    {"name": "Python", "category": "technical"},
    {"name": "SQL & Relational Databases", "category": "technical"},
    {"name": "Data Structures & Algorithms", "category": "technical"},
    {"name": "Cloud Computing (AWS/GCP)", "category": "technical"},
    {"name": "Machine Learning & AI", "category": "technical"},
    {"name": "REST API Design & FastAPI", "category": "technical"},
    {"name": "Web Frontend (HTML/CSS/JS)", "category": "technical"},
    {"name": "Git & CI/CD Pipelines", "category": "tools"},
    {"name": "Docker & Containers", "category": "tools"},
    {"name": "Problem Solving & Critical Thinking", "category": "soft"},
    {"name": "Team Collaboration & Agile", "category": "soft"},
    {"name": "Technical Communication", "category": "soft"}
]

questions = []
q_id = 1

for skill in skills:
    for i in range(1, 16):
        questions.append({
            "id": q_id,
            "skill_name": skill["name"],
            "question_text": f"Question {i} assessing knowledge in {skill['name']}. Which of the following is correct?",
            "category": skill["category"],
            "difficulty": "intermediate",
            "options": [
                {"id": "A", "text": "Correct Option A"},
                {"id": "B", "text": "Incorrect Option B"},
                {"id": "C", "text": "Incorrect Option C"},
                {"id": "D", "text": "Incorrect Option D"}
            ],
            "correct_option": "A",
            "points": 10.0
        })
        q_id += 1

with open('e:/SIH/SkillSetu/backend/app/questions_bank.json', 'w') as f:
    json.dump(questions, f, indent=4)
print("questions_bank.json generated with", len(questions), "questions.")
