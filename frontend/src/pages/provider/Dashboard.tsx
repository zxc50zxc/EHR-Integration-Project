import React, { useEffect, useState } from 'react';
import { FaCalendarAlt, FaFileMedical, FaFlask, FaPills, FaUsers } from 'react-icons/fa';
import { Link } from 'react-router-dom';

import { api } from '../../services/api';
import { FhirPatient } from '../../types';

const ProviderDashboard: React.FC = () => {
  const [patients, setPatients] = useState<FhirPatient[]>([]);

  useEffect(() => {
    api.get<FhirPatient[]>('/fhir/Patient?limit=1000').then((res) => setPatients(res.data)).catch(() => setPatients([]));
  }, []);

  const cards = [
    { label: 'المرضى', value: patients.length, icon: <FaUsers />, color: 'text-blue-500' },
    { label: 'الملاحظات', value: 'FHIR', icon: <FaFileMedical />, color: 'text-emerald-500' },
    { label: 'الأدوية', value: 'Rx', icon: <FaPills />, color: 'text-green-500' },
    { label: 'المختبر', value: 'Lab', icon: <FaFlask />, color: 'text-purple-500' },
    { label: 'المواعيد', value: 'Booking', icon: <FaCalendarAlt />, color: 'text-orange-500' },
  ];

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-8 text-4xl font-black">لوحة الطبيب</h1>
        <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-5">
          {cards.map((card) => (
            <div key={card.label} className="card text-center">
              <div className={`mx-auto mb-3 text-4xl ${card.color}`}>{card.icon}</div>
              <p className="text-gray-500">{card.label}</p>
              <p className="text-3xl font-black">{card.value}</p>
            </div>
          ))}
        </div>
        <section className="card">
          <h2 className="mb-4 text-2xl font-black">إجراءات سريعة</h2>
          <div className="flex flex-wrap gap-3">
            <Link to="/provider/patients" className="btn-primary inline-block">عرض قائمة المرضى</Link>
            <Link to="/appointments" className="rounded-lg bg-orange-600 px-4 py-2 font-bold text-white hover:bg-orange-700">
              فتح نظام المواعيد
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
};

export default ProviderDashboard;
