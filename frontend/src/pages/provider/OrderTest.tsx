import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { api } from '../../services/api';

const OrderTest: React.FC = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [testName, setTestName] = useState('Complete Blood Count');
  const [testCode, setTestCode] = useState('CBC');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await api.post('/lab/tests/order', {
        patient_id: Number(patientId),
        test_name: testName,
        test_code: testCode,
        order_date: new Date().toISOString().split('T')[0],
      });
      navigate(`/provider/patient/${patientId}`);
    } catch {
      alert('خطأ في طلب الاختبار');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow">
        <h1 className="mb-6 text-3xl font-black">طلب اختبار مختبر</h1>
        <input className="input mb-4" placeholder="اسم الاختبار" value={testName} onChange={(e) => setTestName(e.target.value)} />
        <input className="input mb-6" placeholder="رمز الاختبار" value={testCode} onChange={(e) => setTestCode(e.target.value)} />
        <div className="flex gap-4">
          <button disabled={loading} className="btn-primary flex-1">{loading ? 'جاري الطلب...' : 'طلب الاختبار'}</button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary flex-1">إلغاء</button>
        </div>
      </form>
    </main>
  );
};

export default OrderTest;
