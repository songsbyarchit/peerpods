import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./src/App";
import Login from "./src/Login";
import Register from "./src/Register";
import Dashboard from "./src/Dashboard";
import Create from "./src/Create";
import PodView from "./src/PodView";

const root = createRoot(document.getElementById("root"));
root.render(
  <Router>
  <Routes>
    <Route path="/" element={<App />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/create" element={<Create />} />
    <Route path="/pod/:id" element={<PodView />} />
  </Routes>
  </Router>
);