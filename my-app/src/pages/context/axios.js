import axios from 'axios';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
const api = axios.create({
  baseURL: 'http://localhost:8000/api/login_view/',
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const authData = JSON.parse(localStorage.getItem('authData')) || 
                   JSON.parse(sessionStorage.getItem('authData'));
  if (authData?.token) {
    config.headers.Authorization = `Token ${authData.token}`;
  }
  return config;
});

export default api;
