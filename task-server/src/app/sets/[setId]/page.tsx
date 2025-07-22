"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import TaskComponent from "@/components/TaskComponent";
import ProgressBar from "@/components/ProgressBar";
import PrimaryButton from "@/components/PrimaryButton";
import ActionBar from "@/components/ActionBar";
import ReplaceTaskDialog from "@/components/ReplaceTaskDialog";
import type { Question } from "@/types/question";
import type { TaskAnswer, TaskSetSolution } from "@/types/solution";

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
  const [showReplaceModal, setShowReplaceModal] = useState(false);

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
      const solution: TaskSetSolution = {
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

  const handleReplaceTaskClick = () => {
    setShowReplaceModal(true);
  };

  const handleReplaceTask = (newTask: Question) => {
    console.log("Replacing task with:", newTask);
    console.log(questions);
    setQuestions((prev) => prev.map((q, idx) => (idx === currentTaskIndex ? newTask : q)));
    console.log(questions);
    setGivenAnswer(null); // reset answer
    setShowReplaceModal(false);
  };

  const handleCloseReplaceModal = () => {
    setShowReplaceModal(false);
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
    <div
      style={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        width: "100%",
        maxWidth: 480,
        margin: "0 auto",
      }}
    >
      {/* Progress bar */}
      <ProgressBar currentStep={currentTaskIndex + 1} totalSteps={questions.length} />

      {/* Current task */}
      <TaskComponent
        question={currentQuestion}
        taskNumber={currentTaskIndex + 1}
        onAnswerChange={handleAnswerChange}
        selected={givenAnswer}
      />

      {/* Error message (above action bar) */}
      {isLastTask && submitError && (
        <div
          style={{
            margin: "16px 0 0 0",
            padding: "16px 24px",
            backgroundColor: "#dc3545",
            color: "white",
            borderRadius: 8,
            fontSize: "1rem",
            fontWeight: "bold",
            alignSelf: "flex-end",
            maxWidth: 400,
          }}
        >
          {submitError}
        </div>
      )}

      {/* Action bar at the bottom of the content */}
      <ActionBar>
        <PrimaryButton onClick={handleReplaceTaskClick}>Replace Task</PrimaryButton>
        {!isLastTask && (
          <PrimaryButton onClick={handleNextTask} disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}>
            Next Task →
          </PrimaryButton>
        )}
        {isLastTask && (
          <PrimaryButton
            onClick={handleSubmitSolution}
            disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}
          >
            {status === TaskSetUIStatus.SUBMITTING ? "Saving..." : "Submit Solution"}
          </PrimaryButton>
        )}
      </ActionBar>
      <ReplaceTaskDialog
        open={showReplaceModal}
        onClose={handleCloseReplaceModal}
        onReplace={handleReplaceTask}
        currentTask={currentQuestion}
      />
    </div>
  );
}
