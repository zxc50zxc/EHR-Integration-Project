import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { api } from '../../services/api';

const PrescribeMedication: React.FC = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [drugName, setDrugName] = useState('');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState('twice daily');
  const [route, setRoute] = useState('oral');
  const [indication, setIndication] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      await api.post('/medications/prescribe', {
        patient_id: Number(patientId),
        drug_name: drugName,
        dosage,
        frequency,
        route,
        indication,
        start_date: today,
      });
      navigate(`/provider/patient/${patientId}`);
    } catch {
      alert('خطأ في وصف الدواء');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow">
        <h1 className="mb-6 text-3xl font-black">وصف دواء جديد</h1>
        <input className="input mb-4" placeholder="اسم الدواء" value={drugName} onChange={(e) => setDrugName(e.target.value)} />
        <input className="input mb-4" placeholder="الجرعة (مثال: 500mg)" value={dosage} onChange={(e) => setDosage(e.target.value)} />
        <select className="input mb-4" value={frequency} onChange={(e) => setFrequency(e.target.value)}>
          <option value="once daily">مرة يومياً</option>
          <option value="twice daily">مرتين يومياً</option>
          <option value="three times daily">ثلاث مرات يومياً</option>
          <option value="four times daily">أربع مرات يومياً</option>
          <option value="as needed">عند الحاجة</option>
        </select>
        <select className="input mb-4" value={route} onChange={(e) => setRoute(e.target.value)}>
          <option value="oral">فموي</option>
          <option value="injection">حقن</option>
          <option value="topical">موضعي</option>
          <option value="inhalation">استنشاق</option>
        </select>
        <input className="input mb-6" placeholder="السبب" value={indication} onChange={(e) => setIndication(e.target.value)} />
        <div className="flex gap-4">
          <button disabled={loading} className="flex-1 rounded-lg bg-green-600 px-4 py-2 font-bold text-white hover:bg-green-700 disabled:opacity-50">
            {loading ? 'جاري الوصف...' : 'وصف الدواء'}
          </button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary flex-1">إلغاء</button>
        </div>
      </form>
    </main>
  );
};

export default PrescribeMedication;
