import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_BASE = "/api";

function App() {
  const [monitors, setMonitors] = useState([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadMonitors() {
    try {
      const response = await fetch(`${API_BASE}/monitors`);
      if (!response.ok) throw new Error("Could not load monitors");
      setMonitors(await response.json());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMonitors();
    const timer = setInterval(loadMonitors, 5000);
    return () => clearInterval(timer);
  }, []);

  async function addMonitor(event) {
    event.preventDefault();
    setError("");
    try {
      const response = await fetch(`${API_BASE}/monitors`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not add URL");
      setUrl("");
      await loadMonitors();
    } catch (err) {
      setError(err.message);
    }
  }

  async function checkNow(id) {
    setError("");
    const response = await fetch(`${API_BASE}/monitors/${id}/check`, { method: "POST" });
    if (!response.ok) {
      setError("Manual check failed");
      return;
    }
    await loadMonitors();
  }

  async function removeMonitor(id) {
    const response = await fetch(`${API_BASE}/monitors/${id}`, { method: "DELETE" });
    if (!response.ok) {
      setError("Could not delete monitor");
      return;
    }
    await loadMonitors();
  }

  return (
    <main className="container">
      <header>
        <div>
          <p className="eyebrow">LIGHTWEIGHT STATUS DASHBOARD</p>
          <h1>Uptime Monitor</h1>
          <p className="subtitle">Checks registered URLs every 60 seconds.</p>
        </div>
        <div className="summary">{monitors.length} monitored</div>
      </header>

      <form className="add-form" onSubmit={addMonitor}>
        <input
          type="url"
          required
          placeholder="https://example.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Add URL</button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <p>Loading...</p>
      ) : monitors.length === 0 ? (
        <section className="empty">Add your first URL to begin monitoring.</section>
      ) : (
        <section className="grid">
          {monitors.map((monitor) => {
            const check = monitor.latest_check;
            const state = !check ? "pending" : check.is_up ? "up" : "down";
            return (
              <article className="card" key={monitor.id}>
                <div className="card-top">
                  <span className={`badge ${state}`}>{state.toUpperCase()}</span>
                  <span className="response-time">
                    {check?.response_time_ms != null ? `${check.response_time_ms} ms` : "No data"}
                  </span>
                </div>
                <a href={monitor.url} target="_blank" rel="noreferrer" className="url">
                  {monitor.url}
                </a>
                <div className="details">
                  <span>HTTP: {check?.status_code ?? "-"}</span>
                  <span>
                    Last check: {check ? new Date(check.checked_at).toLocaleString() : "Pending"}
                  </span>
                </div>
                {check?.error && <p className="check-error">{check.error}</p>}
                <div className="actions">
                  <button className="secondary" onClick={() => checkNow(monitor.id)}>Check now</button>
                  <button className="danger" onClick={() => removeMonitor(monitor.id)}>Delete</button>
                </div>
              </article>
            );
          })}
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
