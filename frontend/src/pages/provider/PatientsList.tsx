import React, { useEffect, useState } from 'react';
import { FaSearch, FaUserInjured } from 'react-icons/fa';
import { Link } from 'react-router-dom';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import { api } from '../../services/api';
import { FhirPatient } from '../../types';

const PatientsList: React.FC = () => {
  const [patients, setPatients] = useState<FhirPatient[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<FhirPatient[]>('/fhir/Patient?limit=1000')
      .then((res) => setPatients(res.data))
      .catch(() => setPatients([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = patients.filter((patient) => {
    const name = `${patient.name?.[0]?.given?.[0] || ''} ${patient.name?.[0]?.family || ''}`.toLowerCase();
    const mrn = patient.identifier?.[0]?.value?.toLowerCase() || '';
    return name.includes(query.toLowerCase()) || mrn.includes(query.toLowerCase());
  });

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <h1 className="text-3xl font-black">قائمة المرضى</h1>
          <div className="relative w-full md:w-96">
            <FaSearch className="absolute right-3 top-3 text-gray-400" />
            <input className="input pr-10" placeholder="بحث بالاسم أو MRN" value={query} onChange={(e) => setQuery(e.target.value)} />
          </div>
        </div>
        {filtered.length === 0 ? (
          <section className="card">
            <EmptyState title="لا توجد بيانات مرضى للعرض" description="تأكد من أن الـ Backend يعمل وأن حسابك لديه صلاحية عرض المرضى." />
          </section>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((patient) => (
              <Link key={patient.id} to={`/provider/patient/${patient.id}`} className="card transition hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-blue-100 p-4 text-blue-600"><FaUserInjured /></div>
                  <div>
                    <h2 className="text-xl font-black">{patient.name?.[0]?.given?.[0]} {patient.name?.[0]?.family}</h2>
                    <p className="text-gray-500">MRN: {patient.identifier?.[0]?.value}</p>
                    <p className="text-gray-500">تاريخ الميلاد: {patient.birthDate}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
};

export default PatientsList;
