import React, { useEffect, useState } from "react";
import Modal from "@/components/Modal";
import PrimaryButton from "@/components/PrimaryButton";
import SecondaryButton from "@/components/SecondaryButton";
import type { Question } from "@/types/question";

interface ReplaceTaskDialogProps {
  open: boolean;
  onClose: () => void;
  onReplace: (newTask: Question) => void;
  currentTask: Question;
}

export default function ReplaceTaskDialog({ open, onClose, onReplace, currentTask }: ReplaceTaskDialogProps) {
  const [tasks, setTasks] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Question | null>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError(null);
    setSelected(null);
    // Fetch tasks of same difficulty, excluding current
    fetch(`/api/tasks?difficulty=${currentTask.difficulty}&exclude=${currentTask.pid}`)
      .then((res) => res.json())
      .then((data) => {
        setTasks(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load replacement tasks.");
        setLoading(false);
      });
  }, [open, currentTask]);

  const handleReplace = () => {
    if (selected) onReplace(selected);
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      header={<h1>Replace Task</h1>}
      body={
        loading ? (
          <div>Loading tasks...</div>
        ) : error ? (
          <div>{error}</div>
        ) : tasks.length === 0 ? (
          <div>No other tasks available for this difficulty.</div>
        ) : (
          <ul style={{ maxHeight: 240, overflowY: "auto", padding: "0 16px 0 0", margin: 0 }}>
            {tasks.map((task) => (
              <li
                key={task.pid}
                style={{
                  listStyle: "none",
                  marginBottom: 8,
                  padding: 8,
                  border: selected?.pid === task.pid ? "2px solid #0070f3" : "2px solid #eee",
                  borderRadius: 8,
                  cursor: "pointer",
                  background: selected?.pid === task.pid ? "#f0f8ff" : "#fffff",
                }}
                onClick={() => setSelected(task)}
              >
                <div style={{ fontWeight: 600 }}>ID: {task.pid}</div>
                <div style={{ fontSize: "0.9rem", color: "#66666" }}>{task.question}</div>
              </li>
            ))}
          </ul>
        )
      }
      footer={
        <>
          <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
          <PrimaryButton onClick={handleReplace} disabled={!selected}>
            Replace
          </PrimaryButton>
        </>
      }
    />
  );
}
