import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import Navigation from './Navigation';
import { useAuth } from '../context/AuthContext';
import { Role } from '../types';

interface ProtectedRouteProps {
  roles?: Role[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ roles }) => {
  const { user, token } = useAuth();

  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }

  if (roles && !roles.includes(user.role)) {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Navigation />
      <Outlet />
    </>
  );
};

export default ProtectedRoute;
