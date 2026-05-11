import React, { useState } from 'react';

import { api } from '../../services/api';

const reports = [
  { id: 'compliance', label: 'تقرير الامتثال' },
  { id: 'usage', label: 'تقرير استخدام النظام' },
  { id: 'patients', label: 'تقرير بيانات المرضى' },
  { id: 'lab', label: 'تقرير المختبر' },
];

const Reports: React.FC = () => {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState('');

  const downloadReport = async (reportId: string) => {
    setError('');
    setDownloading(reportId);
    try {
      const response = await api.get(`/admin/reports/${reportId}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${reportId}-report.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      setError('تعذر تحميل التقرير. تأكد من تشغيل الـ Backend وتسجيل الدخول بحساب admin.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-6 text-3xl font-black">التقارير</h1>
        {error && <div className="mb-4 rounded-lg bg-red-100 p-3 text-red-700">{error}</div>}
        <section className="card">
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="flex items-center justify-between rounded-xl border p-4">
                <span className="font-bold">{report.label}</span>
                <button
                  type="button"
                  disabled={downloading === report.id}
                  onClick={() => downloadReport(report.id)}
                  className="btn-primary disabled:opacity-50"
                >
                  {downloading === report.id ? 'جاري التحميل...' : 'تحميل'}
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

export default Reports;
