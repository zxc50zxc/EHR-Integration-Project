import React from 'react';

const LoadingState: React.FC<{ label?: string }> = ({ label = 'جاري التحميل...' }) => (
  <div className="flex min-h-[240px] items-center justify-center">
    <div className="rounded-2xl bg-white px-6 py-4 text-gray-600 shadow-sm">{label}</div>
  </div>
);

export default LoadingState;
