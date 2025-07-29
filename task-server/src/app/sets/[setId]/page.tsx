"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import TaskComponent from "@/components/TaskComponent";
import PrimaryButton from "@/components/PrimaryButton";
import ActionBar from "@/components/ActionBar";
import SecondaryButton from "@/components/SecondaryButton";
import type { Question } from "@/types/question";
import type { TaskAnswer, TaskSetSolution } from "@/types/solution";
import ProgressBar from "../_components/ProgressBar";
import ReplaceTaskDialog from "../_components/ReplaceTaskDialog";

enum TaskSetUIStatus {
  LOADING = "loading",
  ERROR = "error",
  IN_PROGRESS = "inProgress",
  SUBMITTING = "submitting",
}

export default function TaskSetPage(props: {
  params: Promise<{ setId: string }>;
}) {
  const router = useRouter();
  const params = React.use(props.params);
  const { setId } = params;
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [currentTaskStartedAt, setCurrentTaskStartedAt] = useState<Date>(
    new Date()
  );
  const [givenAnswer, setGivenAnswer] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [showReplaceModal, setShowReplaceModal] = useState(false);
  const [solutionAnswers, setSolutionAnswers] = useState<TaskAnswer[]>([]);
  const [status, setStatus] = useState<TaskSetUIStatus>(
    TaskSetUIStatus.LOADING
  );
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!setId) return;
    setStatus(TaskSetUIStatus.LOADING);
    fetch(`/api/sets/${setId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setQuestions(data);
          setCurrentTaskStartedAt(new Date());
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
    if (!givenAnswer) return;

    const currentQuestion = questions[currentTaskIndex];
    const currentTaskAnswer: TaskAnswer = {
      pid: currentQuestion.pid,
      givenAnswer: givenAnswer,
      correctAnswer: currentQuestion.answer,
      question: currentQuestion.question,
      startedAt: currentTaskStartedAt?.toISOString(),
      completedAt: new Date().toISOString(),
    };
    console.log("Current Task Answer:", currentTaskAnswer);
    setSolutionAnswers((prev) => [...prev, currentTaskAnswer]);
    setGivenAnswer(null);
    if (currentTaskIndex < questions.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
      setCurrentTaskStartedAt(new Date());
    }
  };

  const handleSubmitSolution = async () => {
    if (status === TaskSetUIStatus.SUBMITTING || !givenAnswer) return;
    const currentQuestion = questions[currentTaskIndex];
    const currentTaskAnswer: TaskAnswer = {
      pid: currentQuestion.pid,
      givenAnswer: givenAnswer,
      correctAnswer: currentQuestion.answer,
      question: currentQuestion.question,
      startedAt: currentTaskStartedAt?.toISOString(),
      completedAt: new Date().toISOString(),
    };
    // Add last answer
    const allAnswers: TaskAnswer[] = [...solutionAnswers, currentTaskAnswer];
    setStatus(TaskSetUIStatus.SUBMITTING);
    setSubmitError(null);
    const solution: TaskSetSolution = {
      setId,
      answers: allAnswers,
      uuid: crypto.randomUUID(),
      completedAt: new Date().toISOString(),
    };
    console.log("Task Set Solution:", solution);
    try {
      const res = await fetch("/api/solutions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(solution),
      });
      if (!res.ok)
        throw new Error((await res.json()).error || "Failed to save solution");
      setSolutionAnswers([]);
      router.push(`/sets/completed?uuid=${solution.uuid}`);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to save solution");
      setStatus(TaskSetUIStatus.IN_PROGRESS);
    }
  };

  const handleReplaceTaskClick = () => {
    setShowReplaceModal(true);
  };

  const handleReplaceTask = (newTask: Question) => {
    setQuestions((prev) =>
      prev.map((q, idx) => (idx === currentTaskIndex ? newTask : q))
    );
    setCurrentTaskStartedAt(new Date());
    setGivenAnswer(null);
    setShowReplaceModal(false);
  };

  const handleCloseReplaceModal = () => {
    setShowReplaceModal(false);
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
      <ProgressBar
        currentStep={currentTaskIndex + 1}
        totalSteps={questions.length}
      />

      {/* Current task */}
      <TaskComponent
        question={currentQuestion}
        taskNumber={currentTaskIndex + 1}
        onAnswerChange={setGivenAnswer}
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
        <SecondaryButton onClick={handleReplaceTaskClick}>
          Replace Task
        </SecondaryButton>
        {!isLastTask && (
          <PrimaryButton
            onClick={handleNextTask}
            disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}
          >
            Next Task →
          </PrimaryButton>
        )}
        {isLastTask && (
          <PrimaryButton
            onClick={handleSubmitSolution}
            disabled={!givenAnswer || status === TaskSetUIStatus.SUBMITTING}
          >
            {status === TaskSetUIStatus.SUBMITTING
              ? "Saving..."
              : "Submit Solution"}
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
