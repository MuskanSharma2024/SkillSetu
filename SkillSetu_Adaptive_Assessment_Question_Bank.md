# SkillSetu — Adaptive Assessment Question Bank & Selection Rules

> **Purpose:** This file is the executable/reference question-bank specification that must be used **after** `SkillSetu_Adaptive_Assessment_Framework.md`.
>
> **Continuity rule:** The assessment engine must first load and follow `SkillSetu_Adaptive_Assessment_Framework.md` for the overall assessment model, five major fields, subfields, 6D weights, RIASEC profiles, and two assessment paths. It must then load **this file** for the actual question bank, question metadata, scoring tags, and question-selection rules.
>
> **Do not treat this file as a replacement for the framework file.** It is the next layer: `Framework → Selection Rules → Question Bank → Adaptive Assessment → Scoring`.

---

## 1. Required Assessment Flow

The system must follow this order:

```text
Load SkillSetu_Adaptive_Assessment_Framework.md
        ↓
Ask assessment goal
        ↓
┌───────────────────────────────┐
│ A. Career Discovery           │
│ B. Desired Career Gap Analysis│
└───────────────────────────────┘
        ↓
Select Major Field
        ↓
IF A → use major-field 6D weights + RIASEC
IF B → select Subfield → use subfield requirement profile
        ↓
Load questions from this file
        ↓
Apply dimension + field + subfield + difficulty filters
        ↓
Run adaptive assessment
        ↓
Calculate 6D scores
        ↓
IF A → calculate RIASEC + career/subfield profile matching
IF B → compare current profile with required profile
        ↓
Generate explainable result
```

### Important

The system must **not randomly select questions from the entire question bank**.

Every selected question must satisfy the applicable:

- Assessment mode
- Major field
- Subfield, where applicable
- Skill dimension
- Difficulty
- Question-type requirement
- Previous-question exclusion rule

---

# 2. Six-Dimensional Skill Tags

Use these exact codes:

| Code | Dimension | Measures |
|---|---|---|
| COG | Cognitive | Logic, comprehension, patterns, reasoning, learning |
| MAT | Mathematical | Quantitative reasoning, numerical thinking, statistics, mathematics |
| ANA | Analytical | Data interpretation, decomposition, evidence-based reasoning, decisions |
| CRE | Creativity | Idea generation, originality, design thinking, alternatives |
| TEC | Technical | Programming, tools, systems, technical concepts |
| SOF | Soft Skills | Communication, teamwork, leadership, adaptability, organization |

All skill scores should ultimately be normalized to **0–100**.

---

# 3. Difficulty Levels

Every question has one of:

- `Easy`
- `Medium`
- `Hard`

### Adaptive rule

Start with a balanced baseline appropriate to the selected field.

For the first 10 skill questions:

- Approximately 40% Easy
- Approximately 40% Medium
- Approximately 20% Hard

Then adapt.

For each recent batch of 5 questions:

- **4–5 correct:** increase difficulty for the next relevant questions.
- **2–3 correct:** maintain difficulty.
- **0–1 correct:** reduce difficulty for the next relevant questions.

Do not jump directly from Easy to Hard based on one answer.

The engine should consider performance across a small batch.

---

# 4. Question Selection Rules

## 4.1 Career Discovery

When the student chooses **Career Discovery**:

1. Load the selected major field's 6D weightage from `SkillSetu_Adaptive_Assessment_Framework.md`.
2. Convert the percentages into question counts.
3. Select questions from this file matching each dimension.
4. Maintain coverage of all six dimensions where practical.
5. Run a separate RIASEC interest assessment.
6. Compare the resulting 6D + RIASEC profile with the framework's field/subfield requirement profiles.

### Example — Engineering & Technology

Framework weights:

- COG 15%
- MAT 20%
- ANA 20%
- CRE 10%
- TEC 25%
- SOF 10%

For a 30-question skill assessment, use approximately:

- COG: 5
- MAT: 6
- ANA: 6
- CRE: 3
- TEC: 7
- SOF: 3

Small rounding adjustments are allowed.

### Example — Design & Creative Arts

Use substantially more CRE questions because the framework assigns the highest weight to Creativity.

### Example — Business, Management & Finance

Use substantially more SOF questions, while retaining meaningful COG, ANA and CRE coverage.

---

# 5. Desired Career Gap Analysis

