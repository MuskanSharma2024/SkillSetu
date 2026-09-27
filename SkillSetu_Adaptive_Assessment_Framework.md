# SkillSetu – Adaptive Career Assessment Framework

## 1. Purpose

SkillSetu will use an **adaptive two-path assessment system** rather than giving every student the same quiz.

The student first chooses what they need help with:

### Path A — Career Discovery
> **“I don't know which career path suits me.”**

The system:
1. Asks the student to select a broad major field.
2. Builds an assessment using the **6D Skill Vector + RIASEC interests**.
3. Gives greater weight to the dimensions that are more relevant to that field.
4. Calculates the student's strengths and interest profile.
5. Matches the profile against career/subfield requirements.
6. Recommends suitable career clusters and explains the reasons.

### Path B — Desired Career Gap Analysis
> **“I already know what career I want and want to know what I am missing.”**

The system:
1. Asks the student to select a major field.
2. Asks for a specific subfield/career.
3. Loads the requirement profile for that subfield.
4. Generates a **career-specific assessment** focused on the skills needed for that path.
5. Measures the student's current level.
6. Compares current skills with required skills.
7. Identifies gaps and prioritizes them.
8. Generates a development direction/roadmap.

The two paths therefore answer different questions:

| Path | Main Question | Main Output |
|---|---|---|
| Career Discovery | “What could suit me?” | Career-cluster recommendations |
| Gap Analysis | “How ready am I for what I want?” | Skill-gap report + development priorities |

---

# 2. Assessment Model

## 2.1 Six-Dimensional Skill Vector

Every student receives a normalized 0–100 score for:

1. **Cognitive (COG)** – logical reasoning, comprehension, pattern recognition, learning ability
2. **Mathematical (MAT)** – numerical reasoning, quantitative thinking, statistics and mathematical problem solving
3. **Analytical (ANA)** – data interpretation, problem decomposition, evidence-based reasoning and decision making
4. **Creativity (CRE)** – idea generation, design thinking, originality and alternative solution generation
5. **Technical (TEC)** – programming, tools, systems, technical concepts and practical technical ability
6. **Soft Skills (SOF)** – communication, teamwork, leadership, adaptability, organization and interpersonal ability

Output format:

`6D Skill Vector = [COG, MAT, ANA, CRE, TEC, SOF]`

All dimensions are normalized to 0–100.

---

## 2.2 RIASEC Interest Profile

The system also measures six occupational-interest dimensions:

- **R – Realistic:** practical, hands-on, tools, machines, physical systems
- **I – Investigative:** research, science, mathematics, analysis, problem solving
- **A – Artistic:** creativity, design, visual expression, originality
- **S – Social:** teaching, helping, mentoring, collaboration
- **E – Enterprising:** leadership, persuasion, business, decision making
- **C – Conventional:** organization, structured information, accuracy, procedures

Output:

`RIASEC Profile = [R, I, A, S, E, C]`

The RIASEC profile represents **interest**, not skill.

---

# 3. Assessment Logic

## Path A – Career Discovery

### Step A1 – Goal Selection
Student selects:

**Discover a suitable career path**

### Step A2 – Major Field Selection
Student chooses one of the five available major fields.

### Step A3 – Adaptive Assessment
The assessment gives more questions to the relevant dimensions.

Example:

A student selecting **Engineering & Technology** receives relatively more Technical, Analytical and Mathematical questions.

A student selecting **Business & Management** receives relatively more Soft Skills, Analytical, Cognitive and Creative/decision-making questions.

### Step A4 – RIASEC Assessment
RIASEC questions are asked separately because interests should not be treated as technical skill.

### Step A5 – Matching
The system compares:

**Student 6D Vector + Student RIASEC Profile**
against
**Field/Subfield Requirement Profile**

### Step A6 – Output
The system returns:
- Top suitable career clusters
- Match percentage
- Strongest dimensions
- Relevant RIASEC interests
- Areas requiring development
- Explainable reasons for each recommendation

---

# 4. Path B – Desired Career Gap Analysis

### Step B1 – Goal Selection
Student selects:

**Analyze my gaps for a desired career**

### Step B2 – Major Field
Student selects a major field.

