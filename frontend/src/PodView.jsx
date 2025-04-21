import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { API_URL } from "./config";

const API_URL = "${API_URL}";

function PodView() {
  const { id } = useParams();
  const [pod, setPod] = useState(null);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);  
  const [newMessage, setNewMessage] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch(`${API_URL}/pods/pod/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => {
        if (!res.ok) throw new Error("Pod not found");
        return res.json();
      })
      .then(setPod)
      .catch((err) => setError(err.message));    
      
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

  function handleSendMessage(e) {
    e.preventDefault();
    const token = localStorage.getItem("token");
    fetch(`${API_URL}/messages/pods/${id}/send`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: new URLSearchParams({ content: newMessage })
    })
      .then(res => {
        if (!res.ok) throw new Error("Failed to send message");
        return res.json();
      })
      .then(() => {
        setNewMessage("");
        // Re-fetch pod messages
        fetch(`${API_URL}/pods/pod/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
          .then(res => res.json())
          .then(setPod);
      })
      .catch(err => alert(err.message));
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h2>{pod.title}</h2>
      <p>{pod.description}</p>
      <p><em>Media type:</em> {pod.media_type}</p>
      <p><em>Creator:</em> {pod.creator}</p>

      <h3>Messages</h3>
      <ul style={{ listStyleType: "none", paddingLeft: 0, paddingBottom: "6rem" }}>
      {[...pod.messages]
        .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
        .map((msg, idx) => {
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
                  ({new Date(msg.created_at).toLocaleString("en-GB", { timeZone: "Europe/London" })})
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
      {pod.can_send && (
        <form
          onSubmit={handleSendMessage}
          style={{
            position: "fixed",
            bottom: 0,
            left: 0,
            width: "100%",
            backgroundColor: "#fff",
            padding: "1rem",
            display: "flex",
            justifyContent: "center",
            borderTop: "1px solid #ccc",
            zIndex: 1000
          }}
        >
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            rows={3}
            style={{
              width: "70%",
              padding: "0.5rem",
              marginRight: "1rem",
              fontSize: "1rem",
              resize: "none",
              minHeight: "4.5rem",
              maxHeight: "7rem",
              overflowY: "auto",
              lineHeight: "1.5rem"
            }}
          />
          <button type="submit" disabled={!newMessage.trim()}>Send</button>
        </form>
      )}
  </div>
  );
}

export default PodView;