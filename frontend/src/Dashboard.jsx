import React, { useState, useEffect } from "react";

function Dashboard() {
    const [yourPods, setYourPods] = useState([]);
    const [recommended, setRecommended] = useState([]);
    const [activePods, setActivePods] = useState([]);
    const [stats, setStats] = useState({ totalMessages: 0, totalVoiceMinutes: 0 });
  
    useEffect(() => {
      const token = localStorage.getItem("token");
  
      fetch("/pods/user", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setYourPods);
  
      fetch("/pods/recommended", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(data => setRecommended(data.filter(p => p.state !== "locked" && p.remaining_slots > 0)));
  
      fetch("/pods/active", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setActivePods);
  
      fetch("/stats", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setStats);
    }, []);
  
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
        {activePods.map(p => (
          <div key={p.id} style={{ marginBottom: "1rem" }}>
            <h4>{p.title}</h4>
            <ul>
              {p.messages.map((m, i) => (
                <li key={i}>
                  {m.media_type === "text" ? m.content : <em>[Voice message: {m.voice_path}]</em>}
                </li>
              ))}
            </ul>
          </div>
        ))}
  
        <h2>Overall App Stats</h2>
        <p>Total Messages Sent: {stats.totalMessages}</p>
        <p>Total Voice Minutes Shared: {stats.totalVoiceMinutes} minutes</p>
      </div>
    );
  }  

export default Dashboard;