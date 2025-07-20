import React from 'react';

export default function SetCompletedPage() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: '#f6fff6',
    }}>
      <h1 style={{ color: '#28a745', fontSize: '2.5rem', marginBottom: '1rem' }}>Success!</h1>
      <p style={{ fontSize: '1.2rem', color: '#333' }}>
        Your solution was saved successfully.
      </p>
    </div>
  );
}
