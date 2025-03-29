import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios'; // Import axios
import './Login.css';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8000/api/login/', {
        username,
        password,
      });
      if (response.status === 200) {
        onLogin(true); // Notify parent component that login was successful
        navigate('/dashboard'); // Redirect to dashboard
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.response?.status === 400) {
        // If credentials are invalid, redirect to the sign-up page
        alert('Invalid credentials. Redirecting to sign up...');
        navigate('/signup');
      } else {
        alert('An error occurred. Please try again.');
      }
    }
  };

  return (
    <div className="login-container">
      <h2>LOGIN</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
          <div className="remember-me">
            <input type="checkbox" className="remember" />
            <label htmlFor="remember">Remember me</label>
          </div>
      </form>
      <p>
        Don't have an account?{' '}
        <button onClick={() => navigate('/signup')}>Sign Up</button>
      </p>
    </div>
  );
}

export default Login;