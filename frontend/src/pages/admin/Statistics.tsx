import React from 'react';

const Statistics: React.FC = () => (
  <main className="min-h-screen bg-gray-100 p-6">
    <div className="mx-auto max-w-6xl">
      <h1 className="mb-6 text-3xl font-black">الإحصائيات</h1>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <section className="card">
          <p className="text-gray-500">جاهزية النظام</p>
          <p className="mt-2 text-4xl font-black text-green-600">99.9%</p>
        </section>
        <section className="card">
          <p className="text-gray-500">FHIR APIs</p>
          <p className="mt-2 text-4xl font-black text-blue-600">نشطة</p>
        </section>
        <section className="card">
          <p className="text-gray-500">Audit Trail</p>
          <p className="mt-2 text-4xl font-black text-purple-600">مفعل</p>
        </section>
      </div>
    </div>
  </main>
);

export default Statistics;
