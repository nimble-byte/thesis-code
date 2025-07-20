"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import TaskComponent from "@/components/TaskComponent";
import ProgressBar from "@/components/ProgressBar";
import PrimaryButton from "@/components/PrimaryButton";
import type { Question } from "@/types/question";
import type { TaskAnswer } from "@/types/solution";

enum TaskSetUIStatus {
  LOADING = "loading",
  ERROR = "error",
  IN_PROGRESS = "inProgress",
  SUBMITTING = "submitting",
}

export default function TaskSetPage(props: { params: Promise<{ setId: string }> }) {
  const router = useRouter();
  const params = React.use(props.params);
  const { setId } = params;
  const [status, setStatus] = useState<TaskSetUIStatus>(TaskSetUIStatus.LOADING);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [givenAnswer, setGivenAnswer] = useState<string | null>(null);
  const [solutionAnswers, setSolutionAnswers] = useState<TaskAnswer[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!setId) return;
    setStatus(TaskSetUIStatus.LOADING);
    fetch(`/api/sets/${setId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setQuestions(data);
          setStatus(TaskSetUIStatus.IN_PROGRESS);
        } else {
          setStatus(TaskSetUIStatus.ERROR);
          setSubmitError(data.error || "Failed to load task set");
        }
      })
      .catch((err) => {
        setStatus(TaskSetUIStatus.ERROR);
        setSubmitError("Failed to load task set");
      });
  }, [setId]);

  const handleNextTask = () => {
    const currentQuestion = questions[currentTaskIndex];
    if (!givenAnswer) return;
    setSolutionAnswers((prev) => [
      ...prev,
      {
        pid: currentQuestion.pid,
        givenAnswer: givenAnswer,
        correctAnswer: currentQuestion.answer,
        timestamp: new Date().toISOString(),
      },
    ]);
    setGivenAnswer(null);
    if (currentTaskIndex < questions.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
    }
  };

  const handleSubmitSolution = async () => {
    if (status === TaskSetUIStatus.SUBMITTING || !givenAnswer) return;
    const currentQuestion = questions[currentTaskIndex];
    // Add last answer
    const allAnswers = [
      ...solutionAnswers,
      {
        pid: currentQuestion.pid,
        givenAnswer: givenAnswer,
        correctAnswer: currentQuestion.answer,
        timestamp: new Date().toISOString(),
      },
    ];
    setStatus(TaskSetUIStatus.SUBMITTING);
    setSubmitError(null);
    try {
      const solution = {
        setId,
        answers: allAnswers,
        uuid: crypto.randomUUID(),
        completedAt: new Date().toISOString(),
      };
      const res = await fetch("/api/solutions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(solution),
      });
      if (!res.ok) throw new Error((await res.json()).error || "Failed to save solution");
      setSolutionAnswers([]);
      router.push("/sets/completed");
    } catch (err: any) {
      setSubmitError(err.message || "Failed to save solution");
      setStatus(TaskSetUIStatus.IN_PROGRESS);
    }
  };

  const handleAnswerChange = (value: string) => {
    setGivenAnswer(value);
  };

  if (status === TaskSetUIStatus.LOADING) return <div>Loading task set...</div>;
  if (status === TaskSetUIStatus.ERROR) return <div>{submitError}</div>;
  if (questions.length === 0) return <div>No tasks found in this set.</div>;

  const currentQuestion = questions[currentTaskIndex];
  const isLastTask = currentTaskIndex === questions.length - 1;

  return (
    <div style={{ position: "relative", minHeight: "100vh" }}>
      {/* Progress bar */}
      <ProgressBar currentStep={currentTaskIndex + 1} totalSteps={questions.length} />

      {/* Current task */}
      <TaskComponent
        question={currentQuestion}
        taskNumber={currentTaskIndex + 1}
        onAnswerChange={handleAnswerChange}
        selected={givenAnswer}
      />

      {/* Navigation button */}
      {!isLastTask && (
        <PrimaryButton
          onClick={handleNextTask}
          disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}
          style={{ position: "fixed", bottom: "2rem", right: "2rem" }}
        >
          Next Task →
        </PrimaryButton>
      )}

      {/* Submit button for last task */}
      {isLastTask && (
        <PrimaryButton
          onClick={handleSubmitSolution}
          disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}
          style={{ position: "fixed", bottom: "2rem", right: "2rem" }}
        >
          {status === TaskSetUIStatus.SUBMITTING ? "Saving..." : "Submit Solution"}
        </PrimaryButton>
      )}

      {/* Success message removed: now handled by redirect */}

      {/* Error message */}
      {isLastTask && submitError && (
        <div
          style={{
            position: "fixed",
            bottom: "5.5rem",
            right: "2rem",
            padding: "12px 24px",
            backgroundColor: "#dc3545",
            color: "white",
            borderRadius: "8px",
            fontSize: "1rem",
            fontWeight: "bold",
          }}
        >
          {submitError}
        </div>
      )}
    </div>
  );
}
