
const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const TOKEN_KEY = "studyhub_access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}, authenticated = true) {
  const headers = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };

  if (authenticated) {
    const token = getToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    if (response.status === 401 && authenticated) {
      clearToken();
      window.dispatchEvent(new Event("studyhub:unauthorized"));
    }

    const detail = data.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : "Something went wrong";

    throw new Error(message);
  }

  return data;
}

// Authentication

export function registerUser(user) {
  return request(
    "/users",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(user),
    },
    false
  );
}

export function loginUser(email, password) {
  return request(
    "/auth/login",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    },
    false
  );
}

export function getCurrentUser() {
  return request("/users/me");
}

// Notes CRUD

export function getNotes() {
  return request("/notes");
}

export function createNote(note) {
  return request("/notes", {
    method: "POST",
    body: JSON.stringify(note),
  });
}

export function updateNote(id, note) {
  return request(`/notes/${id}`, {
    method: "PUT",
    body: JSON.stringify(note),
  });
}

export function deleteNote(id) {
  return request(`/notes/${id}`, {
    method: "DELETE",
  });
}
