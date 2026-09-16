# SkillSetu — Execution Tasks: SRS Delta (Integrity, Ethics, Outcomes & USP Hardening)

> This file covers everything added to the SRS (§4.8, §5, §10, and related FR-STU-13 /
> FR-ACA-10 / FR-IND-09 / FR-IND-10 / FR-ADM-06 / FR-ADM-07) that is **not** present in the
> four already-executed task files (01-foundation, 02-skill-engine, 03-opportunities,
> 04-portfolio-analytics). Every task here is additive — new tables/columns/endpoints on top
> of what's already built, not a rewrite of anything shipped.

---

## A. Assessment Integrity Layer (SRS §4.8, FR-ADM-07)

*Retrofits into the already-built questionnaire from 02-tasks-skill-engine Task 2.*

### Task A1 — `integrity_flags` Table
New table: `id`, `assessment_id` (FK to `skill_assessments`), `flag_type`
(`tab_switch` | `timing_anomaly` | `self_rating_mismatch`), `raw_signal`, `created_at`.
Raw signal retained only as long as needed to audit the derived score (data-minimization,
§10) — define and implement a retention/purge window.

### Task A2 — Tab-Switch / Window-Blur Detection
Instrument the timed sections (Cognitive, Mathematical, and the Technical validation
mini-quiz) to log a `tab_switch` flag on blur/visibility-change events. Does not block or
fail the attempt — logs only.

### Task A3 — Timing-Anomaly Detection
Server-side check: if an answer is submitted faster than the human-plausible floor for
that item type, log a `timing_anomaly` flag.

### Task A4 — Self-Rating vs. Quiz-Validated Mismatch Flag
Where the Technical section's self-rated Likert score diverges sharply from the
quiz-validated score (the scoring blend already exists per Task 3 in 02-tasks-skill-engine),
additionally log a `self_rating_mismatch` flag — this is a new *flag*, not a new scoring rule.

### Task A5 — Integrity Review Dashboard (Institution Admin)
New admin-facing view listing flagged assessments for review (FR-ADM-07). Does not expose
raw behavioural signal beyond what's needed for review — surface flag type + count, not a
full replay.

---

## B. Ethics & Consent (SRS §10)

*Retrofits into the already-built questionnaire entry flow.*

### Task B1 — Consent Screen
Add a mandatory opt-in consent step before the questionnaire (Task 2 in
02-tasks-skill-engine) can start: plain-language explanation of what is measured, who can
see it, and that cohort-level results feed the Curriculum Feedback Loop in anonymized/
aggregate form only. Block start until consent is recorded; store consent timestamp + version
of the consent text shown.

### Task B2 — Non-Clinical Disclaimer Copy
Add the required disclaimer to the questionnaire intro: this is a career-guidance
instrument, not a psychometric/psychological/clinical assessment.

### Task B3 — Minor / Institutional Consent Gate
Where applicable under institutional policy, gate account activation for minors on
institutional/guardianship consent before the questionnaire unlocks.

### Task B4 — Data Access & Deletion Request
Student-facing action to request a copy of, or deletion of, their own assessment data,
subject to institutional academic-record retention rules. Deletion should cascade
appropriately without breaking aggregate (anonymized) curriculum-feedback statistics
already computed from it.

### Task B5 — No Raw Section-Score Disclosure to Industry
Audit existing industry-facing views (candidate search/shortlisting from
03-tasks-opportunities) to confirm only the Career Cluster fit % + explanation is ever
shown externally — never a raw section-level score (e.g., a specific Creativity sub-score).

---

## C. Career Cluster Layer — Verify or Build (SRS §4.5, FR-STU-03/04/05)

### Task C0 — Confirm Existing Behaviour First
Before building anything here, confirm with whoever implemented Task 6 in
02-tasks-skill-engine whether the "Recommendation Engine (v1)" already includes an
intermediate Career Cluster layer, or matches students directly to postings/programs.

### Task C1 — `career_clusters` Table (if not already present)
Cluster name, ideal skill-weight vector (per-skill or per-dimension, matching whatever
`skill_profiles` shape Task 3 already produces), ideal interest/preference signature,
associated job roles. Seed an initial cluster set.

