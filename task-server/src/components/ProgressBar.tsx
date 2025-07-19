import React from 'react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  className?: string;
}

export default function ProgressBar({ currentStep, totalSteps, className }: ProgressBarProps) {
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div className={className} style={{ maxWidth: 500, margin: '1rem auto 2rem auto', padding: '0 16px' }}>
      <div style={{
        width: '100%',
        height: '6px',
        backgroundColor: '#f0f0f0',
        borderRadius: '3px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progressPercentage}%`,
          height: '100%',
          backgroundColor: '#0070f3',
          transition: 'width 0.3s ease',
          borderRadius: '3px'
        }} />
      </div>
    </div>
  );
}
