import React, { useState } from 'react';
import { FaHeartbeat } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const rolePath = {
  admin: '/admin/dashboard',
  physician: '/provider/patients',
  nurse: '/provider/dashboard',
  staff: '/provider/dashboard',
  lab_technician: '/provider/results',
  patient: '/patient/dashboard',
};

const Login: React.FC = () => {
  const [username, setUsername] = useState('admin1');
  const [password, setPassword] = useState('password123');
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password, remember);
      navigate(rolePath[user.role] || '/patient/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'تعذر تسجيل الدخول');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-slate-900 px-4 py-10">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-8 md:grid-cols-2">
        <div className="text-white">
          <div className="mb-6 inline-flex items-center gap-3 rounded-full bg-white/10 px-4 py-2 backdrop-blur">
            <FaHeartbeat className="text-2xl" />
            <span>Enterprise EHR Integration</span>
          </div>
          <h1 className="text-4xl font-black leading-tight md:text-6xl">نظام السجل الطبي الإلكتروني</h1>
          <p className="mt-6 max-w-xl text-lg text-blue-100">
            بوابات متكاملة للأطباء والمرضى والإداريين، متصلة مباشرة بواجهة FastAPI وموارد FHIR.
          </p>
          <div className="mt-8 rounded-2xl bg-white/10 p-5 text-sm backdrop-blur">
            <p className="font-bold">حسابات تجريبية:</p>
            <p>admin1: إدارة النظام وتحميل التقارير</p>
            <p>doctor1: الطبيب المسؤول عن اعتماد ونشر نتائج المختبر</p>
            <p>labtech1: فني المختبر المسؤول عن استلام الطلب وكتابة النتائج</p>
            <p>nurse1: ممرضة تستطيع رفع ملفات ومتابعة المرضى والمختبر</p>
            <p>patient1: بوابة المريض ورفع ملفاته الشخصية</p>
            <p>كلمة المرور: password123</p>
          </div>
        </div>

        <form onSubmit={handleLogin} className="rounded-3xl bg-white p-8 shadow-2xl">
          <h2 className="mb-2 text-center text-3xl font-black text-gray-900">تسجيل الدخول</h2>
          <p className="mb-8 text-center text-gray-500">ادخل بياناتك للوصول إلى البوابة المناسبة</p>

          {error && <div className="mb-4 rounded-lg bg-red-100 p-3 text-red-700">{error}</div>}

          <label className="mb-2 block font-semibold text-gray-700">اسم المستخدم</label>
          <input className="input mb-4" value={username} onChange={(event) => setUsername(event.target.value)} />

          <label className="mb-2 block font-semibold text-gray-700">كلمة المرور</label>
          <input
            type="password"
            className="input mb-4"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <label className="mb-6 flex items-center gap-2 text-gray-600">
            <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            تذكرني
          </label>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'جاري الدخول...' : 'دخول'}
          </button>

          <p className="mt-6 text-center text-gray-600">
            ليس لديك حساب؟{' '}
            <Link to="/register" className="font-bold text-blue-600 hover:text-blue-700">
              إنشاء حساب
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Login;
