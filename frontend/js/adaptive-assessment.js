/**
 * SkillSetu — Adaptive Assessment Framework Client Logic
 * Implements Path A (Career Discovery) & Path B (Gap Analysis)
 */

let adaptiveState = {
  path: "path_a",
  majorField: "engineering",
  subfield: "software_eng",
  fieldsData: null,
  questions: [],
  currentIndex: 0,
  answers: {},
  timer: null,
  timeRemaining: 0,
  latestResults: null
};

async function loadAdaptiveFields() {
  if (adaptiveState.fieldsData) return adaptiveState.fieldsData;
  try {
    let data;
    if (typeof api !== 'undefined' && api.get) {
      data = await api.get("/skills/adaptive/fields");
    } else {
      const res = await fetch("/api/skills/adaptive/fields");
      data = await res.json();
    }
    adaptiveState.fieldsData = data;
    return adaptiveState.fieldsData;
  } catch (err) {
    console.error("Error loading adaptive fields:", err);
    return null;
  }
}

async function openAdaptiveAssessmentModal(defaultPath = "path_a") {
  adaptiveState.path = defaultPath;
  adaptiveState.currentIndex = 0;
  adaptiveState.answers = {};

  const fields = await loadAdaptiveFields();

  // Reset steps safely
  const step1 = document.getElementById("adaptive-step-1");
  const step2 = document.getElementById("adaptive-step-2");
  const step3 = document.getElementById("adaptive-step-3");
  if (step1) step1.style.display = "block";
  if (step2) step2.style.display = "none";
  if (step3) step3.style.display = "none";

  selectAdaptivePath(defaultPath);
  
  const modal = document.getElementById("adaptive-assessment-modal");
  if (modal) {
    modal.classList.add("active");
  } else {
    console.warn("adaptive-assessment-modal element not found in DOM");
  }
}

function closeAdaptiveAssessmentModal() {
  if (adaptiveState.timer) clearInterval(adaptiveState.timer);
  const modal = document.getElementById("adaptive-assessment-modal");
  if (modal) {
    modal.classList.remove("active");
  }
}

function selectAdaptivePath(pathKey) {
  adaptiveState.path = pathKey;
  document.querySelectorAll(".path-choice-card").forEach(c => c.classList.remove("active"));
  
  const selectedCard = document.getElementById(`path-card-${pathKey}`);
  if (selectedCard) selectedCard.classList.add("active");

  const subfieldContainer = document.getElementById("adaptive-subfield-select-container");
  if (subfieldContainer) {
    subfieldContainer.style.display = (pathKey === "path_b") ? "block" : "none";
  }
  
  updateFieldSelectionUI();
}

function selectAdaptiveMajorField(fieldKey) {
  adaptiveState.majorField = fieldKey;
  document.querySelectorAll(".field-choice-card").forEach(c => c.classList.remove("active"));
  
  const card = document.getElementById(`field-card-${fieldKey}`);
  if (card) card.classList.add("active");

  updateSubfieldDropdown();
}

function updateFieldSelectionUI() {
  if (!adaptiveState.fieldsData) return;
  const grid = document.getElementById("adaptive-fields-grid");
  if (!grid) return;

  grid.innerHTML = Object.values(adaptiveState.fieldsData).map(f => `
    <div class="field-choice-card ${f.id === adaptiveState.majorField ? 'active' : ''}" 
         id="field-card-${f.id}" 
         onclick="selectAdaptiveMajorField('${f.id}')">
      <div style="font-size: 1.6rem; margin-bottom: 0.35rem;">${f.icon}</div>
      <div style="font-size: 0.85rem; font-weight: 600;">${f.name}</div>
    </div>
  `).join("");

  updateSubfieldDropdown();
}

function updateSubfieldDropdown() {
  if (!adaptiveState.fieldsData) return;
  const field = adaptiveState.fieldsData[adaptiveState.majorField];
  const select = document.getElementById("adaptive-subfield-select");
  if (!select || !field) return;

  select.innerHTML = field.subfields.map(sf => `
    <option value="${sf.id}">${sf.name}</option>
  `).join("");

  if (field.subfields.length > 0) {
    adaptiveState.subfield = field.subfields[0].id;
  }
}

