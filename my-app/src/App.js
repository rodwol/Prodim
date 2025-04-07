import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Navbar from './pages/Navbar';
import Dashboard from './pages/Dashboard';
import CognitiveTest from './pages/CognitiveTest';
import LifestyleTracker from './pages/LifestyleTracker';
import LifestyleHistory from './pages/LifestyleHistory';
import CaregiverDashboard from './pages/CaregiverDashboard';
import HealthcareProfessionals from './pages/HealthcareProfessionals';
import SignUp from './pages/Signup';
import Services from './pages/Services';
import Login from './pages/Login';
import { AuthProvider } from './pages/context/AuthContext';
import { useState } from 'react';

function App() {
  const isAuthenticated = localStorage.getItem('authToken');
  const [authData, setAuthData] = useState(null);

  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/services" element={<Services />} />
            <Route path="/login" element={<Login />} />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
            >
              <Route
                path="cognitive-test"
                element={isAuthenticated ? <CognitiveTest /> : <Navigate to="/login" />}
              />
              <Route
                path="lifestyle-tracker"
                element={isAuthenticated ? <LifestyleTracker /> : <Navigate to="/login" />}
              />
              <Route
                path="lifestyle-history"
                element={isAuthenticated ? <LifestyleHistory /> : <Navigate to="/login" />}
              />
              <Route
                path="healthcare-professionals"
                element={isAuthenticated ? <HealthcareProfessionals /> : <Navigate to="/login" />}
              />
              <Route
                path="caregiver-view"
                element={isAuthenticated && authData?.isCaregiver ? <CaregiverDashboard /> : <Navigate to="/login" />}
              />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;


