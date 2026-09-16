/**
 * Global App Helpers, Notifications, and Client-side Route Guarding
 */

function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  
  const icon = type === "success" ? "✓" : type === "error" ? "✕" : "ℹ";
  toast.innerHTML = `<span style="font-weight: bold;">${icon}</span><span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function getRoleDashboardUrl(role) {
  switch (role) {
    case "student": return "/dashboards/student.html";
    case "industry": return "/dashboards/industry.html";
    case "academician": return "/dashboards/academician.html";
    case "institution_admin": return "/dashboards/institution.html";
    default: return "/";
  }
}

function updateNavbarUser() {
  const user = api.getUser();
  const navContainer = document.getElementById("nav-auth-section");
  if (!navContainer) return;

  if (user && api.isAuthenticated()) {
    const roleColors = {
      student: "badge-primary",
      industry: "badge-cyan",
      academician: "badge-purple",
      institution_admin: "badge-amber"
    };

    const roleClass = roleColors[user.role] || "badge-primary";
    const dashUrl = getRoleDashboardUrl(user.role);

    navContainer.innerHTML = `
      <div class="user-nav-badge">
        <span class="badge ${roleClass}">${user.role.replace('_', ' ').toUpperCase()}</span>
        <span style="font-weight: 600; font-size: 0.9rem;">${user.full_name}</span>
      </div>
      <a href="${dashUrl}" class="btn btn-secondary btn-sm">Dashboard</a>
      <button onclick="api.logout()" class="btn btn-danger btn-sm">Logout</button>
    `;
  } else {
    navContainer.innerHTML = `
      <button onclick="openAuthModal('login')" class="btn btn-secondary btn-sm">Sign In</button>
      <button onclick="openAuthModal('register')" class="btn btn-primary btn-sm">Get Started</button>
    `;
  }
}

function enforceRole(allowedRoles = []) {
  if (!api.isAuthenticated()) {
    showToast("Please sign in to access this dashboard", "error");
    window.location.href = "/";
    return;
  }

  const user = api.getUser();
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    showToast(`Access restricted for role '${user.role}'. Redirecting to your dashboard...`, "error");
    setTimeout(() => {
      window.location.href = getRoleDashboardUrl(user.role);
    }, 1200);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updateNavbarUser();
});
