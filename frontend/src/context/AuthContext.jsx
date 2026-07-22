import { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';
import { expandWebApp } from '../utils/telegram';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    expandWebApp();

    api('/users/me')
      .then((data) => {
        setUser(data);
      })
      .catch((err) => {
        console.error('Auth failed:', err);
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  const updateUser = (updates) => {
    setUser((prev) => ({ ...prev, ...updates }));
  };

  return (
    <AuthContext.Provider value={{ user, setUser, updateUser, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
