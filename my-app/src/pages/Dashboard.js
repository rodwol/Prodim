import React from 'react';
import './Dashboard.css';
import { Routes, Route, Link, useLocation, Outlet } from 'react-router-dom';
import CognitiveTest from './CognitiveTest';
import LifestyleTracker from './LifestyleTracker';
import HealthcareProfessionals from './HealthcareProfessionals';

function Dashboard() {
  const location = useLocation();

  return (
    <div className="dashboard">
      <h2>Health Dashboard</h2>
      <nav className="dashboard-nav">
        <Link
          to="cognitive-test"
          className={location.pathname.includes('cognitive-test') ? 'active' : ''}
        >
          Cognitive Test
        </Link>
        <Link
          to="lifestyle-tracker"
          className={location.pathname.includes('lifestyle-tracker') ? 'active' : ''}
        >
          Lifestyle Tracker
        </Link>
        <Link
          to="healthcare-professionals"
          className={location.pathname.includes('healthcare-professionals') ? 'active' : ''}
        >
          Healthcare Professionals
        </Link>
      </nav>
      <Outlet /> {
          <Routes>
          <Route path="cognitive-test" element={<CognitiveTest />} />
          <Route path="lifestyle-tracker" element={<LifestyleTracker />} />
          <Route path="healthcare-professionals" element={<HealthcareProfessionals />} />
        </Routes>
      }
    </div>
  );
}

export default Dashboard;