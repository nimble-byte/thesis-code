"use client";

import React, { useEffect, useState } from 'react';
import TaskComponent from '@/components/TaskComponent';
import type { Question } from '@/types/question';

enum TaskPageStatus {
  LOADING = 'loading',
  ERROR = 'error',
  READY = 'ready',
}

export default function TaskPage(props: { params: Promise<{ index: string }> }) {
  const params = React.use(props.params);
  const { index } = params;
  const [question, setQuestion] = useState<Question | null>(null);
  const [status, setStatus] = useState<TaskPageStatus>(TaskPageStatus.LOADING);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!index) return;
    setStatus(TaskPageStatus.LOADING);
    fetch(`/api/questions/${index}`)
      .then(res => res.json())
      .then(data => {
        setQuestion(data);
        setStatus(TaskPageStatus.READY);
      })
      .catch(err => {
        setError('Failed to load question');
        setStatus(TaskPageStatus.ERROR);
      });
  }, [index]);

  if (status === TaskPageStatus.LOADING) return <div>Loading...</div>;
  if (status === TaskPageStatus.ERROR) return <div>{error}</div>;
  if (!question) return <div>No question found.</div>;

  return <TaskComponent question={question} />;
}
