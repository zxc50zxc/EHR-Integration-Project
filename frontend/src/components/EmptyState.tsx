import React from 'react';

const EmptyState: React.FC<{ title: string; description?: string }> = ({ title, description }) => (
  <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
    <p className="text-lg font-bold text-gray-700">{title}</p>
    {description && <p className="mt-2 text-gray-500">{description}</p>}
  </div>
);

export default EmptyState;
