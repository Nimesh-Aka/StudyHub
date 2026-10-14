
import { useEffect, useState } from "react";
import { getNotes } from "./api";
import "./App.css";

function App() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadNotes() {
      try {
        const data = await getNotes();
        setNotes(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadNotes();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>My Notes</h1>
        <p>Your notes, saved in PostgreSQL.</p>
      </header>

      <section className="notes-list">
        <h2>Your Notes ({notes.length})</h2>

        {loading && <p>Loading notes...</p>}
        {error && <p>{error}</p>}

        {!loading &&
          !error &&
          notes.map((note) => (
            <article className="note-card" key={note.id}>
              <h3>{note.title}</h3>
              <p>{note.description}</p>
              <small>{note.date}</small>
            </article>
          ))}
      </section>
    </div>
  );
}

export default App;
