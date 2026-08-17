import React from 'react';

export const SparkleIcon: React.FC<{ className?: string }> = ({ className = 'w-4 h-4 text-goa-yellow' }) => (
  <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
    <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z" />
  </svg>
);
