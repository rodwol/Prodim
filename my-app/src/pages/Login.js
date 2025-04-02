import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from './context/AuthContext';
import './Login.css';

function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [formErrors, setFormErrors] = useState({});
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    // Check if user is already logged in via session
    const checkAuth = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/check-auth/', {
          withCredentials: true
        });

        if (response.data.authenticated) {
          login({
            username: response.data.user.username,
            user_id: response.data.user.id,
            isCaregiver: response.data.is_caregiver,
            isPatient: response.data.is_patient
          });
          navigate('/dashboard', { replace: true });
        }
      } catch (err) {
        console.log('Session check error:', err);
      }
    };

    checkAuth();
  }, [navigate, login]);

  const validateForm = () => {
    const errors = {};
    if (!formData.username.trim()) errors.username = 'Username is required';
    if (!formData.password) errors.password = 'Password is required';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear errors when typing
    if (error) setError('');
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/login_view/',
        {
          username: formData.username,
          password: formData.password
        },
        {
          withCredentials: true,  // Important for session cookies
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // Get CSRF token function needed
          }
        }
      );

      const authData = {
        username: response.data.username,
        user_id: response.data.user_id,
        isCaregiver: response.data.is_caregiver,
        isPatient: response.data.is_patient
      };

      // Store basic user data (without token)
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('userData', JSON.stringify(authData));

      // Update auth context
      login(authData);

      // Navigate to dashboard
      navigate('/dashboard', { replace: true });

    } catch (error) {
      console.error('Login error:', error);

      let errorMessage = 'Login failed. Please try again.';

      if (error.response) {
        if (error.response.status === 400) {
          errorMessage = error.response.data?.detail || 'Invalid username or password';
        } else if (error.response.status === 401) {
          errorMessage = 'Authentication failed';
        } else if (error.response.status === 403) {
          errorMessage = 'Please use the caregiver login';
        }
      }

      setError(errorMessage);
      setFormData(prev => ({ ...prev, password: '' }));

    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to get CSRF token from cookies
  const getCSRFToken = () => {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue;
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && (
        <div className="error-message">
          {error}
          {(error.includes('Invalid') || error.includes('failed')) && (
            <button 
              onClick={() => navigate('/signup')}
              className="text-button"
            >
              Sign up instead?
            </button>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            id="username"
            name="username"
            type="text"
            value={formData.username}
            onChange={handleChange}
            required
            disabled={isLoading}
            autoComplete="username"
            className={formErrors.username ? 'error' : ''}
          />
          {formErrors.username && (
            <span className="field-error">{formErrors.username}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            required
            disabled={isLoading}
            autoComplete="current-password"
            className={formErrors.password ? 'error' : ''}
          />
          {formErrors.password && (
            <span className="field-error">{formErrors.password}</span>
          )}
        </div>

        <div className="remember-me">
          <input
            type="checkbox"
            id="rememberMe"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            disabled={isLoading}
          />
          <label htmlFor="rememberMe">Remember me</label>
        </div>

        <button 
          type="submit" 
          disabled={isLoading || !formData.username || !formData.password}
          className={`login-button ${isLoading ? 'loading' : ''}`}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>
      </form>

      <div className="signup-prompt">
        Don't have an account?{' '}
        <button 
          type="button" 
          onClick={() => navigate('/signup')}
          className="text-button"
          disabled={isLoading}
        >
          Sign up
        </button>
      </div>
    </div>
  );
}

export default Login;