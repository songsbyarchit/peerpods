import React, { useState, useEffect } from "react";

function Dashboard() {
    const [yourPods, setYourPods] = useState([]);
    const [recommended, setRecommended] = useState([]);
    const [activePods, setActivePods] = useState([]);
    const [showAllPods, setShowAllPods] = useState(false);    
    const [stats, setStats] = useState({ totalMessages: 0, totalVoiceMinutes: 0 });
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
  
    useEffect(() => {
      fetch("http://localhost:8000/pods/refresh-states", {
        method: "POST"
      }).catch(err => console.error("Failed to refresh pod states:", err));
    }, []);    

    useEffect(() => {
      const token = localStorage.getItem("token");
  
        fetch("http://localhost:8000/pods/user", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setYourPods);
  
      fetch("http://localhost:8000/pods/recommended", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(data => setRecommended(data.filter(p => p.state !== "locked" && p.remaining_slots > 0)));
  
        fetch("http://localhost:8000/pods", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(data => {
          const activeOnly = data.filter(p => p.state === "active");
          setActivePods(activeOnly);
        });      
  
      fetch("http://localhost:8000/stats", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setStats);
    }, []);

    function handleSearch(e) {
      e.preventDefault();
      const token = localStorage.getItem("token");
    
      fetch(`http://localhost:8000/pods/search?query=${encodeURIComponent(searchQuery)}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => setSearchResults(data))
        .catch(err => console.error("Search failed:", err));
    }    

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

        <form onSubmit={handleSearch} style={{ marginBottom: "2rem" }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search pod titles or descriptions..."
            style={{ padding: "0.5rem", width: "300px" }}
          />
          <button type="submit" style={{ marginLeft: "0.5rem" }}>Search</button>
        </form>

        {searchResults.length > 0 && (
          <div style={{ marginBottom: "2rem" }}>
            <h2>Search Results</h2>
            <ul style={{ listStyleType: "none", paddingLeft: 0 }}>
              {searchResults.map((pod) => (
                <li key={pod.id} style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ccc", borderRadius: "8px" }}>
                  <strong>{pod.title}</strong> — {pod.description}
                  <div style={{ fontSize: "0.9rem", color: "#777" }}>
                    Media: {pod.media_type} | Duration: {pod.duration_hours}h | Messages: {pod.message_count}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

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
              title={`Creator: ${p.creator || "Unknown"} | Users: ${p.messages ? p.messages.map(m => m.user).join(", ") : "No messages yet"}`}
              >
              <strong>{p.title}</strong>
              <div style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
                <div><em>Creator:</em> {p.creator || "Unknown"}</div>
                <div><em>Status:</em> {p.state || "unknown"}</div>
                <div><em>Messages:</em> {p.messages ? p.messages.length : 0}</div>
                <div><em>Users:</em> {p.messages ? new Set(p.messages.map(m => m.user)).size : 0}</div>
                {p.state === "scheduled" && (
                  <div><em>Time left:</em> {formatCountdown(p.auto_launch_at)}</div>
                )}
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