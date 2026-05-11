import React, { useEffect, useState } from 'react';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import StatusBadge from '../../components/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { LabResult, LabTest } from '../../types';

const PatientLabResults: React.FC = () => {
  const { user } = useAuth();
  const patientId = user?.patient_id || user?.user_id;
  const [tests, setTests] = useState<LabTest[]>([]);
  const [results, setResults] = useState<Record<number, LabResult[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    api.get<LabTest[]>(`/lab/patient/${patientId}/tests`)
      .then(async (res) => {
        setTests(res.data);
        const pairs = await Promise.all(
          res.data.slice(0, 10).map(async (test) => {
            const result = await api.get<LabResult[]>(`/lab/tests/${test.id}/results`).catch(() => ({ data: [] as LabResult[] }));
            return [test.id, result.data] as const;
          }),
        );
        setResults(Object.fromEntries(pairs));
      })
      .catch(() => setTests([]))
      .finally(() => setLoading(false));
  }, [patientId]);

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-3xl font-black">نتائج المختبر</h1>
        {tests.length === 0 ? (
          <section className="card"><EmptyState title="لا توجد نتائج مختبر" /></section>
        ) : (
          <div className="space-y-4">
            {tests.map((test) => (
              <section key={test.id} className="card">
                <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <h2 className="text-2xl font-black">{test.test_name}</h2>
                    <p className="text-gray-500">تاريخ الطلب: {test.order_date}</p>
                  </div>
                  <StatusBadge value={test.status} />
                </div>
                {(results[test.id] || []).length === 0 ? (
                  <p className="text-gray-500">لا توجد نتائج تفصيلية بعد.</p>
                ) : (
                  <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                    {results[test.id].map((result) => (
                      <div key={result.id} className="rounded-xl border p-4">
                        <p className="font-bold">{result.result_name}</p>
                        <p className="text-2xl font-black">{result.result_value} {result.unit}</p>
                        <p className="text-sm text-gray-500">المرجع: {result.reference_range}</p>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            ))}
          </div>
        )}
      </div>
    </main>
  );
};

export default PatientLabResults;
