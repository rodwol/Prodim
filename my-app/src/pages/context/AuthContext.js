import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [authData, setAuthData] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/login/', credentials, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': getCSRFToken()
        }
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
      await axios.post('/api/logout/', {}, {
        withCredentials: true,
        headers: {
          'X-CSRFToken': getCSRFToken()
        }
      });
      setAuthData(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/check-auth/', {
        withCredentials: true
      });
      if (response.data.authenticated) {
        setAuthData(response.data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const getCSRFToken = () => {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue;
  };

  return (
    <AuthContext.Provider value={{ 
      authData, 
      login, 
      logout, 
      loading,
      getCSRFToken
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}