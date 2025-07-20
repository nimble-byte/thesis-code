"use client";
import React, { useEffect, useState } from 'react';
import TaskComponent from '@/components/TaskComponent';
import type { Question } from '@/types/question';

export default function TaskPage(props: { params: Promise<{ index: string }> }) {
  const params = React.use(props.params);
  const { index } = params;
  const [question, setQuestion] = useState<Question | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!index) return;
    fetch(`/api/questions/${index}`)
      .then(res => res.json())
      .then(data => {
        setQuestion(data);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load question');
        setLoading(false);
      });
  }, [index]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!question) return <div>No question found.</div>;

  return <TaskComponent question={question} />;
}
