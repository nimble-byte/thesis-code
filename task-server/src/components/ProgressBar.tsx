import React from 'react';

interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  className?: string;
}

export default function ProgressBar({ currentStep, totalSteps, className }: ProgressBarProps) {
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <div className={className} style={{ maxWidth: 480, margin: '16px auto 24px auto', padding: '0 16px' }}>
      <div style={{
        width: '100%',
        height: 8,
        backgroundColor: '#f0f0f0',
        borderRadius: 4,
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progressPercentage}%`,
          height: '100%',
          backgroundColor: '#0070f3',
          transition: 'width 0.3s ease',
          borderRadius: 4
        }} />
      </div>
    </div>
  );
}
