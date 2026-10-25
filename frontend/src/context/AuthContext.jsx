import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('docverify_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('docverify_token');
      if (savedToken) {
        try {
          const userData = await authApi.getMe();
          setUser(userData);
        } catch (err) {
          localStorage.removeItem('docverify_token');
          localStorage.removeItem('docverify_user');
          setUser(null);
          setToken(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await authApi.login(email, password);
    localStorage.setItem('docverify_token', data.access_token);
    localStorage.setItem('docverify_user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const register = async (fullName, email, password, role = 'USER') => {
    await authApi.register(fullName, email, password, role);
    return await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('docverify_token');
    localStorage.removeItem('docverify_user');
    setToken(null);
    setUser(null);
  };

  const isAdmin = user?.role?.toUpperCase() === 'ADMIN';

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
