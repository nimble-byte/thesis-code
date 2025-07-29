"use client";

import React, { useEffect, useState } from "react";

import SolutionIdDisplay from "@/components/SolutionIdDisplay";
import { TaskSetSolution } from "@/types/solution";
import TaskReportTable from "../_components/TaskReportTable";

export default function SolutionPage(props: { params: Promise<{ uuid: string }> }) {
  const params = React.use(props.params);
  const { uuid } = params;
  const [solution, setSolution] = useState<TaskSetSolution | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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
  }, [uuid]);

  if (loading) {
    return <div style={{ maxWidth: 480, margin: "24px auto", padding: 16 }}>Loading...</div>;
  }
  if (error) {
    return <div style={{ maxWidth: 480, margin: "24px auto", padding: 16 }}>{error}</div>;
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        height: "100vh",
      }}
    >
      <div style={{ maxWidth: 960, padding: 24 }}>
        <h1 style={{ color: "#333333", fontSize: "2.5rem", marginBottom: 24 }}>Solution Report</h1>
        <p style={{ color: "#333333", marginBottom: 16 }}>Your participant ID is:</p>
        {solution && (
          <>
            <SolutionIdDisplay uuid={solution.uuid} />
            <p style={{ color: "#333333", marginBottom: 16 }}>Here you can review your answers:</p>
            <TaskReportTable answers={solution.answers} />
          </>
        )}
      </div>
    </div>
  );
}