### Step B3 – Subfield
Student selects a specific subfield.

### Step B4 – Personalized Quiz
The system loads the requirement profile of that subfield.

Questions are selected according to the skills that matter most for that career.

### Step B5 – Gap Calculation

For each relevant skill:

`Gap = Required Level – Current Level`

The system should distinguish:

- **Strong:** current level meets/exceeds requirement
- **Moderate Gap:** small development needed
- **High Gap:** substantial development needed
- **Critical Gap:** major prerequisite is missing

### Step B6 – Output

Example:

**Desired Career: Data Science**

- Analytical: 82/100 → Strong
- Mathematical: 68/100 → Moderate Gap
- Technical: 54/100 → High Gap
- Soft Skills: 71/100 → Strong

**Priority Development Areas**
1. Technical – Python/Data tools
2. Mathematical – Statistics
3. Technical – Machine Learning fundamentals

The system should not say that a student is “unsuitable”. It should identify the **current profile and development gaps**.

---

# 5. Major Fields and Subfields

For the first version, SkillSetu will support five major fields.

## FIELD 1 – Engineering & Technology

### Subfields
1. Software Engineering
2. Artificial Intelligence & Machine Learning
3. Data Science & Analytics
4. Cybersecurity
5. Electronics & Embedded Systems

### Typical career directions
Software Developer, AI/ML Engineer, Data Scientist, Data Analyst, Cybersecurity Analyst, Embedded Engineer, Systems Engineer.

---

## FIELD 2 – Business, Management & Finance

### Subfields
1. Business Management
2. Marketing & Digital Marketing
3. Finance & Investment
4. Business/Data Analytics
5. Entrepreneurship

### Typical career directions
Business Analyst, Marketing Specialist, Financial Analyst, Product/Business Manager, Entrepreneur, Operations Manager.

---

## FIELD 3 – Science & Research

### Subfields
1. Mathematics & Statistics
2. Physics
3. Chemistry
4. Life Sciences & Biotechnology
5. Scientific/Data Research

### Typical career directions
Researcher, Statistician, Scientist, Data Researcher, Biostatistics/Research Professional, Laboratory/Research roles.

---

## FIELD 4 – Design & Creative Arts

### Subfields
1. UI/UX & Product Design
2. Graphic & Visual Design
3. Fashion & Textile Design
4. Animation & Digital Media
5. Content & Creative Media

### Typical career directions
UI/UX Designer, Product Designer, Graphic Designer, Fashion Designer, Animator, Visual/Content Designer.

---

## FIELD 5 – Social, Education & Communication

### Subfields
1. Education & Teaching
2. Psychology & Counselling
3. Human Resources
4. Media & Communication
5. Social/Community Development

### Typical career directions
Teacher, Trainer, Counsellor, HR Professional, Communication Specialist, Community/Development Professional.

---

# 6. Major-Field Weightage – Career Discovery

The following weights represent the **relative importance of the six dimensions** when adapting the Career Discovery assessment.

> These are initial product-design weights. They should be treated as configurable parameters and refined after testing the assessment with real users and domain/reference data.

## 6.1 Engineering & Technology

| Dimension | Weight |
|---|---:|
| Cognitive | 15% |
| Mathematical | 20% |
| Analytical | 20% |
| Creativity | 10% |
| Technical | 25% |
| Soft Skills | 10% |
| **Total** | **100%** |

RIASEC emphasis: **I, R, C**, with A/E/S varying by subfield.

---

## 6.2 Business, Management & Finance

| Dimension | Weight |
|---|---:|
| Cognitive | 15% |
| Mathematical | 10% |
| Analytical | 15% |
| Creativity | 15% |
| Technical | 10% |
| Soft Skills | 35% |
| **Total** | **100%** |

RIASEC emphasis: **E, S, C**, with I/A varying by subfield.

---

## 6.3 Science & Research

| Dimension | Weight |
|---|---:|
| Cognitive | 20% |
| Mathematical | 20% |
| Analytical | 25% |
| Creativity | 10% |
| Technical | 15% |
| Soft Skills | 10% |
| **Total** | **100%** |

RIASEC emphasis: **I, C, R**.

