
import { useEffect, useRef, useState } from "react";
import {
  getNotes,
  createNote,
  updateNote,
  deleteNote,
  getToken,
  clearToken,
  getCurrentUser,
} from "./api";
import Auth from "./Auth";
import "./App.css";

function getTodayDate() {
  const today = new Date();
  const localDate = new Date(
    today.getTime() - today.getTimezoneOffset() * 60000
  );

  return localDate.toISOString().slice(0, 10);
}

function App() {
  // Authentication state
  const [token, setToken] = useState(() => getToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [authChecking, setAuthChecking] = useState(true);

  // Notes state
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState(getTodayDate());

  const dateInputRef = useRef(null);

  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Check whether the stored token is still valid.
  useEffect(() => {
    let active = true;

    async function checkAuthentication() {
      if (!getToken()) {
        if (active) {
          setAuthChecking(false);
          setLoading(false);
        }
        return;
      }

      try {
        const user = await getCurrentUser();

        if (active) {
          setCurrentUser(user);
          setToken(getToken());
        }
      } catch {
        clearToken();

        if (active) {
          setToken(null);
          setCurrentUser(null);
          setNotes([]);
        }
      } finally {
        if (active) {
          setAuthChecking(false);
        }
      }
    }

    checkAuthentication();

    return () => {
      active = false;
    };
  }, []);

  // Load notes after authentication succeeds.
  useEffect(() => {
    if (!token || !currentUser) return;

    loadNotes();
  }, [token, currentUser]);

  // Handle expired or invalid JWTs.
  useEffect(() => {
    function handleUnauthorized() {
      clearToken();
      setToken(null);
      setCurrentUser(null);
      setNotes([]);
      setEditingId(null);
      setError("Your session has expired. Please sign in again.");
    }

    window.addEventListener(
      "studyhub:unauthorized",
      handleUnauthorized
    );

    return () => {
      window.removeEventListener(
        "studyhub:unauthorized",
        handleUnauthorized
      );
    };
  }, []);

  async function loadNotes() {
    try {
      setError("");
      const data = await getNotes();
      setNotes(data);
    } catch (err) {
      setError(err.message || "Unable to load notes.");
    } finally {
      setLoading(false);
    }
  }

  function handleLogin() {
    const storedToken = getToken();

    if (!storedToken) {
      setToken(null);
      setCurrentUser(null);
      return;
    }

    setAuthChecking(true);

    getCurrentUser()
      .then((user) => {
        setCurrentUser(user);
        setToken(storedToken);
        setError("");
      })
      .catch(() => {
        clearToken();
        setToken(null);
        setCurrentUser(null);
        setError("Unable to verify your session. Please sign in again.");
      })
      .finally(() => {
        setAuthChecking(false);
      });
  }

  function handleLogout() {
    clearToken();
    setToken(null);
    setCurrentUser(null);
    setNotes([]);
    setLoading(true);
    resetForm();
  }

  function resetForm() {
    setTitle("");
    setDescription("");
    setDate(getTodayDate());
    setEditingId(null);
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!title.trim() || !description.trim() || !date) {
      setError("Please fill in all fields.");
      return;
    }

    const note = {
      title: title.trim(),
      description: description.trim(),
      date,
    };

    try {
      setSaving(true);
      setError("");

      if (editingId !== null) {
        await updateNote(editingId, note);
      } else {
        await createNote(note);
      }

      resetForm();
      await loadNotes();
    } catch (err) {
      setError(err.message || "Unable to save the note.");
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(note) {
    setTitle(note.title);
    setDescription(note.description);
    setDate(String(note.date).slice(0, 10));
    setEditingId(note.id);
    setError("");

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(id) {
    if (!window.confirm("Are you sure you want to delete this note?")) {
      return;
    }

    try {
      setError("");
      await deleteNote(id);

      if (editingId === id) {
        resetForm();
      }

      await loadNotes();
    } catch (err) {
      setError(err.message || "Unable to delete the note.");
    }
  }

  function openDatePicker() {
    const input = dateInputRef.current;

    if (!input) return;

    if (typeof input.showPicker === "function") {
      try {
        input.showPicker();
        return;
      } catch {
        // Fall back to focusing the native date input.
      }
    }

    input.focus();
  }

  // Show a loading screen while checking authentication.
  if (authChecking) {
    return (
      <div className="app">
        <main className="dashboard">
          <p className="status-message">Checking your session...</p>
        </main>
      </div>
    );
  }

  // Show login and registration when signed out.
  if (!token || !currentUser) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon" aria-hidden="true">
            ✎
          </div>

          <div>
            <h1>My Notes</h1>
            <p>Create, organize, and manage your notes.</p>
          </div>
        </div>

        <div className="user-controls">
          <span className="welcome-message">
            Welcome, {currentUser.name}
          </span>

          <button
            className="secondary-button"
            type="button"
            onClick={handleLogout}
          >
            Log Out
          </button>
        </div>
      </header>

      <main className="dashboard">
        <section className="panel form-panel">
          <h2>{editingId !== null ? "Edit Note" : "Create a Note"}</h2>

          <form className="note-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <label htmlFor="note-title">Title</label>
              <input
                id="note-title"
                type="text"
                placeholder="Enter your note title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="note-description">Description</label>
              <textarea
                id="note-description"
                placeholder="Write something worth remembering..."
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="note-date">Date</label>

              <div className="date-input-wrapper">
                <input
                  ref={dateInputRef}
                  id="note-date"
                  type="date"
                  value={date}
                  onChange={(event) => setDate(event.target.value)}
                  required
                />

                <button
                  className="calendar-button"
                  type="button"
                  onClick={openDatePicker}
                  aria-label="Open calendar"
                  title="Open calendar"
                >
                  ▦
                </button>
              </div>
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId !== null
                  ? "Update Note"
                  : "＋ Add Note"}
            </button>

            {editingId !== null && (
              <button
                className="secondary-button"
                type="button"
                onClick={resetForm}
                disabled={saving}
              >
                Cancel Edit
              </button>
            )}
          </form>
        </section>

        <section className="notes-section">
          <div className="notes-toolbar">
            <div>
              <h2>Your Notes</h2>
              <p className="notes-subtitle">
                All your notes in one place.
              </p>
            </div>

            <span className="note-count">
              {notes.length} {notes.length === 1 ? "note" : "notes"}
            </span>
          </div>

          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}

          {loading && (
            <p className="status-message">Loading notes...</p>
          )}

          {!loading && notes.length === 0 && !error && (
            <div className="empty-state">
              <span className="empty-icon" aria-hidden="true">
                ✎
              </span>
              <strong>No notes yet</strong>
              <p>Create your first note using the form.</p>
            </div>
          )}

          {!loading && notes.length > 0 && (
            <div className="notes-list">
              {notes.map((note) => (
                <article className="note-card" key={note.id}>
                  <div className="note-card-header">
                    <h3>{note.title}</h3>
                    <span className="note-date">
                      {String(note.date).slice(0, 10)}
                    </span>
                  </div>

                  <p className="note-description">
                    {note.description}
                  </p>

                  <div className="note-actions">
                    <button
                      type="button"
                      onClick={() => handleEdit(note)}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="delete-button"
                      onClick={() => handleDelete(note.id)}
                    >
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      <footer className="app-footer">
        StudyHub · Keep your thoughts organized.
      </footer>
    </div>
  );
}

export default App;
