import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const API_URL = "http://localhost:8000";

function PodView() {
  const { id } = useParams();
  const [pod, setPod] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/pods/pod/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Pod not found");
        return res.json();
      })
      .then(setPod)
      .catch((err) => setError(err.message));
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
      <ul>
      {pod.messages.map((msg, idx) => (
        <li key={idx}>
            <strong>{msg.user}:</strong>{" "}
            {msg.media_type === "text"
            ? msg.content
            : <em>[Voice message: {msg.voice_path}]</em>}
        </li>
        ))}
      </ul>
    </div>
  );
}

export default PodView;