When the student chooses **Desired Career Gap Analysis**:

1. Ask for the major field.
2. Ask for the subfield.
3. Load the subfield requirement profile from the framework.
4. Select questions from the relevant 6D dimensions.
5. Add subfield-specific technical/domain questions where available.
6. Compare the student's measured level with the required level.

Formula:

`Gap = Required Level - Current Level`

Interpretation:

- `Gap <= 0` → Strong / Meets requirement
- `Gap 1–10` → Small development area
- `Gap 11–20` → Moderate gap
- `Gap 21–30` → High gap
- `Gap > 30` → Critical development gap

These thresholds are configurable.

The system must **not** tell a student that they are "unsuitable" for a career. It should identify their current profile and development areas.

---

# 6. Question Metadata Standard

Every question in the database should use this structure:

```text
Question ID:
Dimension:
Major Field:
Subfield:
Difficulty:
Question Type:
Question:
Options:
Correct Answer:
Skill Tested:
Selection Rule:
Adaptive Rule:
```

For situational questions, use:

```text
Best Answer:
```

instead of `Correct Answer` when appropriate.

---

# 7. COG — Cognitive Question Bank

## COG-01

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Easy  
**Question Type:** MCQ

**Question:**  
A train travels 60 km in 1 hour. At the same speed, how far will it travel in 3 hours?

A. 120 km  
B. 150 km  
C. 180 km  
D. 240 km

**Correct Answer:** C

**Skill Tested:** Basic reasoning and proportional thinking

**Selection Rule:**  
Use for any field when a basic cognitive reasoning question is required.

**Adaptive Rule:**  
If answered correctly, another COG question of equal or higher difficulty may follow.

---

## COG-02

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Easy  
**Question Type:** Logical MCQ

**Question:**  
All programmers in a team know Python. Ravi is a programmer in the team. What can definitely be concluded?

A. Ravi knows Java  
B. Ravi knows Python  
C. Ravi is the team leader  
D. Everyone who knows Python is a programmer

**Correct Answer:** B

**Skill Tested:** Logical deduction

**Selection Rule:**  
General-purpose COG question.

---

## COG-03

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Easy  
**Question Type:** Pattern MCQ

**Question:**  
Find the next number:

2, 4, 8, 16, ?

A. 20  
B. 24  
C. 30  
D. 32

**Correct Answer:** D

**Skill Tested:** Pattern recognition

---

## COG-04

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Medium  
**Question Type:** Logical MCQ

**Question:**  
A box contains red, blue and green balls. Every red ball is larger than every blue ball, and every green ball is smaller than every blue ball. Which statement must be true?

A. Every red ball is larger than every green ball  
B. Every green ball is larger than every red ball  
C. Some blue balls are larger than red balls  
D. Red and green balls have equal size

**Correct Answer:** A

**Skill Tested:** Logical relationship reasoning

---

## COG-05

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Medium  
**Question Type:** Ordering MCQ

**Question:**  
A student studies Python before SQL, SQL before statistics, and statistics before machine learning. Which subject must be studied first?

A. SQL  
B. Statistics  
C. Python  
D. Machine Learning

**Correct Answer:** C

**Skill Tested:** Sequential reasoning

---

## COG-06

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Medium  
**Question Type:** Ordering MCQ

**Question:**  
Three people A, B and C have different heights. A is taller than B. C is taller than A. Who is shortest?

A. A  
B. B  
C. C  
D. Cannot determine

**Correct Answer:** B

**Skill Tested:** Ordering logic

---

## COG-07

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Hard  
**Question Type:** Constraint reasoning

**Question:**  
Five tasks must be completed. P must occur before Q, Q before R, and S before T. Which sequence is valid?

A. Q, P, S, R, T  
B. P, Q, S, T, R  
C. S, P, Q, T, R  
D. R, P, Q, S, T

**Correct Answer:** C

**Skill Tested:** Constraint reasoning

---

## COG-08

**Dimension:** COG  
**Major Field:** ALL  
**Subfield:** ALL  
**Difficulty:** Hard  
**Question Type:** Conditional reasoning

**Question:**  
A rule says:

> If a project uses AI, it must have a testing phase.

Project X has no testing phase.

What can logically be concluded?

A. X definitely uses AI  
B. X definitely does not use AI  
C. X may or may not use AI  
D. X is successful

**Correct Answer:** B

**Skill Tested:** Conditional reasoning

