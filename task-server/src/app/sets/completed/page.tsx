"use client";
import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { TaskSetSolution } from "@/types/solution";

export default function SetCompletedPage() {
  const searchParams = useSearchParams();
  const [solution, setSolution] = useState<TaskSetSolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Try to get solution from navigation state (if available)
  useEffect(() => {
    const navState = window.history.state?.usr || window.history.state?.state;
    if (navState && navState.solution) {
      setSolution(navState.solution);
      setLoading(false);
      return;
    }
    // Fallback: check for uuid in query params
    const uuid = searchParams?.get("uuid");
    if (uuid) {
      fetch(`/api/solutions/${uuid}`)
        .then((res) => {
          if (!res.ok) throw new Error("Solution not found");
          return res.json();
        })
        .then((data) => {
          setSolution(data);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || "Failed to load solution");
          setLoading(false);
        });
    } else {
      setError("No solution data available.");
      setLoading(false);
    }
  }, [searchParams]);

  if (loading) {
    return <div style={{ textAlign: "center", marginTop: 48 }}>Loading solution...</div>;
  }

  // Placeholder: show success message for now
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "#f6fff6",
        padding: 16,
      }}
    >
      <h1 style={{ color: "#28a745", fontSize: "2.5rem", marginBottom: 24 }}>Success!</h1>
      <p style={{ fontSize: "1.2rem", color: "#333", marginBottom: 16 }}>Your solution was saved successfully.</p>

      {error && <div style={{ color: "#dc3545", textAlign: "center", marginTop: 48 }}>{error}</div>}
      {/* TODO: Add table and solution ID display here */}
    </div>
  );
}
