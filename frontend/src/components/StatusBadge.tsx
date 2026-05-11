import React from 'react';

const colors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  completed: 'bg-blue-100 text-blue-800',
  ordered: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-indigo-100 text-indigo-800',
  assigned: 'bg-indigo-100 text-indigo-800',
  collected: 'bg-orange-100 text-orange-800',
  sample_collected: 'bg-orange-100 text-orange-800',
  received: 'bg-sky-100 text-sky-800',
  verified: 'bg-emerald-100 text-emerald-800',
  released: 'bg-green-100 text-green-800',
  normal: 'bg-green-100 text-green-800',
  abnormal: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
  final: 'bg-purple-100 text-purple-800',
  pending: 'bg-yellow-100 text-yellow-800',
  stopped: 'bg-red-100 text-red-800',
  current: 'bg-sky-100 text-sky-800',
};

const StatusBadge: React.FC<{ value: string }> = ({ value }) => (
  <span className={`rounded-full px-3 py-1 text-sm font-semibold ${colors[value] || 'bg-gray-100 text-gray-700'}`}>
    {value}
  </span>
);

export default StatusBadge;