---

# 8. MAT — Mathematical Question Bank

## MAT-01

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Easy  
**Question Type:** MCQ

**Question:**  
What is 20% of 250?

A. 25  
B. 40  
C. 50  
D. 75

**Correct Answer:** C

**Skill Tested:** Percentage calculation

---

## MAT-02

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
If x + 7 = 15, what is x?

A. 6  
B. 7  
C. 8  
D. 9

**Correct Answer:** C

**Skill Tested:** Basic algebra

---

## MAT-03

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
A ratio is 2:3. If the first quantity is 20, what is the second?

A. 25  
B. 30  
C. 35  
D. 40

**Correct Answer:** B

**Skill Tested:** Ratio reasoning

---

## MAT-04

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
A number increases from 80 to 100. What is the percentage increase?

A. 20%  
B. 25%  
C. 30%  
D. 40%

**Correct Answer:** B

**Skill Tested:** Percentage reasoning

---

## MAT-05

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
The mean of 10, 20, 30 and x is 25. What is x?

A. 30  
B. 35  
C. 40  
D. 45

**Correct Answer:** C

**Skill Tested:** Mean and algebra

---

## MAT-06

**Dimension:** MAT  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
A fair coin is tossed twice. What is the probability of getting exactly one head?

A. 1/4  
B. 1/2  
C. 3/4  
D. 1

**Correct Answer:** B

**Skill Tested:** Probability

---

## MAT-07

**Dimension:** MAT  
**Major Field:** Science & Research  
**Subfield:** Mathematics & Statistics / Scientific/Data Research  
**Difficulty:** Hard

**Question:**  
A dataset has values:

2, 4, 6, 8, 10

If every value is multiplied by 3, what happens to the mean?

A. It becomes one-third  
B. It remains unchanged  
C. It becomes three times  
D. It increases by 3

**Correct Answer:** C

**Skill Tested:** Statistical transformation

---

## MAT-08

**Dimension:** MAT  
**Major Field:** Engineering & Technology; Science & Research  
**Subfield:** AI & Machine Learning / Data Science & Analytics / Scientific Data Research  
**Difficulty:** Hard

**Question:**  
A model has a 70% probability of correctly classifying an individual case. Assuming independent cases, what is the probability that it correctly classifies both of two cases?

A. 0.14  
B. 0.49  
C. 0.70  
D. 1.40

**Correct Answer:** B

**Skill Tested:** Probability

---

# 9. ANA — Analytical Question Bank

## ANA-01

**Dimension:** ANA  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
A company receives:

- Monday: 100 orders
- Tuesday: 120
- Wednesday: 150

Which day had the highest number of orders?

A. Monday  
B. Tuesday  
C. Wednesday  
D. Same every day

**Correct Answer:** C

**Skill Tested:** Data interpretation

---

## ANA-02

**Dimension:** ANA  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
A student has:

- Python: 80%
- SQL: 60%
- Statistics: 70%

Which skill has the lowest score?

**Correct Answer:** SQL

**Skill Tested:** Comparative analysis

---

## ANA-03

**Dimension:** ANA  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
A website receives 10,000 visitors. 2,000 leave immediately. What is the approximate bounce rate?

A. 10%  
B. 20%  
C. 50%  
D. 80%

**Correct Answer:** B

**Skill Tested:** Data interpretation

---

## ANA-04

**Dimension:** ANA  
**Major Field:** Business, Management & Finance  
**Subfield:** Business/Data Analytics  
**Difficulty:** Medium

**Question:**

| Month | Sales |
|---|---:|
| January | ₹50k |
| February | ₹60k |
| March | ₹58k |
| April | ₹72k |

Which statement is supported by the data?

A. Sales continuously increased  
B. April had the highest sales  
C. March had the highest sales  
D. February had the lowest sales

**Correct Answer:** B

**Skill Tested:** Data-based reasoning

---

## ANA-05

**Dimension:** ANA  
**Major Field:** Engineering & Technology; Science & Research  
**Subfield:** AI/ML, Data Science, Scientific/Data Research  
**Difficulty:** Medium

**Question:**  
A model performs with 98% training accuracy and 65% testing accuracy. What is the most likely concern?

A. Underfitting  
B. Overfitting  
C. Missing data only  
D. Perfect generalization

**Correct Answer:** B

**Skill Tested:** Analytical interpretation of model performance

