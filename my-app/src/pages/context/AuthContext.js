import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [authData, setAuthData] = useState(null);
  const [loading, setLoading] = useState(true);

  const getCSRFToken = () => {
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
  };

  const fetchCSRFToken = async () => {
    try {
      await axios.get('http://localhost:8000/api/csrf/', { withCredentials: true });
    } catch (error) {
      console.error('CSRF token fetch failed:', error);
    }
  };

  const login = async (credentials) => {
    try {
      await fetchCSRFToken(); // Ensure CSRF token is set
      const response = await axios.post('http://localhost:8000/api/login_view/', credentials, {
        withCredentials: true,
        headers: { 'X-CSRFToken': getCSRFToken() }
      });
      setAuthData(response.data);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await fetchCSRFToken();
      await axios.post('http://localhost:8000/api/logout/', {}, {
        withCredentials: true,
        headers: { 'X-CSRFToken': getCSRFToken() }
      });
      setAuthData(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const checkAuth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/check-auth/', { withCredentials: true });
      if (response.data.authenticated) setAuthData(response.data.user);
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { checkAuth(); }, []);

  return (
    <AuthContext.Provider value={{ authData, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