function onSubfieldChange(val) {
  adaptiveState.subfield = val;
}

async function startAdaptiveQuestionnaire() {
  const subfieldSelect = document.getElementById("adaptive-subfield-select");
  if (subfieldSelect && adaptiveState.path === "path_b") {
    adaptiveState.subfield = subfieldSelect.value;
  }

  try {
    let data;
    const reqPayload = {
      path: adaptiveState.path,
      major_field: adaptiveState.majorField,
      subfield: adaptiveState.subfield
    };

    if (typeof api !== 'undefined' && api.post) {
      data = await api.post("/skills/adaptive/questionnaire", reqPayload);
    } else {
      const res = await fetch("/api/skills/adaptive/questionnaire", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reqPayload)
      });
      data = await res.json();
    }

    adaptiveState.questions = data.questions || [];
    adaptiveState.currentIndex = 0;
    adaptiveState.answers = {};
    adaptiveState.timeRemaining = adaptiveState.questions.length * 60;

    const step1 = document.getElementById("adaptive-step-1");
    const step2 = document.getElementById("adaptive-step-2");
    if (step1) step1.style.display = "none";
    if (step2) step2.style.display = "block";

    renderAdaptiveQuestion();
    startAdaptiveTimer();
  } catch (err) {
    if (typeof showToast === 'function') {
      showToast("Error starting adaptive questionnaire: " + err.message, "error");
    } else {
      alert("Error starting assessment: " + err.message);
    }
  }
}

