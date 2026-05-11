import React from 'react';
import { FaCalendarAlt, FaExternalLinkAlt } from 'react-icons/fa';

const APPOINTMENTS_URL = 'https://smart-healthcare-appointment-system.streamlit.app';

const Appointments: React.FC = () => (
  <main className="min-h-screen bg-gray-100 p-6">
    <div className="mx-auto max-w-7xl">
      <section className="card mb-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center gap-3 rounded-full bg-blue-50 px-4 py-2 text-blue-700">
              <FaCalendarAlt />
              <span className="font-bold">Smart Healthcare Appointment System</span>
            </div>
            <h1 className="text-3xl font-black">المواعيد والحجوزات</h1>
            <p className="mt-3 max-w-2xl text-gray-600">
              هذه الصفحة تربط نظام EHR الحالي بنظام ترتيب المواعيد الخارجي لربط الطبيب بالمريض وتنظيم الحجوزات.
            </p>
          </div>
          <a
            href={APPOINTMENTS_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-bold text-white hover:bg-blue-700"
          >
            فتح نظام المواعيد <FaExternalLinkAlt />
          </a>
        </div>
      </section>

      <section className="card">
        <div className="mb-4 flex flex-col justify-between gap-3 md:flex-row md:items-center">
          <div>
            <h2 className="text-2xl font-black">عرض نظام المواعيد داخل EHR</h2>
            <p className="text-gray-500">إذا لم يظهر التطبيق هنا، استخدم زر الفتح في تبويب جديد.</p>
          </div>
          <span className="rounded-full bg-yellow-100 px-3 py-1 text-sm font-bold text-yellow-800">
            ربط خارجي بدون مزامنة بيانات
          </span>
        </div>

        <div className="overflow-hidden rounded-2xl border bg-white">
          <iframe
            title="Smart Healthcare Appointment System"
            src={APPOINTMENTS_URL}
            className="h-[720px] w-full"
          />
        </div>
      </section>
    </div>
  </main>
);

export default Appointments;