---

## ANA-06

**Dimension:** ANA  
**Major Field:** ALL  
**Difficulty:** Hard

**Question:**  
An experiment shows:

Group A conversion = 5%  
Group B conversion = 5.2%

Before declaring B better, what should be investigated?

A. Statistical significance and sample size  
B. Logo color  
C. Font size only  
D. Employee birthdays

**Correct Answer:** A

**Skill Tested:** Evidence-based decision making

---

# 10. CRE — Creativity Question Bank

Creativity questions should assess **problem solving and alternative thinking**, not simply ask whether the student considers themselves creative.

## CRE-01

**Dimension:** CRE  
**Major Field:** Design & Creative Arts; ALL  
**Difficulty:** Easy

**Question:**  
A user says:

> "This app has too many buttons and I don't know where to start."

Which redesign approach demonstrates the most useful creative thinking?

A. Add more buttons  
B. Remove everything  
C. Group functions and create a clearer visual hierarchy  
D. Change only the background color

**Correct Answer:** C

**Skill Tested:** Creative problem solving

---

## CRE-02

**Dimension:** CRE  
**Major Field:** Business, Management & Finance; Design & Creative Arts; Media & Communication  
**Difficulty:** Medium

**Question:**  
You need to advertise a water bottle to college students using only one image and three words. Which approach demonstrates stronger creative thinking?

A. "BUY WATER BOTTLE NOW"  
B. Show a student carrying the bottle with a memorable short phrase  
C. List all technical specifications  
D. Use the company's address as the main text

**Correct Answer:** B

**Skill Tested:** Creative communication

---

## CRE-03

**Dimension:** CRE  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
A team has very little budget for a college event. Which approach demonstrates creative problem solving?

A. Cancel immediately  
B. Find alternative resources, partnerships and reusable materials  
C. Spend more money  
D. Ignore the budget

**Correct Answer:** B

**Skill Tested:** Resourceful problem solving

---

## CRE-04

**Dimension:** CRE  
**Major Field:** Design & Creative Arts; Business, Management & Finance  
**Difficulty:** Hard

**Question:**  
A user complains that an application is boring despite having all required functions. What should be explored first?

A. Only increase animations  
B. User needs, interaction flow and visual hierarchy  
C. Delete the application  
D. Add random features

**Correct Answer:** B

**Skill Tested:** Design thinking and problem framing

---

# 11. TEC — Technical Question Bank

Technical questions must be used more heavily for technical subfields.

## TEC-01

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Software Engineering; Data Science & Analytics; AI & Machine Learning  
**Difficulty:** Easy

**Question:**  
Which data structure follows FIFO?

A. Stack  
B. Queue  
C. Tree  
D. Graph

**Correct Answer:** B

**Skill Tested:** Fundamental data structures

---

## TEC-02

**Dimension:** TEC  
**Major Field:** Engineering & Technology; Science & Research  
**Subfield:** AI & Machine Learning; Data Science & Analytics; Scientific/Data Research  
**Difficulty:** Easy

**Question:**  
Which language is commonly used for data science?

A. Python  
B. HTML  
C. CSS  
D. XML

**Correct Answer:** A

**Skill Tested:** Basic programming/data-tool awareness

---

## TEC-03

**Dimension:** TEC  
**Major Field:** Engineering & Technology; Business, Management & Finance  
**Subfield:** Software Engineering; Data Science & Analytics; Business/Data Analytics  
**Difficulty:** Easy

**Question:**  
What does SQL primarily help with?

A. Image editing  
B. Database operations  
C. Video editing  
D. Hardware manufacturing

**Correct Answer:** B

**Skill Tested:** Database fundamentals

---

## TEC-04

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Software Engineering; AI & Machine Learning; Data Science & Analytics; Cybersecurity  
**Difficulty:** Medium

**Question:**  
What is the primary purpose of Git?

A. Database hosting  
B. Version control  
C. Image compression  
D. Operating system management

**Correct Answer:** B

**Skill Tested:** Software development workflow

---

## TEC-05

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Software Engineering; AI & Machine Learning; Data Science & Analytics; Cybersecurity  
**Difficulty:** Medium

**Question:**  
Which HTTP method is commonly used to retrieve data from an API?

A. GET  
B. PUSH  
C. FETCH  
D. READ

**Correct Answer:** A

**Skill Tested:** Web/API fundamentals

