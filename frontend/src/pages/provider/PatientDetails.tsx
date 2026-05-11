import React, { useEffect, useState } from 'react';
import { FaFileMedical, FaFlask, FaPills } from 'react-icons/fa';
import { Link, useParams } from 'react-router-dom';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import StatusBadge from '../../components/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { ClinicalDocument, FhirPatient, LabTest, Medication } from '../../types';

const PatientDetails: React.FC = () => {
  const { patientId } = useParams();
  const { user } = useAuth();
  const [patient, setPatient] = useState<FhirPatient | null>(null);
  const [documents, setDocuments] = useState<ClinicalDocument[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [tests, setTests] = useState<LabTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyTestId, setBusyTestId] = useState<number | null>(null);

  const loadPatientData = () => {
    if (!patientId) return Promise.resolve();
    return Promise.all([
      api.get<FhirPatient>(`/fhir/Patient/${patientId}`).then((res) => setPatient(res.data)),
      api.get<ClinicalDocument[]>(`/clinical/patient/${patientId}/documents`).then((res) => setDocuments(res.data)).catch(() => setDocuments([])),
      api.get<Medication[]>(`/medications/patient/${patientId}/medications`).then((res) => setMedications(res.data)).catch(() => setMedications([])),
      api.get<LabTest[]>(`/lab/patient/${patientId}/tests`).then((res) => setTests(res.data)).catch(() => setTests([])),
    ]);
  };

  useEffect(() => {
    loadPatientData().finally(() => setLoading(false));
  }, [patientId]);

  const canReviewLab = user?.role === 'physician' || user?.role === 'admin';

  const runLabReviewAction = async (test: LabTest, action: 'verify' | 'release') => {
    setBusyTestId(test.id);
    try {
      await api.post(`/lab/tests/${test.id}/${action}`);
      await loadPatientData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'تعذر تنفيذ الإجراء');
    } finally {
      setBusyTestId(null);
    }
  };

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <section className="card mb-6">
          <h1 className="text-3xl font-black">{patient?.name?.[0]?.given?.[0]} {patient?.name?.[0]?.family}</h1>
          <p className="mt-2 text-gray-500">MRN: {patient?.identifier?.[0]?.value} | DOB: {patient?.birthDate}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link className="btn-primary" to={`/provider/patient/${patientId}/add-document`}>إضافة ملاحظة</Link>
            <Link className="rounded-lg bg-green-600 px-4 py-2 font-bold text-white hover:bg-green-700" to={`/provider/patient/${patientId}/prescribe`}>وصف دواء</Link>
            <Link className="rounded-lg bg-purple-600 px-4 py-2 font-bold text-white hover:bg-purple-700" to={`/provider/patient/${patientId}/order-test`}>طلب اختبار</Link>
          </div>
        </section>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <section className="card">
            <h2 className="mb-4 flex items-center gap-2 text-xl font-black"><FaFileMedical /> الملاحظات</h2>
            {documents.length === 0 ? <EmptyState title="لا توجد ملاحظات" /> : documents.slice(0, 5).map((doc) => (
              <div key={doc.id} className="mb-3 rounded-xl border p-3">
                <p className="font-bold">{doc.title}</p>
                <p className="text-sm text-gray-500">نسخة {doc.version}</p>
              </div>
            ))}
          </section>
          <section className="card">
            <h2 className="mb-4 flex items-center gap-2 text-xl font-black"><FaPills /> الأدوية</h2>
            {medications.length === 0 ? <EmptyState title="لا توجد أدوية" /> : medications.slice(0, 5).map((med) => (
              <div key={med.id} className="mb-3 rounded-xl border p-3">
                <p className="text-xs font-bold text-green-700">RX-{String(med.id).padStart(6, '0')}</p>
                <p className="font-bold">{med.drug_name}</p>
                <p className="text-sm text-gray-500">{med.dosage} - {med.frequency}</p>
              </div>
            ))}
          </section>
          <section className="card">
            <h2 className="mb-4 flex items-center gap-2 text-xl font-black"><FaFlask /> المختبر</h2>
            {tests.length === 0 ? <EmptyState title="لا توجد اختبارات" /> : tests.slice(0, 5).map((test) => (
              <div key={test.id} className="mb-3 rounded-xl border p-3">
                <p className="text-xs font-bold text-purple-700">LAB-{String(test.id).padStart(6, '0')}</p>
                <p className="font-bold">{test.test_name}</p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <StatusBadge value={test.status} />
                  {canReviewLab && test.status === 'completed' && (
                    <button
                      type="button"
                      disabled={busyTestId === test.id}
                      onClick={() => runLabReviewAction(test, 'verify')}
                      className="rounded-lg bg-emerald-600 px-3 py-1 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-50"
                    >
                      اعتماد
                    </button>
                  )}
                  {canReviewLab && test.status === 'verified' && (
                    <button
                      type="button"
                      disabled={busyTestId === test.id}
                      onClick={() => runLabReviewAction(test, 'release')}
                      className="rounded-lg bg-blue-600 px-3 py-1 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                      نشر للمريض
                    </button>
                  )}
                </div>
              </div>
            ))}
            <Link to="/provider/results" className="mt-3 inline-block text-sm font-bold text-purple-700">بحث وإدارة كل اختبارات المختبر</Link>
          </section>
        </div>
      </div>
    </main>
  );
};

export default PatientDetails;
