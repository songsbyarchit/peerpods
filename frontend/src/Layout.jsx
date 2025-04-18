import React, { useState, useEffect } from "react";
import Navbar from "./Navbar";
import { Outlet } from "react-router-dom";

function Layout({ children }) {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    fetch("http://localhost:8000/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setCurrentUser)
      .catch(() => setCurrentUser(null));
  }, []);


  return (
    <>
      <Navbar currentUser={currentUser} setCurrentUser={setCurrentUser} />
      <main><Outlet /></main>
    </>
  );
}

export default Layout;