---

## 6.4 Design & Creative Arts

| Dimension | Weight |
|---|---:|
| Cognitive | 10% |
| Mathematical | 5% |
| Analytical | 10% |
| Creativity | 40% |
| Technical | 15% |
| Soft Skills | 20% |
| **Total** | **100%** |

RIASEC emphasis: **A**, with S/E/C varying by subfield.

---

## 6.5 Social, Education & Communication

| Dimension | Weight |
|---|---:|
| Cognitive | 15% |
| Mathematical | 5% |
| Analytical | 10% |
| Creativity | 15% |
| Technical | 5% |
| Soft Skills | 50% |
| **Total** | **100%** |

RIASEC emphasis: **S, E, A**, with C/I varying by subfield.

---

# 7. Subfield Requirement Profiles – Gap Analysis

For Gap Analysis, the system should use the selected subfield rather than only the broad major field.

The following are **initial requirement profiles** for the prototype.

## Engineering & Technology

| Subfield | COG | MAT | ANA | CRE | TEC | SOF |
|---|---:|---:|---:|---:|---:|---:|
| Software Engineering | 15 | 15 | 20 | 10 | 30 | 10 |
| AI & Machine Learning | 15 | 25 | 25 | 10 | 20 | 5 |
| Data Science & Analytics | 15 | 25 | 25 | 10 | 20 | 10 |
| Cybersecurity | 15 | 15 | 25 | 5 | 30 | 5 |
| Electronics & Embedded | 15 | 20 | 20 | 10 | 30 | 5 |

## Business, Management & Finance

| Subfield | COG | MAT | ANA | CRE | TEC | SOF |
|---|---:|---:|---:|---:|---:|---:|
| Business Management | 15 | 10 | 15 | 15 | 5 | 40 |
| Marketing | 10 | 5 | 10 | 25 | 5 | 45 |
| Finance & Investment | 15 | 25 | 25 | 5 | 10 | 10 |
| Business/Data Analytics | 15 | 20 | 25 | 10 | 20 | 5 |
| Entrepreneurship | 15 | 10 | 15 | 20 | 5 | 35 |

## Science & Research

| Subfield | COG | MAT | ANA | CRE | TEC | SOF |
|---|---:|---:|---:|---:|---:|---:|
| Mathematics & Statistics | 25 | 35 | 25 | 5 | 5 | 5 |
| Physics | 20 | 30 | 25 | 10 | 10 | 5 |
| Chemistry | 20 | 20 | 25 | 10 | 20 | 5 |
| Life Sciences & Biotechnology | 20 | 15 | 25 | 10 | 25 | 5 |
| Scientific/Data Research | 20 | 25 | 30 | 10 | 10 | 5 |

## Design & Creative Arts

| Subfield | COG | MAT | ANA | CRE | TEC | SOF |
|---|---:|---:|---:|---:|---:|---:|
| UI/UX & Product Design | 10 | 5 | 15 | 35 | 15 | 20 |
| Graphic & Visual Design | 10 | 5 | 10 | 45 | 10 | 20 |
| Fashion & Textile Design | 10 | 5 | 10 | 45 | 15 | 15 |
| Animation & Digital Media | 10 | 5 | 10 | 40 | 20 | 15 |
| Content & Creative Media | 10 | 5 | 10 | 40 | 10 | 25 |

## Social, Education & Communication

| Subfield | COG | MAT | ANA | CRE | TEC | SOF |
|---|---:|---:|---:|---:|---:|---:|
| Education & Teaching | 15 | 5 | 10 | 15 | 5 | 50 |
| Psychology & Counselling | 20 | 5 | 15 | 15 | 5 | 50 |
| Human Resources | 15 | 5 | 15 | 10 | 5 | 50 |
| Media & Communication | 10 | 5 | 10 | 25 | 5 | 45 |
| Social/Community Development | 15 | 5 | 15 | 15 | 5 | 45 |

---

# 8. RIASEC Subfield Interest Profiles

RIASEC should be used primarily to measure **interest alignment**, not competence.

Initial dominant-interest mappings:

