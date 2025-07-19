"use client";
import React, { useEffect, useState } from 'react';
import TaskComponent from '../../../components/TaskComponent';
import ProgressBar from '../../../components/ProgressBar';
import type { Question } from '../../../types/question';

export default function TaskSetPage(props: { params: Promise<{ setName: string }> }) {
  const params = React.use(props.params);
  const { setName } = params;
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [answers, setAnswers] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    if (!setName) return;
    fetch(`/api/sets/${setName}`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setQuestions(data);
        } else {
          setError(data.error || 'Failed to load task set');
        }
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load task set');
        setLoading(false);
      });
  }, [setName]);

  const handleNextTask = () => {
    if (currentTaskIndex < questions.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
    }
  };

  const handleAnswerChange = (selected: string) => {
    const currentQuestion = questions[currentTaskIndex];
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.pid]: selected
    }));
  };

  if (loading) return <div>Loading task set...</div>;
  if (error) return <div>{error}</div>;
  if (questions.length === 0) return <div>No tasks found in this set.</div>;

  const currentQuestion = questions[currentTaskIndex];
  const isLastTask = currentTaskIndex === questions.length - 1;

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      {/* Progress bar */}
      <ProgressBar
        currentStep={currentTaskIndex + 1}
        totalSteps={questions.length}
      />

      {/* Current task */}
      <TaskComponent
        question={currentQuestion}
        taskNumber={currentTaskIndex + 1}
        onAnswerChange={handleAnswerChange}
      />

      {/* Navigation button */}
      {!isLastTask && (
        <button
          onClick={handleNextTask}
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            padding: '12px 24px',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0, 112, 243, 0.3)',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.backgroundColor = '#0051cc';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.backgroundColor = '#0070f3';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          Next Task →
        </button>
      )}

      {/* Completion message */}
      {isLastTask && (
        <div style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          padding: '12px 24px',
          backgroundColor: '#28a745',
          color: 'white',
          borderRadius: '8px',
          fontSize: '1rem',
          fontWeight: 'bold',
        }}>
          Set Complete! 🎉
        </div>
      )}
    </div>
  );
}
