import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { api } from '../../services/api';

const AddDocument: React.FC = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [docType, setDocType] = useState('Note');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await api.post('/clinical/documents', {
        patient_id: Number(patientId),
        document_type: docType,
        title,
        content,
      });
      navigate(`/provider/patient/${patientId}`);
    } catch {
      alert('خطأ في إضافة الملاحظة');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl rounded-2xl bg-white p-8 shadow">
        <h1 className="mb-6 text-3xl font-black">إضافة ملاحظة سريرية</h1>
        <select value={docType} onChange={(e) => setDocType(e.target.value)} className="input mb-4">
          <option value="Note">ملاحظة</option>
          <option value="Report">تقرير</option>
          <option value="Summary">ملخص</option>
        </select>
        <input className="input mb-4" placeholder="عنوان الملاحظة" value={title} onChange={(e) => setTitle(e.target.value)} />
        <textarea className="input mb-6 min-h-52" placeholder="محتوى الملاحظة..." value={content} onChange={(e) => setContent(e.target.value)} />
        <div className="flex gap-4">
          <button disabled={loading} className="btn-primary flex-1">{loading ? 'جاري الحفظ...' : 'حفظ الملاحظة'}</button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary flex-1">إلغاء</button>
        </div>
      </form>
    </main>
  );
};

export default AddDocument;
