/**
 * SkillSetu Central API Client
 * Manages JWT tokens, automatic Authorization headers, token refreshing, and unified error handling.
 */
const API_BASE = "/api";

const api = {
  getToken: () => localStorage.getItem("skillsetu_access_token"),
  getRefreshToken: () => localStorage.getItem("skillsetu_refresh_token"),
  getUser: () => {
    try {
      return JSON.parse(localStorage.getItem("skillsetu_user"));
    } catch (e) {
      return null;
    }
  },
  
  setAuth: (tokenData) => {
    if (tokenData.access_token) {
      localStorage.setItem("skillsetu_access_token", tokenData.access_token);
    }
    if (tokenData.refresh_token) {
      localStorage.setItem("skillsetu_refresh_token", tokenData.refresh_token);
    }
    const user = {
      id: tokenData.user_id,
      email: tokenData.email,
      full_name: tokenData.full_name,
      role: tokenData.role
    };
    localStorage.setItem("skillsetu_user", JSON.stringify(user));
  },

  clearAuth: () => {
    localStorage.removeItem("skillsetu_access_token");
    localStorage.removeItem("skillsetu_refresh_token");
    localStorage.removeItem("skillsetu_user");
  },

  isAuthenticated: () => !!localStorage.getItem("skillsetu_access_token"),

  logout: () => {
    api.clearAuth();
    window.location.href = "/";
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;
    const headers = options.headers || {};

    const token = api.getToken();
    if (token && !headers["Authorization"]) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    options.headers = headers;

    let response = await fetch(url, options);

    // If 401 Unauthorized, attempt refresh
    if (response.status === 401 && api.getRefreshToken()) {
      const refreshed = await api.tryRefreshToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${api.getToken()}`;
        response = await fetch(url, options);
      } else {
        api.logout();
        throw new Error("Session expired. Please log in again.");
      }
    }

    if (!response.ok) {
      let errDetail = "Request failed";
      try {
        const errJson = await response.json();
        errDetail = errJson.detail || JSON.stringify(errJson);
      } catch (e) {
        errDetail = response.statusText;
      }
      throw new Error(errDetail);
    }

    return response.json();
  },

  async tryRefreshToken() {
    const refreshToken = api.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("skillsetu_access_token", data.access_token);
        return true;
      }
    } catch (e) {
      console.error("Token refresh failed:", e);
    }
    return false;
  },

  get: (endpoint) => api.request(endpoint, { method: "GET" }),
  
  post: (endpoint, body) => api.request(endpoint, {
    method: "POST",
    body: body instanceof FormData ? body : JSON.stringify(body)
  }),

  put: (endpoint, body) => api.request(endpoint, {
    method: "PUT",
    body: body instanceof FormData ? body : JSON.stringify(body)
  }),

  upload: (endpoint, formData) => api.request(endpoint, {
    method: "POST",
    body: formData
  })
};