### Task C2 — Cluster Fit Computation (if not already present)
Compute top-5 cluster fit % + a plain-language explanation naming the 2–3 strongest
contributing skills, ahead of (not replacing) the existing posting-level ranking from
Task 6. Version the cluster vectors so past explanations stay auditable (needed for Task E2).

---

## D. Outcome Reporting & Posting Trust (SRS FR-IND-09, FR-IND-10)

### Task D1 — `hire_outcomes` Table
New table distinct from the existing internship completion/mentor-feedback record
(03-tasks-opportunities Task 8): `application_id`, `reported_at`, `interval`
(`3_month` | `6_month`), `retained` (bool), `performance_rating`. This is specifically
post-*hire* (placement) outcome tracking, not internship completion feedback.

### Task D2 — Industry Outcome-Reporting Flow
UI/endpoint for industry to submit a `hire_outcomes` record at the defined interval after a
selection. Simple reminder/notification to prompt industry at the 3/6-month mark.

### Task D3 — Posting Trust Score
Computed field on `postings` (or the `opportunities` table from
03-tasks-opportunities Task 1): historical conversion rate + average response time +
aggregated `hire_outcomes` ratings for that company. Display on the student-facing posting
card and search/browse view (Task 3 in 03-tasks-opportunities).

---

## E. Longitudinal Skill Growth & Outcome-Validated Recalibration (SRS FR-STU-13, §5.2, §5.3)

### Task E1 — Skill Growth Trend View (Student)
Trend-line chart per skill dimension across all past `skill_profiles` snapshots for a
student (history already implied by re-running the questionnaire — confirm snapshots
aren't being overwritten in place; if they are, add versioning now). Annotate each
gap-between-snapshots with which course/program/internship (from
03-tasks-opportunities Tasks 10–11) was completed in between.

### Task E2 — Academician Growth View
Surface the same trend data, aggregated for an academician's assigned students/sections,
alongside the existing participation/placement view (04-tasks-portfolio-analytics Task 7).

### Task E3 — Outcome-Validated Cluster Recalibration Job
Scheduled job: periodically adjust `career_clusters` ideal vectors using accumulated
`hire_outcomes` data — clusters whose high-fit matches consistently under-perform get
weightings adjusted down; consistently successful clusters get weighting confidence
increased. Log every recalibration (old vector, new vector, date, triggering data volume)
for auditability.

---

## F. Structured Curriculum Feedback Workflow (SRS FR-ACA-10, FR-ADM-06)

*Upgrades the informal "flag courses to update" behaviour already sketched in
02-tasks-skill-engine Task 10 into a trackable, approvable workflow.*

### Task F1 — `syllabus_revision_proposals` Table
`id`, `curriculum_report_id` (links to the existing gap-vs-demand report from
02-tasks-skill-engine Task 9), `submitted_by` (academician), `course_code`,
`proposed_change`, `status` (`submitted` | `under_review` | `approved` | `rejected`),
`institution_admin_notes`.

### Task F2 — Academician Submission Flow
From the existing Curriculum Feedback Dashboard (02-tasks-skill-engine Task 10), let an
academician submit a structured proposal instead of only an informal flag.

### Task F3 — Institution Admin Review/Approval Flow
New admin view to review, comment on, and approve/reject submitted proposals; status
changes notify the submitting academician.

### Task F4 — Anonymization Guarantee — Test Coverage
Add an explicit test/check confirming the cohort aggregation feeding Tasks 8–9 in
02-tasks-skill-engine cannot be reverse-engineered to identify an individual student
(e.g., enforce a minimum cohort size before a gap statistic is surfaced).

---

## Suggested build order

1. **A + B** first (integrity + consent) — these patch a live, already-in-use questionnaire;
   don't let more assessment attempts accumulate without them.
2. **C0** (confirm, don't assume) → **C1–C2** if actually missing.
3. **F** (structured proposal workflow) — highest USP visibility for evaluators, builds
   directly on what Task 8–10 already computed.
4. **D** (outcome reporting + trust score) — needs real applications/hires to exist first,
   so naturally comes after the above are live.
5. **E** (growth trend + recalibration) — E1/E2 can happen anytime after A; E3 needs
   meaningful `hire_outcomes` volume from D, so do it last.
