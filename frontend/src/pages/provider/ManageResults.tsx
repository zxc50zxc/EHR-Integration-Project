import React, { useEffect, useState } from 'react';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import StatusBadge from '../../components/StatusBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { LabResult, LabTest } from '../../types';

type WorkflowAction = 'accept' | 'collect' | 'receive' | 'verify' | 'release';

interface ResultForm {
  result_name: string;
  result_value: string;
  unit: string;
  reference_range: string;
  status: string;
}

const emptyResultForm: ResultForm = {
  result_name: '',
  result_value: '',
  unit: '',
  reference_range: '',
  status: 'normal',
};

const sections = [
  { status: 'ordered', title: 'طلبات جديدة' },
  { status: 'accepted', title: 'تم قبولها من المختبر' },
  { status: 'collected', title: 'تم جمع العينة' },
  { status: 'received', title: 'بانتظار إدخال النتائج' },
  { status: 'completed', title: 'بانتظار اعتماد الطبيب' },
  { status: 'verified', title: 'بانتظار النشر للمريض' },
  { status: 'released', title: 'منشورة للمريض' },
];

const ManageResults: React.FC = () => {
  const { user } = useAuth();
  const [tests, setTests] = useState<LabTest[]>([]);
  const [results, setResults] = useState<Record<number, LabResult[]>>({});
  const [resultForms, setResultForms] = useState<Record<number, ResultForm>>({});
  const [loading, setLoading] = useState(true);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [query, setQuery] = useState('');

  const canEnterResults = user?.role === 'lab_technician' || user?.role === 'nurse' || user?.role === 'staff' || user?.role === 'admin';
  const canReviewResults = user?.role === 'physician' || user?.role === 'admin';
  const normalizedQuery = query.trim().toLowerCase();
  const filteredTests = tests.filter((test) => {
    if (!normalizedQuery) return true;
    const labNumber = `lab-${String(test.id).padStart(6, '0')}`.toLowerCase();
    const testResults = results[test.id] || [];
    return [
      labNumber,
      String(test.id),
      `#${test.id}`,
      test.test_name,
      test.test_code,
      test.status,
      String(test.patient_id),
      `patient-${test.patient_id}`,
      `mrn-${test.patient_id}`,
      test.order_date,
      ...testResults.flatMap((result) => [
        result.result_name,
        result.result_value,
        result.unit,
        result.reference_range,
        result.status,
      ]),
    ].some((value) => value?.toLowerCase().includes(normalizedQuery));
  });

  const loadQueue = () => {
    setLoading(true);
    api.get<LabTest[]>('/lab/tests/queue')
      .then(async (res) => {
        setTests(res.data);
        const pairs = await Promise.all(
          res.data.map(async (test) => {
            const result = await api.get<LabResult[]>(`/lab/tests/${test.id}/results`).catch(() => ({ data: [] as LabResult[] }));
            return [test.id, result.data] as const;
          }),
        );
        setResults(Object.fromEntries(pairs));
      })
      .catch(() => setTests([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const runAction = async (test: LabTest, action: WorkflowAction) => {
    setBusyKey(`${action}-${test.id}`);
    try {
      await api.post(`/lab/tests/${test.id}/${action}`);
      loadQueue();
    } finally {
      setBusyKey(null);
    }
  };

  const updateResultForm = (testId: number, key: keyof ResultForm, value: string) => {
    setResultForms((current) => ({
      ...current,
      [testId]: {
        ...(current[testId] || emptyResultForm),
        [key]: value,
      },
    }));
  };

  const submitResult = async (test: LabTest) => {
    const form = resultForms[test.id] || emptyResultForm;
    if (!form.result_name || !form.result_value || !form.unit || !form.reference_range) {
      alert('يرجى إدخال اسم النتيجة والقيمة والوحدة والمجال الطبيعي');
      return;
    }

    setBusyKey(`result-${test.id}`);
    try {
      await api.post(`/lab/tests/${test.id}/results`, form);
      setResultForms((current) => ({ ...current, [test.id]: emptyResultForm }));
      loadQueue();
    } finally {
      setBusyKey(null);
    }
  };

  const actionsFor = (test: LabTest): Array<{ key: WorkflowAction; label: string }> => {
    if (test.status === 'ordered' && canEnterResults) return [{ key: 'accept', label: 'قبول الطلب' }];
    if (test.status === 'accepted' && canEnterResults) return [{ key: 'collect', label: 'تأكيد جمع العينة' }];
    if (test.status === 'collected' && canEnterResults) return [{ key: 'receive', label: 'استلام العينة في المختبر' }];
    if (test.status === 'completed' && canReviewResults) return [{ key: 'verify', label: 'اعتماد النتيجة' }];
    if (test.status === 'verified' && canReviewResults) return [{ key: 'release', label: 'نشر للمريض' }];
    return [];
  };

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-2 text-3xl font-black">إدارة نتائج المختبر</h1>
        <p className="mb-6 text-gray-600">
          الطبيب يطلب التحليل، فني المختبر يقبل الطلب ويجمع العينة ويدخل النتائج، ثم الطبيب يعتمد وينشر للمريض.
        </p>
        <section className="card mb-6">
          <label className="mb-2 block font-bold text-gray-700">بحث سريع عن اختبار أو نتيجة</label>
          <input
            className="input"
            placeholder="ابحث بـ LAB-000102 أو اسم التحليل أو رقم المريض أو قيمة النتيجة"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <p className="mt-2 text-sm text-gray-500">
            النتائج المعروضة: {filteredTests.length} من {tests.length}
          </p>
        </section>
        {tests.length === 0 ? (
          <section className="card"><EmptyState title="لا توجد اختبارات للعرض" /></section>
        ) : filteredTests.length === 0 ? (
          <section className="card"><EmptyState title="لا توجد نتائج مطابقة للبحث" description="جرّب رقم مثل LAB-000102 أو اسم التحليل." /></section>
        ) : sections.map((section) => {
          const sectionTests = filteredTests.filter((test) => test.status === section.status);
          if (sectionTests.length === 0) return null;

          return (
            <section key={section.status} className="card mb-6">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-2xl font-black">{section.title}</h2>
                <span className="rounded-full bg-gray-100 px-3 py-1 text-sm font-bold text-gray-700">{sectionTests.length}</span>
              </div>

              <div className="space-y-4">
                {sectionTests.map((test) => {
                  const form = resultForms[test.id] || emptyResultForm;
                  const testActions = actionsFor(test);
                  const testResults = results[test.id] || [];

                  return (
                    <div key={test.id} className="rounded-xl border p-4">
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="text-xs font-bold text-purple-700">LAB-{String(test.id).padStart(6, '0')}</p>
                          <p className="font-bold">{test.test_name}</p>
                          <p className="text-gray-500">طلب رقم #{test.id} - المريض #{test.patient_id} - {test.order_date}</p>
                        </div>
                        <StatusBadge value={test.status} />
                      </div>

                      <div className="mt-3 grid grid-cols-1 gap-2 text-sm text-gray-600 md:grid-cols-4">
                        <span>الطبيب: {test.practitioner_id}</span>
                        <span>فني المختبر: {test.assigned_to || '-'}</span>
                        <span>مدخل النتائج: {test.resulted_by || '-'}</span>
                        <span>الاعتماد: {test.verified_by || '-'}</span>
                      </div>

                      {testResults.length > 0 && (
                        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                          {testResults.map((result) => (
                            <div key={result.id} className="rounded-lg bg-gray-50 p-3">
                              <p className="font-bold">{result.result_name}</p>
                              <p className="text-xl font-black">{result.result_value} {result.unit}</p>
                              <p className="text-sm text-gray-500">المرجع: {result.reference_range}</p>
                              <StatusBadge value={result.status} />
                            </div>
                          ))}
                        </div>
                      )}

                      {test.status === 'received' && canEnterResults && (
                        <div className="mt-4 rounded-xl bg-blue-50 p-4">
                          <h3 className="mb-3 font-black">إدخال نتيجة المختبر</h3>
                          <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
                            <input className="input" placeholder="اسم النتيجة" value={form.result_name} onChange={(event) => updateResultForm(test.id, 'result_name', event.target.value)} />
                            <input className="input" placeholder="القيمة" value={form.result_value} onChange={(event) => updateResultForm(test.id, 'result_value', event.target.value)} />
                            <input className="input" placeholder="الوحدة" value={form.unit} onChange={(event) => updateResultForm(test.id, 'unit', event.target.value)} />
                            <input className="input" placeholder="المجال الطبيعي" value={form.reference_range} onChange={(event) => updateResultForm(test.id, 'reference_range', event.target.value)} />
                            <select className="input" value={form.status} onChange={(event) => updateResultForm(test.id, 'status', event.target.value)}>
                              <option value="normal">طبيعي</option>
                              <option value="abnormal">غير طبيعي</option>
                              <option value="critical">حرج</option>
                            </select>
                          </div>
                          <button
                            type="button"
                            disabled={busyKey === `result-${test.id}`}
                            onClick={() => submitResult(test)}
                            className="mt-3 rounded-lg bg-green-600 px-4 py-2 text-sm font-bold text-white hover:bg-green-700 disabled:opacity-50"
                          >
                            {busyKey === `result-${test.id}` ? 'جاري الحفظ...' : 'حفظ النتيجة'}
                          </button>
                        </div>
                      )}

                      <div className="mt-4 flex flex-wrap gap-2">
                        {testActions.map((action) => (
                          <button
                            key={action.key}
                            type="button"
                            disabled={busyKey === `${action.key}-${test.id}`}
                            onClick={() => runAction(test, action.key)}
                            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-50"
                          >
                            {busyKey === `${action.key}-${test.id}` ? 'جاري التنفيذ...' : action.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          );
        })}
      </div>
    </main>
  );
};

export default ManageResults;
