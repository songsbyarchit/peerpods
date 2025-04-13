import React, { useState } from "react";
import { createRoot } from "react-dom/client";

const API_URL = "http://localhost:8000";

function App() {
  // States for listing
  const [users, setUsers] = useState([]);
  const [pods, setPods] = useState([]);
  const [messages, setMessages] = useState([]);
  const [recommended, setRecommended] = useState([]);

  // States for creation forms
  const [newUsername, setNewUsername] = useState("");
  const [newBio, setNewBio] = useState("");

  const [newPodTitle, setNewPodTitle] = useState("");
  const [newPodDesc, setNewPodDesc] = useState("");
  const [newPodHours, setNewPodHours] = useState(24);
  const [newPodDrift, setNewPodDrift] = useState(1);

  const [newMsgContent, setNewMsgContent] = useState("");
  const [newMsgUserId, setNewMsgUserId] = useState("");
  const [newMsgPodId, setNewMsgPodId] = useState("");

  const [recommendUserId, setRecommendUserId] = useState("");

  // Fetch lists
  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/users/`);
      const data = await res.json();
      setUsers(data);
    } catch (err) {
      console.error("Error fetching users:", err);
    }
  };

  const fetchPods = async () => {
    try {
      const res = await fetch(`${API_URL}/pods/`);
      const data = await res.json();
      setPods(data);
    } catch (err) {
      console.error("Error fetching pods:", err);
    }
  };

  const fetchMessages = async () => {
    try {
      const res = await fetch(`${API_URL}/messages/`);
      const data = await res.json();
      setMessages(data);
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  };

  // Create new user
  const createUser = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/users/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: newUsername,
          bio: newBio,
        }),
      });
      const data = await res.json();
      // Clear form
      setNewUsername("");
      setNewBio("");
      console.log("Created user:", data);
    } catch (err) {
      console.error("Error creating user:", err);
    }
  };

  // Create new pod
  const createPod = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/pods/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newPodTitle,
          description: newPodDesc,
          duration_hours: Number(newPodHours),
          drift_tolerance: Number(newPodDrift),
        }),
      });
      const data = await res.json();
      // Clear form
      setNewPodTitle("");
      setNewPodDesc("");
      setNewPodHours(24);
      setNewPodDrift(1);
      console.log("Created pod:", data);
    } catch (err) {
      console.error("Error creating pod:", err);
    }
  };

  // Create new message
  const createMessage = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: Number(newMsgUserId),
          pod_id: Number(newMsgPodId),
          content: newMsgContent,
        }),
      });
      const data = await res.json();
      // Clear form
      setNewMsgContent("");
      setNewMsgUserId("");
      setNewMsgPodId("");
      console.log("Created message:", data);
    } catch (err) {
      console.error("Error creating message:", err);
    }
  };

  // Get recommended pods
  const getRecommended = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/users/${recommendUserId}/recommended`);
      const data = await res.json();
      setRecommended(data);
    } catch (err) {
      console.error("Error getting recommended pods:", err);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1>PeerPods Frontend</h1>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Lists</h2>
        <button onClick={fetchUsers}>Fetch Users</button>{" "}
        <button onClick={fetchPods}>Fetch Pods</button>{" "}
        <button onClick={fetchMessages}>Fetch Messages</button>
        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <div>
            <h3>Users</h3>
            <ul>
              {users.map((u) => (
                <li key={u.id}>
                  {u.id}. {u.username} (Bio: {u.bio})
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3>Pods</h3>
            <ul>
              {pods.map((p) => (
                <li key={p.id}>
                  {p.id}. {p.title} (Desc: {p.description})
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3>Messages</h3>
            <ul>
              {messages.map((m) => (
                <li key={m.id}>
                  {m.id}. Content: {m.content}, User: {m.user_id}, Pod: {m.pod_id}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Create User</h2>
        <form onSubmit={createUser} style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="text"
            placeholder="Username"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Bio"
            value={newBio}
            onChange={(e) => setNewBio(e.target.value)}
          />
          <button type="submit">Create User</button>
        </form>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Create Pod</h2>
        <form onSubmit={createPod} style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="text"
            placeholder="Title"
            value={newPodTitle}
            onChange={(e) => setNewPodTitle(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Description"
            value={newPodDesc}
            onChange={(e) => setNewPodDesc(e.target.value)}
          />
          <input
            type="number"
            placeholder="Duration (hours)"
            value={newPodHours}
            onChange={(e) => setNewPodHours(e.target.value)}
          />
          <input
            type="number"
            placeholder="Drift Tolerance"
            value={newPodDrift}
            onChange={(e) => setNewPodDrift(e.target.value)}
          />
          <button type="submit">Create Pod</button>
        </form>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Create Message</h2>
        <form onSubmit={createMessage} style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="number"
            placeholder="User ID"
            value={newMsgUserId}
            onChange={(e) => setNewMsgUserId(e.target.value)}
            required
          />
          <input
            type="number"
            placeholder="Pod ID"
            value={newMsgPodId}
            onChange={(e) => setNewMsgPodId(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Content"
            value={newMsgContent}
            onChange={(e) => setNewMsgContent(e.target.value)}
            required
          />
          <button type="submit">Create Message</button>
        </form>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Recommended Pods</h2>
        <form onSubmit={getRecommended} style={{ display: "flex", gap: "0.5rem" }}>
          <input
            type="number"
            placeholder="User ID"
            value={recommendUserId}
            onChange={(e) => setRecommendUserId(e.target.value)}
            required
          />
          <button type="submit">Get Recommended Pods</button>
        </form>
        <ul>
          {recommended.map((r) => (
            <li key={r.id}>
              {r.id}. {r.title} (Desc: {r.description})
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);