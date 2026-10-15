
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Something went wrong");
  }

  return response.json();
}

// GET: Fetch all notes
export function getNotes() {
  return request(`${API_URL}/notes`);
}

// POST: Create a new note
export function createNote(note) {
  return request(`${API_URL}/notes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(note),
  });
}

// PUT: Update an existing note
export function updateNote(id, note) {
  return request(`${API_URL}/notes/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(note),
  });
}

// DELETE: Delete a note
export function deleteNote(id) {
  return request(`${API_URL}/notes/${id}`, {
    method: "DELETE",
  });
}
