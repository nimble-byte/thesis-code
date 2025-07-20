"use client";
import React, { useEffect, useState } from 'react';
import TaskComponent from '../../../components/TaskComponent';
import ProgressBar from '../../../components/ProgressBar';
import type { Question } from '../../../types/question';
import type { TaskAnswer } from '../../../types/solution';

export default function TaskSetPage(props: { params: Promise<{ setId: string }> }) {
  const params = React.use(props.params);
  const { setId } = params;
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [givenAnswer, setGivenAnswer] = useState<string | null>(null);
  const [solutionAnswers, setSolutionAnswers] = useState<TaskAnswer[]>([]);

  useEffect(() => {
    if (!setId) return;
    fetch(`/api/sets/${setId}`)
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
  }, [setId]);

  const handleNextTask = () => {
    const currentQuestion = questions[currentTaskIndex];
    if (!givenAnswer) return;
    // Record answer with timestamp and correct answer
    setSolutionAnswers(prev => ([
      ...prev,
      {
        pid: currentQuestion.pid,
        givenAnswer: givenAnswer,
        correctAnswer: currentQuestion.answer,
        timestamp: new Date().toISOString(),
      }
    ]));
    setGivenAnswer(null);
    if (currentTaskIndex < questions.length - 1) {
      setCurrentTaskIndex(currentTaskIndex + 1);
    }
  };

  const handleAnswerChange = (value: string) => {
    setGivenAnswer(value);
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
        selected={givenAnswer}
      />

      {/* Navigation button */}
      {!isLastTask && (
        <button
          onClick={handleNextTask}
          disabled={!givenAnswer}
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            padding: '12px 24px',
            backgroundColor: !givenAnswer ? '#b3c6e6' : '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: 'bold',
            cursor: !givenAnswer ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 12px rgba(0, 112, 243, 0.3)',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => {
            if (givenAnswer) {
              e.currentTarget.style.backgroundColor = '#0051cc';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }
          }}
          onMouseOut={(e) => {
            if (givenAnswer) {
              e.currentTarget.style.backgroundColor = '#0070f3';
              e.currentTarget.style.transform = 'translateY(0)';
            }
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