---

## TEC-06

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Cybersecurity; Software Engineering  
**Difficulty:** Medium

**Question:**  
Which technique converts a password into a fixed-length representation designed to be one-way?

A. Hashing  
B. Compression  
C. Rendering  
D. Sorting

**Correct Answer:** A

**Skill Tested:** Security fundamentals

---

## TEC-07

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Software Engineering; Data Science & Analytics  
**Difficulty:** Hard

**Question:**  
A program becomes slow when searching for an element in a list of one million unsorted elements. Which change can improve lookup performance when appropriate?

A. Use a suitable indexed data structure  
B. Add comments  
C. Rename variables  
D. Increase screen resolution

**Correct Answer:** A

**Skill Tested:** Data structures and performance reasoning

---

## TEC-08 — AI/ML Specific

**Dimension:** TEC  
**Major Field:** Engineering & Technology  
**Subfield:** Artificial Intelligence & Machine Learning  
**Difficulty:** Medium

**Question:**  
Which situation is a common sign of overfitting?

A. High training performance but substantially lower performance on unseen data  
B. Low training and low testing performance  
C. No training data  
D. Identical predictions for every input

**Correct Answer:** A

**Skill Tested:** Machine learning fundamentals

**Selection Rule:**  
Use when the selected subfield is AI/ML.

---

# 12. SOF — Soft Skill Question Bank

Soft-skill questions should use **situational judgment** rather than asking students to rate themselves.

## SOF-01

**Dimension:** SOF  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
Your teammate has not completed their part of a project one day before submission. What is the most constructive first response?

A. Publicly blame them  
B. Understand the blocker and agree on a concrete plan  
C. Ignore it  
D. Immediately remove them

**Best Answer:** B

**Skill Tested:** Teamwork and problem resolution

---

## SOF-02

**Dimension:** SOF  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
During a meeting, someone disagrees with your idea. What should you do?

A. Interrupt them  
B. Ask them to explain their reasoning  
C. End the discussion  
D. Say they are wrong

**Best Answer:** B

**Skill Tested:** Communication and active listening

---

## SOF-03

**Dimension:** SOF  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
You receive criticism about your presentation. What is the most useful response?

A. Reject all criticism  
B. Ask for specific examples and identify what can be improved  
C. Stop presenting  
D. Blame the audience

**Best Answer:** B

**Skill Tested:** Adaptability and feedback handling

---

## SOF-04

**Dimension:** SOF  
**Major Field:** ALL  
**Difficulty:** Medium

**Question:**  
Two teammates strongly disagree about implementation. What should the team do first?

A. Let the loudest person decide  
B. Compare both approaches against agreed requirements  
C. Avoid the problem  
D. Vote without discussion

**Best Answer:** B

**Skill Tested:** Collaborative decision making

---

## SOF-05

**Dimension:** SOF  
**Major Field:** ALL  
**Difficulty:** Easy

**Question:**  
You don't understand an assigned task. What is the best initial action?

A. Pretend you understand  
B. Clarify the expected outcome and constraints  
C. Submit random work  
D. Wait until the deadline

**Best Answer:** B

**Skill Tested:** Communication and initiative

---

# 13. RIASEC Interest Assessment

RIASEC questions are **interest questions**, not ability questions.

Use a 1–5 scale:

```text
1 = Strongly Dislike
2 = Dislike
3 = Neutral
4 = Like
5 = Strongly Like
```

Calculate the average for each RIASEC category.

---

## R — Realistic

### R01
I enjoy working with physical tools or equipment.

### R02
I like building or assembling things.

### R03
I enjoy practical hands-on tasks.

### R04
I would enjoy working with machines or hardware.

### R05
I like solving problems by physically testing different solutions.

### R06
I enjoy outdoor or field-based activities.

### R07
I prefer doing something practical rather than only discussing it.

### R08
I enjoy understanding how physical systems work.

---

## I — Investigative

### I01
I enjoy solving difficult intellectual problems.

### I02
I like understanding why something happens.

### I03
I enjoy mathematics, science or logical reasoning.

### I04
I like investigating information before reaching a conclusion.

### I05
I enjoy experimenting with different hypotheses.

### I06
I like analyzing data to discover patterns.

### I07
I enjoy learning how complex systems work.

### I08
I prefer finding evidence before making decisions.

---

## A — Artistic

### A01
I enjoy creating visual designs.

