import React, { useState, useEffect } from "react";

function Dashboard() {
    const [yourPods, setYourPods] = useState([]);
    const [recommended, setRecommended] = useState([]);
    const [activePods, setActivePods] = useState([]);
    const [showAllPods, setShowAllPods] = useState(false);    
    const [stats, setStats] = useState({ totalMessages: 0, totalVoiceMinutes: 0 });
  
    useEffect(() => {
      const token = localStorage.getItem("token");
  
        fetch("http://localhost:8000/pods/user", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setYourPods);
  
      fetch("http://localhost:8000/pods/recommended", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(data => setRecommended(data.filter(p => p.state !== "locked" && p.remaining_slots > 0)));
  
      fetch("http://localhost:8000/pods/active", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setActivePods);
  
      fetch("http://localhost:8000/stats", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setStats);
    }, []);

    function formatCountdown(isoTime) {
      if (!isoTime) return "N/A";
      const now = new Date();
      const target = new Date(isoTime);
      const diff = target - now;
      if (diff <= 0) return "Ended";
      const hours = String(Math.floor(diff / (1000 * 60 * 60))).padStart(2, "0");
      const minutes = String(Math.floor((diff / (1000 * 60)) % 60)).padStart(2, "0");
      const seconds = String(Math.floor((diff / 1000) % 60)).padStart(2, "0");
      return `${hours}:${minutes}:${seconds}`;
    }    
  
    return (
      <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
        <h2>Your Pods</h2>
        {yourPods.length === 0 ? (
          <p>You have no pods. <a href="/create">Create one now</a>.</p>
        ) : (
          <ul>
            {yourPods.map(p => (
              <li key={p.id}><strong>{p.title}</strong> — {p.state}</li>
            ))}
          </ul>
        )}
  
        <h2>Top 3 Recommended Pods</h2>
        <ul>
          {recommended.slice(0, 3).map(p => (
            <li key={p.id}>
              <strong>{p.title}</strong><br />
              <em>{p.description}</em><br />
              <button onClick={() => joinPod(p.id)}>Join</button>
            </li>
          ))}
        </ul>
  
        <h2>Active Pods (Spectator View)</h2>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
            {(showAllPods ? activePods : activePods.slice(0, 10)).map((p) => (
            <a
              key={p.id}
              href={`/pod/${p.id}`}
              style={{
                border: "1px solid #ccc",
                borderRadius: "10px",
                padding: "1rem",
                width: "200px",
                textDecoration: "none",
                color: "black",
                backgroundColor: "#f9f9f9",
                boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
                position: "relative"
              }}
              title={`Users: ${p.messages.map(m => m.user).join(", ")}`}
            >
              <strong>{p.title}</strong>
              <div style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
                <div><em>Status:</em> {p.state || "unknown"}</div>
                <div><em>Messages:</em> {p.messages.length}</div>
                <div><em>Users:</em> {new Set(p.messages.map(m => m.user)).size}</div>
                <div><em>Time left:</em> {formatCountdown(p.auto_launch_at)}</div>
              </div>
            </a>
          ))}
          {activePods.length > 10 && (
            <button onClick={() => setShowAllPods(prev => !prev)}>
              {showAllPods ? "Show Less" : "View More"}
            </button>
          )}
          </div>
  
        <h2>Overall App Stats</h2>
        <p>Total Messages Sent: {stats.totalMessages}</p>
        <p>Total Voice Minutes Shared: {stats.totalVoiceMinutes} minutes</p>
      </div>
    );
  }  

export default Dashboard;