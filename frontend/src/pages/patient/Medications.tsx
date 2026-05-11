import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import StatusBadge from '../../components/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { Medication } from '../../types';

const PatientMedications: React.FC = () => {
  const { user } = useAuth();
  const patientId = user?.patient_id || user?.user_id;
  const [medications, setMedications] = useState<Medication[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    api.get<Medication[]>(`/medications/patient/${patientId}/medications`)
      .then((res) => setMedications(res.data))
      .catch(() => setMedications([]))
      .finally(() => setLoading(false));
  }, [patientId]);

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-3xl font-black">الأدوية</h1>
        <section className="card">
          {medications.length === 0 ? (
            <EmptyState title="لا توجد أدوية" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-right">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3">الدواء</th>
                    <th className="p-3">الجرعة</th>
                    <th className="p-3">التكرار</th>
                    <th className="p-3">الحالة</th>
                    <th className="p-3">تاريخ البداية</th>
                    <th className="p-3">الوصفة</th>
                  </tr>
                </thead>
                <tbody>
                  {medications.map((med) => (
                    <tr key={med.id} className="border-b">
                      <td className="p-3 font-bold">{med.drug_name}</td>
                      <td className="p-3">{med.dosage}</td>
                      <td className="p-3">{med.frequency}</td>
                      <td className="p-3"><StatusBadge value={med.status} /></td>
                      <td className="p-3">{med.start_date}</td>
                      <td className="p-3">
                        <Link
                          to={`/patient/medications/${med.id}/invoice`}
                          className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-bold text-white hover:bg-blue-700"
                        >
                          RX-{String(med.id).padStart(6, '0')} / طباعة
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default PatientMedications;
