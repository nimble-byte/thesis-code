"use client";
import React from 'react';
import type { Question } from '@/types/question';

interface TaskComponentProps {
  task: Question;
  onAnswerChange?: (selected: string) => void;
  selected?: string | null;
}


export default function TaskComponent({ task, onAnswerChange, selected }: TaskComponentProps) {
  const handleSelectionChange = (value: string) => {
    onAnswerChange?.(value);
  };

  const imageUrl = `/images/${task.image}`;

  return (
    <div
      style={{
        margin: '24px auto',
        padding: 16,
        border: '1px solid #eeeeee',
        borderRadius: 8,
        width: '100%'
      }}
    >
      <h1 style={{ marginBottom: 16, textAlign: 'center', fontSize: '1.5rem' }}>Task: {task.pid}</h1>
      <img src={imageUrl} alt="Task" style={{ objectFit: 'contain', margin: '0 auto 16px auto', display: 'block' }} />
      <h2 style={{ marginBottom: 16 }}>{task.translation}</h2>
      <form>
        {task.choices.map((opt, idx) => (
          <div key={idx} style={{ marginBottom: 8 }}>
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
