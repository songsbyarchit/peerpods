import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

function Create() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [durationHours, setDurationHours] = useState(24);
  const [driftTolerance, setDriftTolerance] = useState(3);
  const [mediaType, setMediaType] = useState("text");
  const [maxChars, setMaxChars] = useState(500);
  const [maxMessages, setMaxMessages] = useState(10);
  const [launchMode, setLaunchMode] = useState("manual");
  const [maxVoiceSeconds, setMaxVoiceSeconds] = useState(60); // new  
  const [autoLaunchAt, setAutoLaunchAt] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  useEffect(() => {
    const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
    setTimezone(detected);
  }, []);  

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const token = localStorage.getItem("token");
  
    const payload = {
      title,
      description,
      duration_hours: durationHours,
      drift_tolerance: driftTolerance,
      media_type: mediaType,
      max_chars_per_message: maxChars,
      max_messages_per_day: maxMessages,
      launch_mode: launchMode,
      auto_launch_at: launchMode === "countdown" ? autoLaunchAt : null,
      timezone,
      max_voice_message_seconds: mediaType === "voice" || mediaType === "both" ? maxVoiceSeconds : null,      
    };
  
    try {
      const res = await fetch(`${API_URL}/pods/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
  
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to create pod.");
      }
  
      const data = await res.json();
      console.log("Pod created:", data);
      alert("Pod created!");
    } catch (err) {
      console.error("Pod creation failed:", err);
      alert("Error creating pod.");
    }
  };  

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: 600, margin: "0 auto" }}>
      <h2>Create a New Pod</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />

        <label>
          Duration (hours):
          <select value={durationHours} onChange={(e) => setDurationHours(Number(e.target.value))}>
            <option value={24}>24h</option>
            <option value={168}>7 days</option>
            <option value={720}>30 days</option>
          </select>
        </label>

        <label>
        Drift Tolerance:
        <input
            type="range"
            min="1"
            max="5"
            value={driftTolerance}
            onChange={(e) => setDriftTolerance(Number(e.target.value))}
        />
        <div style={{ fontSize: "0.9rem", color: "#555" }}>
            Current: {driftTolerance} — {["Strict", "Low", "Medium", "High", "Very High"][driftTolerance - 1]}
        </div>
        </label>

        <label>
          Media Type:
          <select value={mediaType} onChange={(e) => setMediaType(e.target.value)}>
            <option value="text">Text only</option>
            <option value="voice">Voice only</option>
            <option value="both">Both</option>
          </select>
        </label>

        {(mediaType === "voice" || mediaType === "both") && (
        <label>
            Max voice note duration (seconds):
            <select value={maxVoiceSeconds} onChange={(e) => setMaxVoiceSeconds(Number(e.target.value))}>
            <option value={30}>30s</option>
            <option value={60}>1 min</option>
            <option value={180}>3 mins</option>
            <option value={300}>5 mins</option>
            </select>
        </label>
        )}

        {(mediaType === "text" || mediaType === "both") && (
        <label>
            Max characters per message:
            <select value={maxChars} onChange={(e) => setMaxChars(Number(e.target.value))}>
            <option value={100}>100</option>
            <option value={250}>250</option>
            <option value={500}>500</option>
            <option value={1000}>1000</option>
            </select>
        </label>
        )}

        <label>
          Max messages per day:
          <select value={maxMessages} onChange={(e) => setMaxMessages(Number(e.target.value))}>
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
        </label>

        <label>
        Launch Mode:
        <select value={launchMode} onChange={(e) => setLaunchMode(e.target.value)}>
            <option value="manual">Manual</option>
            <option value="countdown">Countdown</option>
        </select>
        </label>

        {launchMode === "countdown" && (
        <label>
            Auto Launch At (ISO format):
            <input
            type="datetime-local"
            value={autoLaunchAt}
            onChange={(e) => setAutoLaunchAt(e.target.value)}
            required
            />
        </label>
        )}

        <button type="submit">Next: Configure Launch</button>
      </form>
    </div>
  );
}

export default Create;