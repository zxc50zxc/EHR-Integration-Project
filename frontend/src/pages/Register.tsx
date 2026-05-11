import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'patient',
    date_of_birth: '',
    gender: 'unknown',
    phone: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form);
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'تعذر إنشاء الحساب');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <form onSubmit={handleSubmit} className="w-full max-w-lg rounded-3xl bg-white p-8 shadow-xl">
        <h1 className="mb-6 text-center text-3xl font-black">إنشاء حساب جديد</h1>
        {error && <div className="mb-4 rounded-lg bg-red-100 p-3 text-red-700">{error}</div>}
        <div className="grid gap-4">
          <input className="input" placeholder="اسم المستخدم" value={form.username} onChange={(e) => update('username', e.target.value)} />
          <input className="input" placeholder="البريد الإلكتروني" value={form.email} onChange={(e) => update('email', e.target.value)} />
          <input className="input" placeholder="الاسم الكامل" value={form.full_name} onChange={(e) => update('full_name', e.target.value)} />
          <input className="input" type="password" placeholder="كلمة المرور" value={form.password} onChange={(e) => update('password', e.target.value)} />
          <select className="input" value={form.role} onChange={(e) => update('role', e.target.value)}>
            <option value="patient">مريض</option>
            <option value="staff">موظف</option>
            <option value="nurse">ممرض</option>
            <option value="lab_technician">فني مختبر</option>
            <option value="physician">طبيب</option>
          </select>
          {form.role === 'patient' && (
            <>
              <input className="input" type="date" value={form.date_of_birth} onChange={(e) => update('date_of_birth', e.target.value)} />
              <select className="input" value={form.gender} onChange={(e) => update('gender', e.target.value)}>
                <option value="unknown">غير محدد</option>
                <option value="male">ذكر</option>
                <option value="female">أنثى</option>
              </select>
              <input className="input" placeholder="رقم الجوال" value={form.phone} onChange={(e) => update('phone', e.target.value)} />
            </>
          )}
        </div>
        <button disabled={loading} className="btn-primary mt-6 w-full">
          {loading ? 'جاري الإنشاء...' : 'إنشاء الحساب'}
        </button>
        <Link to="/login" className="mt-4 block text-center font-semibold text-blue-600">العودة لتسجيل الدخول</Link>
      </form>
    </div>
  );
};

export default Register;
