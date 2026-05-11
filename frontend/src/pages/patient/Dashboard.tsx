import React, { useEffect, useState } from 'react';
import { FaCalendar, FaFlask, FaPills, FaUser } from 'react-icons/fa';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import StatusBadge from '../../components/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { FhirPatient, LabTest, Medication } from '../../types';

const PatientDashboard: React.FC = () => {
  const { user } = useAuth();
  const patientId = user?.patient_id || user?.user_id;
  const [patient, setPatient] = useState<FhirPatient | null>(null);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [labTests, setLabTests] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!patientId) return;
    Promise.all([
      api.get<FhirPatient>(`/fhir/Patient/${patientId}`).then((res) => setPatient(res.data)).catch(() => setPatient(null)),
      api.get<Medication[]>(`/medications/patient/${patientId}/medications`).then((res) => setMedications(res.data)).catch(() => setMedications([])),
      api.get<LabTest[]>(`/lab/patient/${patientId}/tests`).then((res) => setLabTests(res.data)).catch(() => setLabTests([])),
    ]).finally(() => setLoading(false));
  }, [patientId]);

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-8 text-4xl font-black text-gray-800">لوحة التحكم - المريض</h1>

        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
          <div className="card flex items-center gap-4">
            <FaUser className="text-4xl text-blue-500" />
            <div>
              <p className="text-gray-500">الاسم</p>
              <p className="text-xl font-black">{patient?.name?.[0]?.given?.[0] || user?.username} {patient?.name?.[0]?.family}</p>
            </div>
          </div>
          <div className="card">
            <p className="text-gray-500">المعرف الطبي</p>
            <p className="text-2xl font-black">{patient?.identifier?.[0]?.value || '-'}</p>
          </div>
          <div className="card">
            <p className="text-gray-500">تاريخ الميلاد</p>
            <p className="text-2xl font-black">{patient?.birthDate || '-'}</p>
          </div>
          <div className="card flex items-center gap-4">
            <FaCalendar className="text-4xl text-orange-500" />
            <div>
              <p className="text-gray-500">المواعيد</p>
              <p className="text-2xl font-black">قريباً</p>
            </div>
          </div>
        </div>

        <section className="card mb-8">
          <h2 className="mb-4 flex items-center gap-3 text-2xl font-black"><FaPills className="text-green-500" /> الأدوية الحالية</h2>
          {medications.length === 0 ? (
            <EmptyState title="لا توجد أدوية حالية" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-right">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3">اسم الدواء</th>
                    <th className="p-3">الجرعة</th>
                    <th className="p-3">التكرار</th>
                    <th className="p-3">الحالة</th>
                    <th className="p-3">تاريخ البداية</th>
                  </tr>
                </thead>
                <tbody>
                  {medications.slice(0, 6).map((med) => (
                    <tr key={med.id} className="border-b hover:bg-gray-50">
                      <td className="p-3 font-bold">{med.drug_name}</td>
                      <td className="p-3">{med.dosage}</td>
                      <td className="p-3">{med.frequency}</td>
                      <td className="p-3"><StatusBadge value={med.status} /></td>
                      <td className="p-3">{med.start_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="card">
          <h2 className="mb-4 flex items-center gap-3 text-2xl font-black"><FaFlask className="text-purple-500" /> نتائج المختبر</h2>
          {labTests.length === 0 ? (
            <EmptyState title="لا توجد اختبارات مختبر" />
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {labTests.slice(0, 6).map((test) => (
                <div key={test.id} className="rounded-xl border p-4">
                  <h3 className="text-lg font-black">{test.test_name}</h3>
                  <p className="text-gray-600">التاريخ: {test.order_date}</p>
                  <div className="mt-3"><StatusBadge value={test.status} /></div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default PatientDashboard;
