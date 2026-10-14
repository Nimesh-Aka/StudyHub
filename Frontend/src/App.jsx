
import { useEffect, useState } from "react";
import {
  getNotes,
  createNote,
  updateNote,
  deleteNote,
} from "./api";
import "./App.css";

function App() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState(
    new Date().toLocaleDateString("en-CA")
  );

  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadNotes() {
    try {
      setError("");
      const data = await getNotes();
      setNotes(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNotes();
  }, []);

  function resetForm() {
    setTitle("");
    setDescription("");
    setDate(new Date().toLocaleDateString("en-CA"));
    setEditingId(null);
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
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(note) {
    setTitle(note.title);
    setDescription(note.description);
    setDate(note.date);
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
      await loadNotes();

      if (editingId === id) {
        resetForm();
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>My Notes</h1>
        <p>Create and manage your notes.</p>
      </header>

      <form className="note-form" onSubmit={handleSubmit}>
        <h2>{editingId !== null ? "Edit Note" : "Create Note"}</h2>

        <input
          type="text"
          placeholder="Note title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          required
        />

        <textarea
          placeholder="Write your note..."
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          required
        />

        <input
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          required
        />

        <button type="submit" disabled={saving}>
          {saving
            ? "Saving..."
            : editingId !== null
              ? "Update Note"
              : "Add Note"}
        </button>

        {editingId !== null && (
          <button type="button" onClick={resetForm}>
            Cancel Edit
          </button>
        )}
      </form>

      {error && <p className="error">{error}</p>}

      <section className="notes-list">
        <h2>Your Notes ({notes.length})</h2>

        {loading && <p>Loading notes...</p>}

        {!loading && !error && notes.length === 0 && (
          <p>No notes yet. Create your first note!</p>
        )}

        {notes.map((note) => (
          <article className="note-card" key={note.id}>
            <h3>{note.title}</h3>
            <p>{note.description}</p>
            <small>{note.date}</small>

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
      </section>
    </div>
  );
}

export default App;
