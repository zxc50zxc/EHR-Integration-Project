import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import LoadingState from '../../components/LoadingState';
import { api } from '../../services/api';
import { Medication } from '../../types';

const PrescriptionInvoice: React.FC = () => {
  const { medicationId } = useParams();
  const [medication, setMedication] = useState<Medication | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!medicationId) return;
    api.get<Medication>(`/medications/${medicationId}`)
      .then((res) => setMedication(res.data))
      .catch(() => setMedication(null))
      .finally(() => setLoading(false));
  }, [medicationId]);

  if (loading) return <LoadingState />;

  if (!medication) {
    return (
      <main className="min-h-screen bg-gray-100 p-6">
        <section className="card mx-auto max-w-3xl">
          <h1 className="text-2xl font-black">الوصفة غير موجودة</h1>
          <Link to="/patient/medications" className="mt-4 inline-block font-bold text-blue-600">العودة للأدوية</Link>
        </section>
      </main>
    );
  }

  const prescriptionNumber = `RX-${String(medication.id).padStart(6, '0')}`;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-3xl">
        <div className="mb-4 flex justify-between print:hidden">
          <Link to="/patient/medications" className="font-bold text-blue-600">العودة للأدوية</Link>
          <button onClick={() => window.print()} className="btn-primary">طباعة للصيدلي</button>
        </div>

        <section className="rounded-2xl bg-white p-8 shadow print:shadow-none">
          <div className="mb-8 border-b pb-6 text-center">
            <p className="text-sm font-bold text-blue-700">EHR Integration Prescription</p>
            <h1 className="text-3xl font-black">فاتورة / وصفة دوائية</h1>
            <p className="mt-2 text-xl font-black text-green-700">{prescriptionNumber}</p>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <p className="text-gray-500">رقم المريض</p>
              <p className="text-lg font-bold">{medication.patient_id}</p>
            </div>
            <div>
              <p className="text-gray-500">رقم الطبيب</p>
              <p className="text-lg font-bold">{medication.practitioner_id}</p>
            </div>
            <div>
              <p className="text-gray-500">الدواء</p>
              <p className="text-lg font-bold">{medication.drug_name}</p>
            </div>
            <div>
              <p className="text-gray-500">الجرعة</p>
              <p className="text-lg font-bold">{medication.dosage}</p>
            </div>
            <div>
              <p className="text-gray-500">التكرار</p>
              <p className="text-lg font-bold">{medication.frequency}</p>
            </div>
            <div>
              <p className="text-gray-500">طريقة الاستخدام</p>
              <p className="text-lg font-bold">{medication.route}</p>
            </div>
            <div>
              <p className="text-gray-500">تاريخ البداية</p>
              <p className="text-lg font-bold">{medication.start_date}</p>
            </div>
            <div>
              <p className="text-gray-500">الحالة</p>
              <p className="text-lg font-bold">{medication.status}</p>
            </div>
          </div>

          {medication.indication && (
            <div className="mt-6 rounded-xl bg-gray-50 p-4">
              <p className="text-gray-500">السبب الطبي</p>
              <p className="text-lg font-bold">{medication.indication}</p>
            </div>
          )}

          <div className="mt-8 border-t pt-6 text-sm text-gray-500">
            <p>يرجى تقديم رقم الوصفة للصيدلي: <span className="font-bold text-gray-900">{prescriptionNumber}</span></p>
            <p>هذه الوصفة صادرة إلكترونياً من نظام السجل الطبي الإلكتروني.</p>
          </div>
        </section>
      </div>
    </main>
  );
};

export default PrescriptionInvoice;
