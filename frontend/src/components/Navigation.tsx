import React from 'react';
import { FaSignOutAlt } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavigationLinks = () => {
    if (user?.role === 'admin') {
      return (
        <>
          <Link to="/admin/dashboard" className="text-white hover:text-blue-100">الرئيسية</Link>
          <Link to="/admin/users" className="text-white hover:text-blue-100">المستخدمين</Link>
          <Link to="/appointments" className="text-white hover:text-blue-100">المواعيد</Link>
          <Link to="/provider/results" className="text-white hover:text-blue-100">المختبر</Link>
          <Link to="/upload" className="rounded-lg bg-white/15 px-3 py-1 text-white hover:bg-white/25">رفع ملف</Link>
          <Link to="/admin/statistics" className="text-white hover:text-blue-100">الإحصائيات</Link>
          <Link to="/admin/reports" className="text-white hover:text-blue-100">التقارير</Link>
        </>
      );
    }
    if (user?.role === 'lab_technician') {
      return (
        <>
          <Link to="/provider/results" className="text-white hover:text-blue-100">قائمة المختبر</Link>
          <Link to="/upload" className="rounded-lg bg-white/15 px-3 py-1 text-white hover:bg-white/25">رفع ملف</Link>
        </>
      );
    }
    if (user?.role === 'physician' || user?.role === 'nurse' || user?.role === 'staff') {
      return (
        <>
          <Link to="/provider/dashboard" className="text-white hover:text-blue-100">الرئيسية</Link>
          <Link to="/provider/patients" className="text-white hover:text-blue-100">المرضى</Link>
          <Link to="/appointments" className="text-white hover:text-blue-100">المواعيد</Link>
          <Link to="/provider/results" className="text-white hover:text-blue-100">نتائج المختبر</Link>
          <Link to="/upload" className="rounded-lg bg-white/15 px-3 py-1 text-white hover:bg-white/25">رفع ملف</Link>
        </>
      );
    }
    return (
      <>
        <Link to="/patient/dashboard" className="text-white hover:text-blue-100">الرئيسية</Link>
        <Link to="/patient/records" className="text-white hover:text-blue-100">السجل الطبي</Link>
        <Link to="/patient/medications" className="text-white hover:text-blue-100">الأدوية</Link>
        <Link to="/patient/lab-results" className="text-white hover:text-blue-100">المختبر</Link>
        <Link to="/appointments" className="text-white hover:text-blue-100">المواعيد</Link>
        <Link to="/upload" className="rounded-lg bg-white/15 px-3 py-1 text-white hover:bg-white/25">رفع ملف</Link>
      </>
    );
  };

  return (
    <nav className="bg-blue-700 text-white shadow">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:flex-row md:items-center md:justify-between">
        <Link to="/" className="text-xl font-bold">نظام السجل الطبي الإلكتروني</Link>
        <div className="flex flex-wrap items-center gap-4">
          {getNavigationLinks()}
          <span className="rounded-full bg-blue-800 px-3 py-1 text-sm">
            {user?.username} ({user?.role})
          </span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg bg-red-600 px-3 py-2 text-sm font-bold hover:bg-red-700"
          >
            <FaSignOutAlt /> تسجيل الخروج
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
