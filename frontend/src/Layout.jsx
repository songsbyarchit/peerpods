import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";
import { Outlet } from "react-router-dom";
import { API_URL } from "./config";

function Layout({ children }) {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    console.log("🔍 Layout mounted");

    const token = localStorage.getItem("token");
    console.log("🪪 Retrieved token:", token);
    if (!token) return;

    console.log("🌐 Making fetch to:", `${API_URL}/auth/me`);

    fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(async res => {
        console.log("📬 Response received:", res.status);
        const data = await res.json();
        console.log("📦 Response data:", data);
        setCurrentUser(data);
      })
      .catch(err => {
        console.error("❌ Fetch failed:", err);
        setCurrentUser(null);
      });
  }, []);

  return (
    <>
      {currentUser === null && localStorage.getItem("token") ? (
        <p>Loading...</p>
      ) : (
        <>
          <Navbar currentUser={currentUser} setCurrentUser={setCurrentUser} />
          <main>
            <Outlet context={{ currentUser, setCurrentUser }} />
          </main>
        </>
      )}
    </>
  );
}

export default Layout;