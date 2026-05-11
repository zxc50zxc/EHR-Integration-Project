import React, { useEffect, useState } from 'react';

import EmptyState from '../../components/EmptyState';
import LoadingState from '../../components/LoadingState';
import { api } from '../../services/api';
import { SystemUser } from '../../types';

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<SystemUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<SystemUser[]>('/admin/users')
      .then((res) => setUsers(res.data))
      .catch(() => setUsers([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;

  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-6xl">
        <h1 className="mb-6 text-3xl font-black">إدارة المستخدمين</h1>
        <section className="card">
          {users.length === 0 ? (
            <EmptyState title="لا يوجد مستخدمون للعرض" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-right">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">اسم المستخدم</th>
                    <th className="p-3">الاسم</th>
                    <th className="p-3">البريد</th>
                    <th className="p-3">الدور</th>
                    <th className="p-3">Patient ID</th>
                    <th className="p-3">الحالة</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b">
                      <td className="p-3">{user.id}</td>
                      <td className="p-3 font-bold">{user.username}</td>
                      <td className="p-3">{user.full_name}</td>
                      <td className="p-3">{user.email}</td>
                      <td className="p-3">{user.role}</td>
                      <td className="p-3">{user.patient_id || '-'}</td>
                      <td className={`p-3 font-bold ${user.is_active ? 'text-green-600' : 'text-red-600'}`}>
                        {user.is_active ? 'نشط' : 'معطل'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default AdminUsers;
