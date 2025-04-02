import React from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
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

function App() {
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

            {/* Dashboard Route with Nested Routes */}
            <Route path="/dashboard/*" element={<Dashboard />}>
              <Route path="cognitive-test" element={<CognitiveTest />} />
              <Route path="lifestyle-tracker" element={<LifestyleTracker />} />
              <Route path="lifestyle-history" element={<LifestyleHistory />} />
              <Route path="caregiver-view" element={<CaregiverDashboard />} />
              <Route path="healthcare-professionals" element={<HealthcareProfessionals />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
