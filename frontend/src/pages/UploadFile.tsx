import React, { useState } from 'react';

import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

const UploadFile: React.FC = () => {
  const { user } = useAuth();
  const [patientId, setPatientId] = useState(user?.patient_id?.toString() || '');
  const [documentType, setDocumentType] = useState('general');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const isPatient = user?.role === 'patient';

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setMessage('');
    setError('');
    if (!file) {
      setError('اختر ملفاً أولاً');
      return;
    }
    if (!isPatient && !patientId) {
      setError('رقم المريض مطلوب للطبيب أو الممرضة أو الموظف');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('description', description);
    if (patientId) {
      formData.append('patient_id', patientId);
    }

    setLoading(true);
    try {
      const response = await api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(`تم رفع الملف بنجاح: ${response.data.filename}`);
      setFile(null);
      setDescription('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'تعذر رفع الملف');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-3xl">
        <h1 className="mb-2 text-3xl font-black">رفع ملف طبي</h1>
        <p className="mb-6 text-gray-600">
          استخدم هذه الصفحة لرفع ملفات المرضى، تقارير المختبر، المستندات السريرية، أو ملفات المريض الشخصية.
        </p>

        <form onSubmit={handleSubmit} className="card space-y-4">
          {message && <div className="rounded-lg bg-green-100 p-3 text-green-700">{message}</div>}
          {error && <div className="rounded-lg bg-red-100 p-3 text-red-700">{error}</div>}

          <div>
            <label className="mb-2 block font-bold text-gray-700">رقم المريض</label>
            <input
              className="input"
              value={patientId}
              disabled={isPatient}
              placeholder="مثال: 1"
              onChange={(event) => setPatientId(event.target.value)}
            />
            {isPatient && <p className="mt-1 text-sm text-gray-500">سيتم ربط الملف بسجلك الطبي تلقائياً.</p>}
          </div>

          <div>
            <label className="mb-2 block font-bold text-gray-700">نوع الملف</label>
            <select className="input" value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
              <option value="general">ملف عام</option>
              <option value="lab-report">تقرير مختبر</option>
              <option value="clinical-document">مستند سريري</option>
              <option value="insurance">تأمين</option>
              <option value="patient-upload">ملف من المريض</option>
            </select>
          </div>

          <div>
            <label className="mb-2 block font-bold text-gray-700">وصف مختصر</label>
            <textarea
              className="input"
              rows={4}
              value={description}
              placeholder="مثال: تقرير CBC بتاريخ اليوم"
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>

          <div>
            <label className="mb-2 block font-bold text-gray-700">الملف</label>
            <input
              type="file"
              className="input"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <p className="mt-1 text-sm text-gray-500">الحد الأقصى: 10MB.</p>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
            {loading ? 'جاري الرفع...' : 'رفع الملف'}
          </button>
        </form>
      </div>
    </main>
  );
};

export default UploadFile;
