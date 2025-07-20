"use client";
import React from 'react';
import type { Question } from '../types/question';

interface TaskComponentProps {
  question: Question;
  taskNumber?: number;
  onAnswerChange?: (selected: string) => void;
  selected?: string | null;
}


export default function TaskComponent({ question, taskNumber, onAnswerChange, selected }: TaskComponentProps) {
  const handleSelectionChange = (value: string) => {
    onAnswerChange?.(value);
  };

  const imageUrl = `/images/${question.image}`;
  const displayTitle = taskNumber ? `Question ${taskNumber}` : `Question ${question.pid}`;

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 16, border: '1px solid #eeeeee', borderRadius: 8 }}>
      <h1 style={{ marginBottom: 16, textAlign: 'center', fontSize: '1.5rem' }}>{displayTitle}</h1>
      <img src={imageUrl} alt="Task" style={{ width: '100%', objectFit: 'contain', marginBottom: 24 }} />
      <h2 style={{ marginBottom: 16 }}>{question.question}</h2>
      <form>
        {question.choices.map((opt, idx) => (
          <div key={idx} style={{ marginBottom: 12 }}>
            <label>
              <input
                type="radio"
                name="answer"
                value={opt}
                checked={selected === opt}
                onChange={() => handleSelectionChange(opt)}
                style={{ marginRight: 8 }}
              />
              {opt}
            </label>
          </div>
        ))}
      </form>
    </div>
  );
}
