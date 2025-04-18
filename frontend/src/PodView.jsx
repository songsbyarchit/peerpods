import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const API_URL = "http://localhost:8000";

function PodView() {
  const { id } = useParams();
  const [pod, setPod] = useState(null);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);  

  useEffect(() => {
    fetch(`${API_URL}/pods/pod/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Pod not found");
        return res.json();
      })
      .then(setPod)
      .catch((err) => setError(err.message));

    const token = localStorage.getItem("token");
    if (token) {
      fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then(setCurrentUser)
        .catch(() => setCurrentUser(null));
    }
  }, [id]);

  if (error) return <p style={{ color: "red" }}>Error: {error}</p>;
  if (!pod) return <p>Loading...</p>;

  return (
    <div style={{ padding: "2rem" }}>
      <h2>{pod.title}</h2>
      <p>{pod.description}</p>
      <p><em>Media type:</em> {pod.media_type}</p>
      <p><em>Creator:</em> {pod.creator}</p>

      <h3>Messages</h3>
      <ul style={{ listStyleType: "none", paddingLeft: 0 }}>
      {pod.messages.map((msg, idx) => {
        console.log("Message timestamp:", msg.created_at);
        return (
                <li key={idx} style={{
                    backgroundColor: "#f0f0f0",
                    borderRadius: "10px",
                    padding: "0.75rem",
                    marginBottom: "0.5rem",
                    maxWidth: "70%",
                    boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
                    alignSelf: currentUser?.username === msg.user ? "flex-end" : "flex-start",
                    marginLeft: currentUser?.username === msg.user ? "auto" : "0",
                    backgroundColor: currentUser?.username === msg.user ? "#d1ffd6" : "#f0f0f0",
                }}>
                <div style={{ fontWeight: "bold", marginBottom: "0.25rem" }}>
                {msg.user} <span style={{ fontWeight: "normal", color: "#777", fontSize: "0.8rem" }}>
                    ({new Date(msg.created_at).toLocaleString()})
                </span>
                </div>
                <div>
                {msg.media_type === "text"
                    ? msg.content
                    : <em>[Voice message: {msg.voice_path}]</em>}
                </div>
            </li>
        );
        })}
      </ul>
    </div>
  );
}

export default PodView;