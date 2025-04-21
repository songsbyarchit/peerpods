import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { API_URL } from "./config";

const API_URL = "${API_URL}";

function AllPodsView() {
  const [pods, setPods] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/pods/preview`)
      .then((res) => res.json())
      .then((data) => setPods(data))
      .catch((err) => console.error("Error fetching pods:", err));
  }, []);

  return (
    <div style={{ backgroundColor: "#121212", color: "#f5f5f5", minHeight: "100vh", padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>All Pods</h1>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        {pods.map((pod) => (
          <div key={pod.id} style={{
            border: "1px solid #444",
            borderRadius: "8px",
            backgroundColor: "#1e1e1e",
            padding: "1rem",
            width: "300px"
          }}>
            <h3>{pod.title}</h3>
            <p>{pod.description}</p>
            <p><strong>Media:</strong> {pod.media_type}</p>
            <p><strong>Duration:</strong> {pod.duration_hours}h</p>
            <p><strong>Users:</strong> {pod.user_count} | <strong>Messages:</strong> {pod.message_count}</p>
            {pod.view_only ? (
              <span style={{ color: "#ff6b6b" }}>View Only</span>
            ) : (
              <>
                <p>Remaining Slots: {pod.remaining_slots}</p>
                {pod.auto_launch_at && <p>Countdown: {new Date(pod.auto_launch_at).toLocaleString()}</p>}
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const root = createRoot(document.getElementById("allpods-root"));
root.render(<AllPodsView />);