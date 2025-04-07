import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCSRFToken } from './utils/csrf';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const csrfToken = getCSRFToken();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/login_view/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include', // Needed for cookies/sessions
      });

      const data = await response.json();
    
      if (response.ok && data.user_id) {
        localStorage.setItem('authToken', 'true');  // ✅ Check BOTH status + data
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Login failed');  // Show error
      }
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div>
      <h1>Login</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;