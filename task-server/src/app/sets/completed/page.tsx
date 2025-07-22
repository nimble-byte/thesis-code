"use client";
import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import type { TaskSetSolution } from "@/types/solution";
import TaskReportTable from "./TaskReportTable";
import SolutionIdDisplay from "./SolutionIdDisplay";

export default function SetCompletedPage() {
  const searchParams = useSearchParams();
  const [solution, setSolution] = useState<TaskSetSolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const navState = window.history.state?.usr || window.history.state?.state;
    if (navState && navState.solution) {
      setSolution(navState.solution);
      setLoading(false);
      return;
    }

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
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        height: "100vh",
        backgroundColor: "#f6fff6",
      }}
    >
      <div style={{ maxWidth: 960, padding: 24 }}>
        <h1 style={{ color: "#28a745", fontSize: "2.5rem", marginBottom: 24 }}>Success!</h1>
        <p style={{ color: "#333", marginBottom: 16 }}>Your solution was saved successfully. You find your participant ID below.</p>
        {!error && solution ? (
          <>
            <SolutionIdDisplay uuid={solution.uuid} />
            <p style={{ color: "#333", marginBottom: 16 }}>Here you can review your answers:</p>
            <TaskReportTable answers={solution.answers} />
          </>
        ) : (
          <div style={{ color: "#dc3545", marginBottom: 16 }}>{error}</div>
        )}
      </div>
    </div>
  );
}
