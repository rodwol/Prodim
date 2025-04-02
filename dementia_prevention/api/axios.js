import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/', // Your Django API base URL
});

// Add a request interceptor to inject the token
api.interceptors.request.use((config) => {
  const authData = JSON.parse(localStorage.getItem('authData')) || 
                   JSON.parse(sessionStorage.getItem('authData'));
  
  if (authData?.token) {
    config.headers.Authorization = `Token ${authData.token}`;
  }
  
  return config;
});

export default api;
