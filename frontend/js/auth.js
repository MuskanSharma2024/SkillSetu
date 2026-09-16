/**
 * SkillSetu Auth Handlers
 * Modal control, tab toggling, role field switching, and demo one-click logins.
 */

let currentAuthTab = "login";
let currentRegisterRole = "student";
let loadedInstitutions = [];

async function loadInstitutionsDropdown() {
  try {
    loadedInstitutions = await api.get("/institutions");
    const stuSelect = document.getElementById("reg-student-inst");
    const acadSelect = document.getElementById("reg-acad-inst");

    const optionsHtml = `<option value="">-- Select Affiliated Institution --</option>` +
      loadedInstitutions.map(i => `<option value="${i.id}">${i.name} (${i.code})</option>`).join("");

    if (stuSelect) stuSelect.innerHTML = optionsHtml;
    if (acadSelect) acadSelect.innerHTML = optionsHtml;
  } catch (e) {
    console.error("Failed to load institutions:", e);
  }
}

function openAuthModal(tab = "login") {
  const modal = document.getElementById("auth-modal");
  if (!modal) return;
  modal.classList.add("active");
  switchAuthTab(tab);
  if (loadedInstitutions.length === 0) {
    loadInstitutionsDropdown();
  }
}

function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.classList.remove("active");
}

function switchAuthTab(tab) {
  currentAuthTab = tab;
  document.querySelectorAll(".auth-tab").forEach(el => {
    el.classList.toggle("active", el.dataset.tab === tab);
  });

  const loginSection = document.getElementById("auth-login-section");
  const registerSection = document.getElementById("auth-register-section");

  if (loginSection && registerSection) {
    loginSection.style.display = tab === "login" ? "block" : "none";
    registerSection.style.display = tab === "register" ? "block" : "none";
  }
}

function selectRegisterRole(role) {
  currentRegisterRole = role;
  document.querySelectorAll(".role-pill").forEach(el => {
    el.classList.toggle("active", el.dataset.role === role);
  });

  // Hide all role-specific field blocks
  document.querySelectorAll(".role-fields").forEach(el => {
    el.style.display = "none";
  });

  // Show selected role fields
  const activeFields = document.getElementById(`fields-${role}`);
  if (activeFields) {
    activeFields.style.display = "block";
  }
}

// Handle Login Form Submit
async function handleLoginSubmit(event) {
  event.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  const submitBtn = event.target.querySelector("button[type='submit']");

  try {
    submitBtn.disabled = true;
    submitBtn.innerText = "Signing in...";

    const res = await api.post("/auth/login", { email, password });
    api.setAuth(res);
    showToast(`Welcome back, ${res.full_name}!`, "success");
    closeAuthModal();

    setTimeout(() => {
      window.location.href = getRoleDashboardUrl(res.role);
    }, 600);
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = "Sign In";
  }
}

// Handle Register Form Submit
async function handleRegisterSubmit(event) {
  event.preventDefault();
  const fullName = document.getElementById("reg-name").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  const submitBtn = event.target.querySelector("button[type='submit']");

  const payload = {
    email,
    password,
    full_name: fullName,
    role: currentRegisterRole
  };

  // Add role-specific details
  if (currentRegisterRole === "student") {
    const instVal = document.getElementById("reg-student-inst").value;
    if (instVal) payload.institution_id = parseInt(instVal);
    payload.enrollment_no = document.getElementById("reg-student-enroll").value.trim();
    payload.degree = document.getElementById("reg-student-degree").value.trim();
    payload.branch = document.getElementById("reg-student-branch").value.trim();
  } else if (currentRegisterRole === "industry") {
    payload.company_name = document.getElementById("reg-ind-company").value.trim();
    payload.industry_sector = document.getElementById("reg-ind-sector").value;
    payload.location = document.getElementById("reg-ind-location").value.trim();
  } else if (currentRegisterRole === "academician") {
    const instVal = document.getElementById("reg-acad-inst").value;
    if (instVal) payload.institution_id = parseInt(instVal);
    payload.department = document.getElementById("reg-acad-dept").value.trim();
    payload.designation = document.getElementById("reg-acad-desig").value.trim();
  } else if (currentRegisterRole === "institution_admin") {
    payload.institution_name = document.getElementById("reg-admin-inst-name").value.trim();
    payload.institution_code = document.getElementById("reg-admin-inst-code").value.trim();
  }

  try {
    submitBtn.disabled = true;
    submitBtn.innerText = "Creating Account...";

    const res = await api.post("/auth/register", payload);
    api.setAuth(res);
    showToast(`Account successfully created for ${res.full_name}!`, "success");
    closeAuthModal();

    setTimeout(() => {
      window.location.href = getRoleDashboardUrl(res.role);
    }, 600);
  } catch (err) {
    showToast(err.message, "error");
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = "Create Account";
  }
}

// Quick Demo Login for Evaluators
async function quickDemoLogin(role) {
  const demoAccounts = {
    student: { email: "student@skillsetu.edu", pass: "Password123!" },
    industry: { email: "industry@techcorp.com", pass: "Password123!" },
    academician: { email: "prof@dtu.ac.in", pass: "Password123!" },
    institution_admin: { email: "admin@nit.ac.in", pass: "Password123!" }
  };

  const account = demoAccounts[role];
  if (!account) return;

  try {
    showToast(`Logging in as Demo ${role.replace('_', ' ').toUpperCase()}...`, "info");
    const res = await api.post("/auth/login", {
      email: account.email,
      password: account.pass
    });
    api.setAuth(res);
    showToast(`Logged in as ${res.full_name} (${res.role})!`, "success");
    closeAuthModal();

    setTimeout(() => {
      window.location.href = getRoleDashboardUrl(res.role);
    }, 500);
  } catch (err) {
    showToast("Demo login failed: " + err.message, "error");
  }
}
