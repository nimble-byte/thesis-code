"use client";
import React, { useEffect, useState } from 'react';
import type { Question } from '../../../types/question';

export default function TaskPage(props: { params: Promise<{ index: string }> }) {
  const params = React.use(props.params);
  const { index } = params;
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
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

  const imageUrl = `/images/${question.image}`;
  const options = question.choices;

  return (
    <div style={{ maxWidth: 500, margin: '2rem auto', padding: 16, border: '1px solid #eee', borderRadius: 8 }}>
      <img src={imageUrl} alt="Task" style={{ width: '100%', objectFit: 'contain', marginBottom: 24 }} />
      <h2 style={{ marginBottom: 16 }}>{question.question}</h2>
      <form>
        {options.map((opt, idx) => (
          <div key={idx} style={{ marginBottom: 12 }}>
            <label>
              <input
                type="radio"
                name="answer"
                value={opt}
                checked={selected === opt}
                onChange={() => setSelected(opt)}
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
