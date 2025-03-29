import React, { useState } from 'react';
import './App.css';
import { Navigate, BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import Navbar from './pages/Navbar';
import Dashboard from './pages/Dashboard';
import SignUp from './pages/Signup';
import Assessment from './pages/Assessment';
import Services from './pages/Services';
import Login from './pages/Login';
import CognitiveTest from './pages/CognitiveTest';
import LifestyleTracker from './pages/LifestyleTracker';
import HealthcareProfessionals from './pages/HealthcareProfessionals';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Track login status
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" />}>
          {/* Nested routes */}
          <Route path="cognitive-test" element={<CognitiveTest />} />
          <Route path="lifestyle-tracker" element={<LifestyleTracker />} />
          <Route path="healthcare-professionals" element={<HealthcareProfessionals />} />
          {/* Default route (e.g., redirect to cognitive-test) */}
          <Route index element={<Navigate to="cognitive-test" replace />} />
          </Route>
          <Route
          path="/login"
          element={<Login onLogin={(success) => setIsLoggedIn(success)} />}
          />
          <Route path="/signUp" element={<SignUp />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/services" element={<Services />} />
          <Route path="cognitive-test" element={<CognitiveTest />} />
          <Route path="lifestyle-tracker" element={<LifestyleTracker />} />
          <Route path="healthcare-professionals" element={<HealthcareProfessionals />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;