import React from "react";
import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { API_URL } from "./config";

function Navbar({ currentUser, setCurrentUser }) {  

  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    setCurrentUser(null);
    navigate("/login");
  };

  return (
    <nav style={{ padding: "1rem", background: "#eee", marginBottom: "2rem" }}>
      <Link to="/" style={{ marginRight: "1rem" }}>Home</Link>
      {currentUser ? (
        <>
          <Link to="/dashboard" style={{ marginRight: "1rem" }}>Dashboard</Link>
          <Link to="/create" style={{ marginRight: "1rem" }}>Create</Link>
          <span style={{ marginRight: "1rem" }}>
            Welcome, <strong>{currentUser.username}</strong>
          </span>
          <button onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <>
          <Link to="/login" style={{ marginRight: "1rem" }}>Login</Link>
          <Link to="/register">Register</Link>
        </>
      )}
    </nav>
  );
}

export default Navbar;