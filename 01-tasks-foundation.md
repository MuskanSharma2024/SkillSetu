# SkillSetu — Execution Tasks: Foundation & Auth

## Task 1 — Repo & Project Setup
Initialize backend + frontend project structure, install core dependencies, connect to database.

## Task 2 — Database Setup
Create schema/migrations for: `users`, `institutions`, `student_profiles`, `companies`, `skills`.

## Task 3 — User Registration
Implement signup for all 4 roles (student, industry, academician, institution_admin) with role selection.

## Task 4 — Login & JWT Auth
Implement login endpoint, password hashing, JWT issuance + refresh token flow.

## Task 5 — Role-Based Access Control (RBAC)
Middleware that restricts each route by role; test with all 4 role types.

## Task 6 — Student Profile CRUD
Create/read/update student profile (enrollment no, career interests, resume upload link).

## Task 7 — Company Profile CRUD
Create/read/update company profile (name, industry sector) for industry-role users.

## Task 8 — Institution/Academician Profile CRUD
Create/read/update institution + academician profile linkage.

## Task 9 — Document Upload Service
Secure upload endpoint for resumes/certificates (type + size validation, stored path in `documents` table).

## Task 10 — Base Dashboards (Empty Shells)
One dashboard route per role, protected by RBAC, ready to be filled in later phases.
