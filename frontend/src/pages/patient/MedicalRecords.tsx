import React, { useEffect, useState } from 'react';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { ClinicalDocument } from '../../types';

const MedicalRecords: React.FC = () => {
  const { user } = useAuth();
  const patientId = user?.patient_id || user?.user_id;
  const [documents, setDocuments] = useState<ClinicalDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    api.get<ClinicalDocument[]>(`/clinical/patient/${patientId}/documents`)
      .then((res) => setDocuments(res.data))
      .catch(() => setDocuments([]))
      .finally(() => setLoading(false));
  }, [patientId]);

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-6 text-3xl font-black">السجل الطبي</h1>
        <section className="card">
          {documents.length === 0 ? (
            <EmptyState title="لا توجد مستندات سريرية" />
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => (
                <article key={doc.id} className="rounded-xl border p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <h2 className="text-xl font-black">{doc.title}</h2>
                    <span className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700">نسخة {doc.version}</span>
                  </div>
                  <p className="mt-2 text-gray-600">النوع: {doc.document_type}</p>
                  <p className="text-gray-600">التوقيع: {doc.is_signed ? 'موقّع' : 'غير موقّع'}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default MedicalRecords;