### A02
I like expressing ideas through art or creative media.

### A03
I enjoy experimenting with colors, shapes and layouts.

### A04
I like creating original stories or concepts.

### A05
I prefer tasks where there can be multiple creative solutions.

### A06
I enjoy photography, video, animation or visual storytelling.

### A07
I like designing things that communicate a message.

### A08
I enjoy turning abstract ideas into creative outputs.

---

## S — Social

### S01
I enjoy helping people solve their problems.

### S02
I like teaching others something I understand.

### S03
I enjoy listening to people's concerns.

### S04
I like working closely with a team.

### S05
I enjoy explaining difficult ideas to others.

### S06
I would enjoy mentoring someone.

### S07
I like activities involving communication and cooperation.

### S08
I feel comfortable supporting someone who is struggling.

---

## E — Enterprising

### E01
I enjoy leading a team toward a goal.

### E02
I like persuading people using logical arguments.

### E03
I enjoy presenting ideas to an audience.

### E04
I would enjoy starting a business or project.

### E05
I like negotiating and reaching agreements.

### E06
I enjoy setting ambitious goals.

### E07
I like taking responsibility for important decisions.

### E08
I enjoy identifying opportunities and turning them into projects.

---

## C — Conventional

### C01
I enjoy organizing information systematically.

### C02
I like working with structured procedures.

### C03
I enjoy maintaining accurate records.

### C04
I prefer tasks with clear rules and expectations.

### C05
I like organizing schedules and resources.

### C06
I enjoy checking information for errors.

### C07
I like working with tables, lists or structured datasets.

### C08
I prefer having an organized workflow.

---

# 14. RIASEC Scoring

Calculate:

```text
R = average(R01...R08)
I = average(I01...I08)
A = average(A01...A08)
S = average(S01...S08)
E = average(E01...E08)
C = average(C01...C08)
```

Then identify the top 2–3 dimensions.

Example:

```text
I = 4.6
C = 4.2
A = 3.1
R = 2.8
S = 2.5
E = 2.2
```

Profile:

`I-C`

RIASEC should support career matching, but **must not be used alone to determine a student's career**.

---

# 15. Question Selection Algorithm

Use this conceptual algorithm:

```text
INPUT:
    assessment_mode
    major_field
    subfield (optional)
    target_question_count

LOAD:
    SkillSetu_Adaptive_Assessment_Framework.md

IF assessment_mode == "career_discovery":
    weights = major_field_6D_weights
    eligible_questions = questions matching major_field OR ALL

    calculate question_count_per_dimension(weights)

    FOR each dimension:
        filter questions by dimension
        filter by current difficulty
        remove previously asked questions
        select required number

    run RIASEC separately

ELSE IF assessment_mode == "gap_analysis":
    requirement_profile = selected_subfield_requirement_profile

    identify high-weight dimensions
    select questions matching selected subfield
    include relevant general questions
    include subfield-specific technical questions where available
    remove previously asked questions

AFTER each batch:
    calculate recent accuracy
    adapt difficulty

AFTER assessment:
    calculate 6D Skill Vector

IF career_discovery:
    calculate RIASEC
    compare 6D + RIASEC with career requirement profiles

IF gap_analysis:
    calculate current-vs-required gap
    rank development areas by gap magnitude
```

---

# 16. No-Repetition Rule

During one assessment:

```text
previously_asked_question_ids
```

must be maintained.

Before selecting a question:

```text
IF question_id IN previously_asked_question_ids:
    reject question
ELSE:
    allow selection
```

Questions may be reused in different students' assessments.

They should simply not repeat unnecessarily within the **same assessment session**.

---

# 17. Question Balance Rule

Even when one dimension has a high weight, do not completely eliminate other dimensions.

For example:

Engineering:

```text
TEC 25%
MAT 20%
ANA 20%
COG 15%
CRE 10%
SOF 10%
```

does **not** mean:

```text
SOF = 0 questions
CRE = 0 questions
```

The weights control relative emphasis.

---

# 18. Subfield-Specific Priority

For Gap Analysis, use this priority:

```text
Priority 1:
Subfield-specific technical/domain questions

Priority 2:
High-weight 6D dimensions for that subfield

Priority 3:
General 6D questions

Priority 4:
Supporting soft-skill/creativity questions
```

Example:

