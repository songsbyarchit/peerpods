import React, { useState, useEffect } from "react";

function Dashboard() {
    const [yourPods, setYourPods] = useState([]);
    const [recommended, setRecommended] = useState([]);
    const [activePods, setActivePods] = useState([]);
    const [visibleRows, setVisibleRows] = useState(() => {
      const saved = localStorage.getItem("visibleRows");
      return saved ? parseInt(saved, 10) : 1;
    });    
    const [tilesPerRow, setTilesPerRow] = useState(5);    
    const [stats, setStats] = useState({ totalMessages: 0, totalVoiceMinutes: 0 });
    const [searchQuery, setSearchQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [filterState, setFilterState] = useState("");
    const [filterMedia, setFilterMedia] = useState("");
    const [sortOption, setSortOption] = useState("");    
    const [visibleSearchCount, setVisibleSearchCount] = useState(5);

    useEffect(() => {
      fetch("http://localhost:8000/pods/refresh-states", {
        method: "POST"
      }).catch(err => console.error("Failed to refresh pod states:", err));
    }, []);    

    useEffect(() => {
      const token = localStorage.getItem("token");
  
      fetch("http://localhost:8000/pods/user-full", { headers: { Authorization: `Bearer ${token}` } })
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
  
      fetch("http://localhost:8000/pods/stats", { headers: { Authorization: `Bearer ${token}` } })
        .then(res => res.json())
        .then(setStats);
    }, []);

    useEffect(() => {
      function updateTilesPerRow() {
        const width = window.innerWidth;
        const tileWidth = 220; // tile + padding + margin
        const perRow = Math.floor(width / tileWidth);
        setTilesPerRow(perRow);
      }
    
      updateTilesPerRow();
      window.addEventListener("resize", updateTilesPerRow);
      return () => window.removeEventListener("resize", updateTilesPerRow);
    }, []);    

    useEffect(() => {
      localStorage.setItem("visibleRows", visibleRows.toString());
    }, [visibleRows]);    

    function handleSearch(e) {
      e.preventDefault();
      const token = localStorage.getItem("token");
    
      const params = new URLSearchParams({ query: searchQuery });
      if (filterState) params.append("state", filterState);
      if (filterMedia) params.append("media", filterMedia);
      if (sortOption) params.append("sort", sortOption);
      
      fetch(`http://localhost:8000/pods/search?${params.toString()}`, {
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
        <select
          value={sortOption}
          onChange={(e) => setSortOption(e.target.value)}
          style={{ marginLeft: "0.5rem", padding: "0.5rem" }}
        >
          <option value="">Sort By</option>
          <option value="messages">Most Messages</option>
          <option value="latest">Most Recent Message</option>
          <option value="duration">Longest Duration</option>
        </select>
        <button type="submit" style={{ marginLeft: "0.5rem" }}>Search</button>
      </form>

      {searchResults.length > 0 && (
        <div style={{ marginBottom: "2rem" }}>
          <h2>Search Results</h2>
          <ul style={{ listStyleType: "none", paddingLeft: 0 }}>
              {searchResults.slice(0, visibleSearchCount).map((pod) => (
              <li key={pod.id} style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ccc", borderRadius: "8px" }}>
                <strong>{pod.title}</strong> — {pod.description}
                <div style={{ fontSize: "0.9rem", color: "#777" }}>
                  Media: {pod.media_type} | Duration: {pod.duration_hours}h | Messages: {pod.message_count}
                </div>
              </li>
            ))}
          </ul>
          {searchResults.length > 5 && (
            <div style={{ marginTop: "1rem" }}>
              {visibleSearchCount < searchResults.length && (
                <button onClick={() => setVisibleSearchCount(prev => prev + 5)}>
                  Show More Results
                </button>
              )}
              {visibleSearchCount > 5 && (
                <button
                  onClick={() => setVisibleSearchCount(5)}
                  style={{ marginLeft: "0.5rem" }}
                >
                  Show Less
                </button>
              )}
            </div>
          )}
        </div>
      )}

        <h2>Your Pods</h2>
        {yourPods.length === 0 ? (
          <p>You have no pods. <a href="/create">Create one now</a>.</p>
        ) : (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginBottom: "1rem" }}>
          {yourPods.map(p => (
            <a
              key={p.id}
              href={`/pod/${p.id}`}
              style={{
                border: "1px solid #ccc",
                borderRadius: "10px",
                padding: "1rem",
                width: "200px",
                backgroundColor: p.is_creator ? "#c8f7c5" : p.is_participant ? "#dbeafe" : "#f9f9f9",
                boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
                textDecoration: "none",
                color: "black"
              }}
              title={`Role: ${p.is_creator ? "Creator" : "Participant"} | Status: ${p.state}`}
            >
              <strong>{p.title}</strong>
              <div style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                <div><em>Role:</em> {p.is_creator ? "Creator" : "Participant"}</div>
                <div><em>Status:</em> {p.state}</div>
              </div>
            </a>
          ))}
        </div>
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
            {activePods.slice(0, visibleRows * tilesPerRow).map((p) => (
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
                backgroundColor: p.is_creator ? "#c8f7c5" : p.is_participant ? "#dbeafe" : "#f9f9f9",
                boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
                position: "relative"
              }}
              title={`Creator: ${p.creator || "Unknown"} | Users: ${p.messages ? p.messages.map(m => m.user).join(", ") : "No messages yet"}`}
              >
              <strong>{p.title}</strong>
              <div style={{ fontSize: "0.8rem", marginTop: "0.5rem" }}>
                <div>
                  <em>Creator:</em>{" "}
                  {p.is_creator ? <strong>You</strong> : p.creator || "Unknown"}
                </div>
                <div><em>Status:</em> {p.state || "unknown"}</div>
                <div><em>Messages:</em> {p.messages ? p.messages.length : 0}</div>
                <div><em>Users:</em> {p.messages ? new Set(p.messages.map(m => m.user)).size : 0}</div>
                {p.state === "scheduled" && (
                  <div><em>Time left:</em> {formatCountdown(p.auto_launch_at)}</div>
                )}
                </div>
            </a>
          ))}
          {activePods.length > tilesPerRow && (
            <div style={{ marginTop: "1rem" }}>
              {visibleRows * tilesPerRow < activePods.length && (
                <button onClick={() => setVisibleRows(prev => prev + 1)}>
                  Show More Pods
                </button>
              )}
              {visibleRows > 1 && (
                <button
                  onClick={() => setVisibleRows(1)}
                  style={{ marginLeft: "0.5rem" }}
                >
                  Show Less
                </button>
              )}
            </div>
          )}
          </div>
  
          <h2>Overall App Stats</h2>
          <p>Total Messages Sent: {stats.totalMessages}</p>
          <p>Total Voice Minutes Shared: {stats.totalVoiceMinutes} minutes</p>
          <p>Total Pods Created: {stats.totalPods}</p>
          <p>Total Users Registered: {stats.totalUsers}</p>
      </div>
    );
  }  

export default Dashboard;