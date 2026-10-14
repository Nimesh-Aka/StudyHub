
const API_URL = "http://127.0.0.1:8000";

export async function getNotes() {
  const response = await fetch(`${API_URL}/notes`);

  if (!response.ok) {
    throw new Error("Failed to fetch notes");
  }

  return response.json();
}
