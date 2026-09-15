# SkillSetu — Execution Tasks: Skill Engine & Curriculum Feedback Loop

> ⭐ **USP focus**: The curriculum feedback loop is what makes SkillSetu more than a listing site — it's the part that closes the loop the problem statement calls out ("academicians have limited visibility into industry practices"). Prioritize Tasks 8–10 below; they're the differentiator, not just supporting features.

## Task 1 — Skill Master List
Seed `skills` table with technical + soft skills, categorized.

## Task 2 — Skill Assessment Questionnaire
Build the questionnaire/aptitude-test UI + submission endpoint; store raw answers in `skill_assessments`.

## Task 3 — Skill Scoring Logic
Convert raw answers into per-skill proficiency scores; write to `skill_profiles`.

## Task 4 — Gap Detection
Compare each student's scores against current industry-required benchmark per skill; flag gaps.

## Task 5 — Skill Profile View
Student-facing view of their generated skill profile: strengths, gaps, and target-role fit.

## Task 6 — Recommendation Engine (v1)
Rule-based weighted matching: student skill vector vs. opportunity/program requirements → ranked list.

## Task 7 — Recommendation Refresh Trigger
Re-run recommendations whenever a student's profile changes or new opportunities/programs are posted.

## Task 8 — ⭐ Industry Skill-Demand Aggregation
Aggregate required skills across all active opportunities/postings into a live "industry demand" dataset (which skills are most requested, by how many companies, trending up/down).

## Task 9 — ⭐ Skill Gap-vs-Demand Report
Cross-reference aggregate student skill gaps (Task 4) against industry demand (Task 8) to produce a per-institution "curriculum gap report" — which in-demand skills the current student cohort is weakest in.

## Task 10 — ⭐ Curriculum Feedback Dashboard (Academician/Institution)
Build the dashboard view where academicians/institution admins see the Task 9 report and can act on it — e.g. flag which courses/topics should be updated to close the gap. This is the loop back into teaching that the SRS's academician pain-point describes.

## Task 11 — Feedback Loop Notifications
Notify academicians/institution when a new significant gap or demand shift is detected (e.g. a skill jumps in demand across postings).
