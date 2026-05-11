import React, { createContext, useContext, useMemo, useState } from 'react';

import { api } from '../services/api';
import { AuthUser } from '../types';

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  login: (username: string, password: string, remember: boolean) => Promise<AuthUser>;
  register: (payload: {
    username: string;
    email: string;
    full_name: string;
    password: string;
    role: string;
    date_of_birth?: string;
    gender?: string;
    phone?: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const readUser = (): AuthUser | null => {
  const raw = localStorage.getItem('user') || sessionStorage.getItem('user');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
};

const readToken = () => localStorage.getItem('token') || sessionStorage.getItem('token');

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(readUser);
  const [token, setToken] = useState<string | null>(readToken);

  const login = async (username: string, password: string, remember: boolean) => {
    const response = await api.post<AuthUser>('/auth/login', { username, password });
    const storage = remember ? localStorage : sessionStorage;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    storage.setItem('token', response.data.access_token);
    storage.setItem('user', JSON.stringify(response.data));
    setUser(response.data);
    setToken(response.data.access_token);
    return response.data;
  };

  const register: AuthContextValue['register'] = async (payload) => {
    await api.post('/auth/register', payload);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    setUser(null);
    setToken(null);
  };

  const value = useMemo(() => ({ user, token, login, register, logout }), [user, token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return value;
};