| Subfield | Primary RIASEC | Secondary RIASEC |
|---|---|---|
| Software Engineering | I | C |
| AI & Machine Learning | I | R/C |
| Data Science & Analytics | I | C |
| Cybersecurity | I | R/C |
| Electronics & Embedded | R/I | C |
| Business Management | E | S/C |
| Marketing | E | A/S |
| Finance & Investment | C/E | I |
| Business/Data Analytics | I/C | E |
| Entrepreneurship | E | A/S |
| Mathematics & Statistics | I | C |
| Physics | I | R |
| Chemistry | I | R |
| Life Sciences & Biotechnology | I | R |
| Scientific/Data Research | I | C |
| UI/UX & Product Design | A | I/S |
| Graphic & Visual Design | A | C |
| Fashion & Textile Design | A | R/E |
| Animation & Digital Media | A | I |
| Content & Creative Media | A | E/S |
| Education & Teaching | S | A |
| Psychology & Counselling | S | I |
| Human Resources | S/E | C |
| Media & Communication | A/E | S |
| Social/Community Development | S | E/A |

---

# 9. Question Selection Strategy

The system should NOT simply give every user all questions.

### Career Discovery
Select questions according to the chosen major field's 6D weights.

Example:

**Engineering**
- More Technical questions
- More Analytical questions
- More Mathematical questions
- Moderate Cognitive questions
- Fewer Soft-Skill questions

**Design**
- More Creativity questions
- Moderate Technical and Soft-Skill questions
- Fewer Mathematical questions

**Management**
- More Soft-Skill questions
- Moderate Analytical/Cognitive/Creativity questions
- Lower Technical emphasis

### Gap Analysis
Select questions according to the selected subfield.

Example:

`Engineering → AI/ML`

The assessment should prioritize:
- Mathematical reasoning
- Analytical reasoning
- Technical/AI concepts
- Cognitive problem solving

while still measuring the remaining dimensions where relevant.

---

# 10. Important Design Rule

**Weightage determines importance; it should not mean that other dimensions are ignored.**

For example, Software Engineering should not completely ignore communication and teamwork.

Similarly, Management should not completely ignore analytical or quantitative ability.

The weights should therefore change the **number, difficulty and contribution of questions**, rather than completely removing dimensions.

---

# 11. Recommended Assessment Output

After assessment, SkillSetu should display:

### Career Discovery

**Your Profile**
- 6D Skill Vector
- RIASEC Profile
- Strongest dimensions
- Development areas

**Potential Career Clusters**
1. Career Cluster A — Match: XX%
2. Career Cluster B — Match: XX%
3. Career Cluster C — Match: XX%

**Why?**
- Strong analytical ability
- High Investigative interest
- Strong mathematical profile
- Moderate technical readiness

### Desired Career Gap Analysis

**Selected Career:** Data Science

**Current vs Required**

| Skill Dimension | Current | Required | Gap |
|---|---:|---:|---:|
| Cognitive | 78 | 75 | +3 |
| Mathematical | 61 | 80 | -19 |
| Analytical | 76 | 85 | -9 |
| Creativity | 64 | 60 | +4 |
| Technical | 52 | 80 | -28 |
| Soft Skills | 70 | 60 | +10 |

**Priority Gaps**
1. Technical
2. Mathematical
3. Analytical

**Suggested Development Direction**
- Strengthen Python/data tools
- Improve statistics fundamentals
- Practice analytical/data problems
- Build 1–2 relevant projects
- Reassess after development

---

# 12. Future Expansion

This first version intentionally contains only five major fields and 25 subfields.

Later versions can add:
- Healthcare & Medicine
- Law & Public Policy
- Architecture & Planning
- Agriculture & Environmental Sciences
- Hospitality & Tourism
- Skilled Trades
- Sports & Fitness
- Quantitative Finance
- Quantum Computing
- Operations Research
- Other emerging career clusters

The assessment engine should be designed so that **new fields can be added by creating a new requirement profile rather than rewriting the entire assessment system.**

---

## Core Principle

> **SkillSetu should not give the same assessment to everyone. It should first understand the student's goal, then select the relevant assessment, weight the relevant dimensions, compare the result with career requirements, and provide an explainable career direction or skill-gap report.**