```text
Engineering
    ↓
AI & Machine Learning
    ↓
TEC + MAT + ANA + COG
    ↓
AI/ML-specific questions
    +
General 6D questions
```

For:

```text
Business
    ↓
Marketing
```

the system should emphasize:

```text
SOF + CRE + ANA + COG
```

and use marketing-specific questions where available.

---

# 19. Career Discovery Output

The output should contain:

### Student Profile

```text
6D Skill Vector
RIASEC Profile
Strongest dimensions
Development areas
```

### Career/Field Matching

Show several relevant career clusters rather than only one.

Each result should include:

```text
Career/Subfield
Match %
Why it matched
Strong dimensions
Relevant interests
Development areas
```

The explanation must be traceable to the student's measured profile.

---

# 20. Gap Analysis Output

Example:

```text
Desired Career: Data Science

Current vs Required

Dimension       Current    Required    Gap
------------------------------------------------
Cognitive         78         75        +3
Mathematical      61         80       -19
Analytical        76         85        -9
Creativity        64         60        +4
Technical         52         80       -28
Soft Skills       70         60       +10
```

Then:

```text
Priority Development Areas

1. Technical
   - Python
   - Data tools
   - Machine learning fundamentals

2. Mathematical
   - Statistics
   - Probability

3. Analytical
   - Data interpretation
   - Problem decomposition
```

---

# 21. Important Product Rules

1. **Do not give everyone the same assessment.**
2. **Do not randomly select questions without considering the student's field.**
3. **Do not use RIASEC as a measure of skill.**
4. **Do not use one question to determine a skill level.**
5. **Use multiple questions per dimension.**
6. **Adapt difficulty gradually.**
7. **Do not repeat a question within the same assessment.**
8. **Do not completely remove low-weight dimensions.**
9. **For Gap Analysis, prioritize the selected subfield.**
10. **Do not label students as unsuitable.**
11. **Explain why a result was generated.**
12. **Keep all field weights and question-selection parameters configurable.**
13. **New questions, fields and subfields should be addable without rewriting the assessment engine.**
14. **The framework file remains the source of truth for the overall field/subfield structure and requirement profiles.**
15. **This file is the source of truth for the prototype question bank and question-level selection metadata.**

---

# 22. Future Question Expansion

This question bank is a **prototype dataset**, not a complete psychometric assessment.

Before production use, expand each dimension/subfield with substantially more questions, including:

- Multiple equivalent questions measuring the same skill
- More difficulty levels
- More domain-specific questions
- Scenario-based questions
- Data interpretation questions
- Additional technical questions per subfield
- Validation questions
- Questions designed to reduce memorization effects

The engine should select from a larger pool rather than repeatedly exposing the same small set of questions.

---

# 23. File Dependency Contract

This file must be used **after**:

`SkillSetu_Adaptive_Assessment_Framework.md`

The dependency relationship is:

```text
SkillSetu_Adaptive_Assessment_Framework.md
                │
                ├── Assessment modes
                ├── Six skill dimensions
                ├── RIASEC model
                ├── Five major fields
                ├── Subfields
                ├── Major-field weights
                └── Subfield requirement profiles
                                │
                                ▼
SkillSetu_Adaptive_Assessment_Question_Bank.md
                │
                ├── Question bank
                ├── Question metadata
                ├── Difficulty
                ├── Selection rules
                ├── Adaptive rules
                └── RIASEC questions
                                │
                                ▼
                    Assessment Engine
                                │
                                ▼
                         Student Result
```

### Implementation instruction

When implementing the assessment feature, the system should:

1. Locate and read `SkillSetu_Adaptive_Assessment_Framework.md`.
2. Locate and read this file: `SkillSetu_Adaptive_Assessment_Question_Bank.md`.
3. Treat the framework as the structural/configuration source.
4. Treat this file as the question/selection source.
5. Never hard-code the entire question bank into the application if the application can load these definitions from the files.
6. Keep the assessment engine modular so the question bank can later be expanded or replaced.
7. If a question conflicts with the framework's current field/subfield configuration, follow the framework configuration and mark the question for review rather than silently creating a new category.

---

## Final Principle

> **Goal → Major Field → Subfield (if needed) → Requirement Profile → Weighted Question Selection → Adaptive Difficulty → 6D Skill Vector → RIASEC (Career Discovery) → Career Matching OR Skill-Gap Analysis → Explainable Development Direction.**
