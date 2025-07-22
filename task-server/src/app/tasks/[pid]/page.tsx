"use client";

import React, { useEffect, useState } from 'react';
import TaskComponent from '@/components/TaskComponent';
import type { Question } from '@/types/question';

enum TaskPageStatus {
  LOADING = 'loading',
  ERROR = 'error',
  READY = 'ready',
}

export default function TaskPage(props: { params: Promise<{ pid: string }> }) {
  const params = React.use(props.params);
  const { pid } = params;
  const [question, setQuestion] = useState<Question | null>(null);
  const [status, setStatus] = useState<TaskPageStatus>(TaskPageStatus.LOADING);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!pid) return;
    setStatus(TaskPageStatus.LOADING);
    fetch(`/api/tasks/${pid}`)
      .then(res => res.json())
      .then(data => {
        setQuestion(data);
        setStatus(TaskPageStatus.READY);
      })
      .catch(err => {
        setError('Failed to load question');
        setStatus(TaskPageStatus.ERROR);
      });
  }, [pid]);

  if (status === TaskPageStatus.LOADING) return <div style={{ maxWidth: 480, margin: '24px auto', padding: 16 }}>Loading...</div>;
  if (status === TaskPageStatus.ERROR) return <div style={{ maxWidth: 480, margin: '24px auto', padding: 16 }}>{error}</div>;
  if (!question) return <div style={{ maxWidth: 480, margin: '24px auto', padding: 16 }}>No question found.</div>;

  return (
    <div style={{ maxWidth: 480, margin: '24px auto', padding: 16 }}>
      <TaskComponent question={question} />
    </div>
  );
}
