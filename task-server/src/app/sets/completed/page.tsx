"use client";
import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import TaskReportTable from "./TaskReportTable";
import SolutionIdDisplay from "./SolutionIdDisplay";
import { TaskSetSolution } from "@/types/solution";

function SolutionDetails() {
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
    return null;
  }
  if (error) {
    return <div style={{ color: "#dc3545", marginBottom: 16 }}>{error}</div>;
  }
  if (!solution) {
    return null;
  }
  return (
    <>
      <SolutionIdDisplay uuid={solution.uuid} />
      <p style={{ color: "#333", marginBottom: 16 }}>Here you can review your answers:</p>
      <TaskReportTable answers={solution.answers} />
    </>
  );
}

export default function SetCompletedPage() {
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
        <p style={{ color: "#333", marginBottom: 16 }}>
          If you just completed a task set, your solution has been stored successfully. You find your participant ID
          below.
        </p>
        <Suspense fallback={<div style={{ textAlign: "center", marginTop: 48 }}>Loading deatils...</div>}>
          <SolutionDetails />
        </Suspense>
      </div>
    </div>
  );
}