function startAdaptiveTimer() {
  if (adaptiveState.timer) clearInterval(adaptiveState.timer);
  const display = document.getElementById("adaptive-timer-display");
  
  adaptiveState.timer = setInterval(() => {
    if (adaptiveState.timeRemaining <= 0) {
      clearInterval(adaptiveState.timer);
      if (typeof showToast === 'function') showToast("Time expired! Submitting assessment...", "warning");
      submitAdaptiveAssessment();
      return;
    }
    adaptiveState.timeRemaining--;
    const mins = Math.floor(adaptiveState.timeRemaining / 60);
    const secs = adaptiveState.timeRemaining % 60;
    if (display) {
      display.innerText = `⏱️ ${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
  }, 1000);
}

function renderAdaptiveQuestion() {
  const idx = adaptiveState.currentIndex;
  const total = adaptiveState.questions.length;
  if (total === 0) return;
  const q = adaptiveState.questions[idx];

  const counter = document.getElementById("adaptive-question-counter");
  if (counter) counter.innerText = `Question ${idx + 1} of ${total}`;

  const progress = document.getElementById("adaptive-progress-bar");
  if (progress) progress.style.width = `${((idx + 1) / total) * 100}%`;

  const container = document.getElementById("adaptive-question-container");
  if (!container) return;

  const currentAns = adaptiveState.answers[q.id];
  const badgeText = q.dimension ? `6D Dimension: ${q.dimension}` : `RIASEC Interest: Code ${q.riasec}`;

  container.innerHTML = `
    <div style="background: var(--surface); padding: 1.35rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
        <span class="badge badge-teal">${badgeText}</span>
        <span style="font-size: 0.8rem; color: var(--muted);">Step ${idx + 1}</span>
      </div>
      <p style="font-weight: 600; font-size: 1.05rem; margin-bottom: 1.25rem; color: var(--ink);">${q.question}</p>
      <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        ${q.options.map(opt => `
          <label style="display: flex; align-items: center; gap: 0.75rem; cursor: pointer; font-size: 0.95rem; padding: 0.75rem; border-radius: var(--radius-sm); border: 1px solid ${currentAns === opt.id ? 'var(--teal)' : 'var(--border)'}; background: ${currentAns === opt.id ? 'var(--teal-tint)' : 'var(--surface)'};">
            <input type="radio" name="adaptive_q_${q.id}" value="${opt.id}" onchange="saveAdaptiveAnswer(${q.id}, '${opt.id}')" ${currentAns === opt.id ? 'checked' : ''}>
            <span><strong>${opt.id})</strong> ${opt.text}</span>
          </label>
        `).join('')}
      </div>
    </div>
  `;

  // Nav buttons
  const prevBtn = document.getElementById("btn-adaptive-prev");
  const nextBtn = document.getElementById("btn-adaptive-next");
  const submitBtn = document.getElementById("btn-adaptive-submit");
  if (prevBtn) prevBtn.disabled = (idx === 0);

  if (idx === total - 1) {
    if (nextBtn) nextBtn.style.display = "none";
    if (submitBtn) submitBtn.style.display = "inline-block";
  } else {
    if (nextBtn) nextBtn.style.display = "inline-block";
    if (submitBtn) submitBtn.style.display = "none";
  }
}

function saveAdaptiveAnswer(qId, optionId) {
  adaptiveState.answers[qId] = optionId;
  renderAdaptiveQuestion();
}

function nextAdaptiveQuestion() {
  if (adaptiveState.currentIndex < adaptiveState.questions.length - 1) {
    adaptiveState.currentIndex++;
    renderAdaptiveQuestion();
  }
}

function prevAdaptiveQuestion() {
  if (adaptiveState.currentIndex > 0) {
    adaptiveState.currentIndex--;
    renderAdaptiveQuestion();
  }
}

async function submitAdaptiveAssessment() {
  if (adaptiveState.timer) clearInterval(adaptiveState.timer);

  const answerPayload = Object.keys(adaptiveState.answers).map(qId => ({
    question_id: parseInt(qId),
    selected_option: adaptiveState.answers[qId]
  }));

  if (answerPayload.length === 0) {
    if (typeof showToast === 'function') {
      showToast("Please answer at least one question before submitting.", "warning");
    } else {
      alert("Please answer at least one question before submitting.");
    }
    return;
  }

  try {
    let results;
    const reqPayload = {
      path: adaptiveState.path,
      major_field: adaptiveState.majorField,
      subfield: adaptiveState.subfield,
      answers: answerPayload
    };

    if (typeof api !== 'undefined' && api.post) {
      results = await api.post("/skills/adaptive/submit", reqPayload);
    } else {
      const res = await fetch("/api/skills/adaptive/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reqPayload)
      });
      results = await res.json();
    }

    adaptiveState.latestResults = results;
    localStorage.setItem("skillsetu_adaptive_latest_results", JSON.stringify(results));

    renderAdaptiveResults(results);

    const step2 = document.getElementById("adaptive-step-2");
    const step3 = document.getElementById("adaptive-step-3");
    if (step2) step2.style.display = "none";
    if (step3) step3.style.display = "block";

  } catch (err) {
    if (typeof showToast === 'function') {
      showToast("Error submitting adaptive assessment: " + err.message, "error");
    } else {
      alert("Error submitting assessment: " + err.message);
    }
  }
}

function renderAdaptiveResults(res) {
  const container = document.getElementById("adaptive-results-content");
  if (!container) return;

  const vec = res.student_vector || {};
  const riasec = res.student_riasec || {};

  const vectorBarsHtml = [
    { label: "Cognitive Reasoning (COG)", key: "COG", color: "#6366f1" },
    { label: "Mathematical Thinking (MAT)", key: "MAT", color: "#0ea5e9" },
    { label: "Analytical Problem Solving (ANA)", key: "ANA", color: "#14b8a6" },
    { label: "Creativity & Design (CRE)", key: "CRE", color: "#ec4899" },
    { label: "Technical Execution (TEC)", key: "TEC", color: "#10b981" },
    { label: "Soft Skills & Communication (SOF)", key: "SOF", color: "#f59e0b" }
  ].map(item => {
    const val = vec[item.key] || 70.0;
    return `
      <div class="vector-bar-container">
        <div class="vector-bar-label">
          <span>${item.label}</span>
          <span>${val}/100</span>
        </div>
        <div class="vector-bar-track">
          <div class="vector-bar-fill" style="width: ${val}%; background: ${item.color};"></div>
        </div>
      </div>
    `;
  }).join("");

  const riasecHtml = Object.keys(riasec).map(k => `
    <span class="riasec-chip"><strong>${k}:</strong> ${riasec[k]}</span>
  `).join(" ");

  let pathSpecificHtml = "";

  if (res.path === "path_a") {
    pathSpecificHtml = `
      <h4 style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 1rem; color: var(--ink);">🎯 Top Suitable Career Clusters</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; text-align: left;">
        ${(res.top_matches || []).map((match, idx) => `
          <div style="padding: 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-md);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
              <span style="font-weight: 700; color: var(--teal); font-size: 1rem;">${idx + 1}. ${match.title}</span>
              <span class="badge badge-teal">${match.match_percentage}% Match</span>
            </div>
            <p style="font-size: 0.8rem; color: var(--muted); margin-bottom: 0.5rem;">Field: ${match.field_name}</p>
            <div style="font-size: 0.82rem; margin-bottom: 0.5rem;">
              <strong>Typical Roles:</strong> ${match.typical_roles.join(', ')}
            </div>
            <div style="font-size: 0.8rem; color: var(--ink);">
              <strong>Match Reasons:</strong>
              <ul style="margin-top: 0.25rem; padding-left: 1.25rem;">
                ${match.reasons.map(r => `<li>${r}</li>`).join('')}
              </ul>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } else {
    pathSpecificHtml = `
      <h4 style="font-size: 1.1rem; margin-top: 1.5rem; margin-bottom: 1rem; color: var(--ink);">📊 Skill Gap Analysis vs ${res.target_subfield}</h4>
      <div class="data-table-container" style="margin-bottom: 1.25rem;">
        <table class="data-table">
          <thead>
            <tr>
              <th>Dimension</th>
              <th>Current</th>
              <th>Required</th>
              <th>Gap</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${(res.gap_table || []).map(row => `
              <tr>
                <td><strong>${row.dimension_name}</strong></td>
                <td>${row.current}</td>
                <td>${row.required}</td>
                <td style="color: ${row.gap > 0 ? '#ef4444' : '#10b981'}; font-weight: 600;">${row.gap > 0 ? '-' + row.gap : 'Met'}</td>
                <td><span class="badge badge-${row.status_color}">${row.status}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div style="text-align: left; background: var(--surface); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
        <h5 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--teal);">🚀 Prioritized Development Roadmap</h5>
        <ol style="padding-left: 1.25rem; font-size: 0.9rem; color: var(--ink);">
          ${(res.roadmap || []).map(step => `<li style="margin-bottom: 0.35rem;">${step}</li>`).join('')}
        </ol>
      </div>
    `;
  }

  container.innerHTML = `
    <div style="text-align: center; margin-bottom: 1.5rem;">
      <div style="font-size: 2.2rem; margin-bottom: 0.25rem;">⚡</div>
      <h3 style="font-size: 1.35rem; color: var(--ink);">${res.path_name} Report</h3>
      <p style="font-size: 0.85rem; color: var(--muted);">Major Field: ${res.major_field}</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; text-align: left;">
      <div style="background: var(--surface); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
        <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 1rem; color: var(--teal);">6D Skill Vector Profile</h4>
        ${vectorBarsHtml}
      </div>
      <div style="background: var(--surface); padding: 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
        <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 1rem; color: var(--teal);">RIASEC Interest Dimensions</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
          ${riasecHtml}
        </div>
        <p style="font-size: 0.82rem; color: var(--muted);">
          RIASEC codes represent occupational interests (Realistic, Investigative, Artistic, Social, Enterprising, Conventional) aligned with work environments.
        </p>
      </div>
    </div>

    ${pathSpecificHtml}
  `;
}

function redirectToSkillEngine() {
  closeAdaptiveAssessmentModal();
  
  // If user is on student dashboard, switch section cleanly
  if (typeof switchSection === 'function') {
    const linkEl = document.querySelector('.sidebar-link:nth-child(2)');
    if (linkEl) switchSection('skills-section', linkEl);
  } else {
    // Navigate from home page to student dashboard with skill section active
    window.location.href = "/dashboards/student.html#skills-section";
  }
}
