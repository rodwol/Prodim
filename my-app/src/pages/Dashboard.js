import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import './Dashboard.css';

function Dashboard() {
  const location = useLocation();
  const { authData } = useAuth();

  const isActive = (path) => {
    return location.pathname === `/dashboard/${path}` || 
           location.pathname.startsWith(`/dashboard/${path}/`);
  };

  return (
    <div className="dashboard">
      <h2>Health Dashboard</h2>
      <nav className="dashboard-nav">
        <Link to="/dashboard/cognitive-test" className={isActive('cognitive-test') ? 'active' : ''}>
          Cognitive Test
        </Link>
        <Link to="/dashboard/lifestyle-tracker" className={isActive('lifestyle-tracker') ? 'active' : ''}>
          Lifestyle Tracker
        </Link>
        <Link to="/dashboard/lifestyle-history" className={isActive('lifestyle-history') ? 'active' : ''}>
          History
        </Link>
        <Link to="/dashboard/healthcare-professionals" className={isActive('healthcare-professionals') ? 'active' : ''}>
          Healthcare Professionals
        </Link>
        {authData?.isCaregiver && (
          <Link to="/dashboard/caregiver-view" className={isActive('caregiver-view') ? 'active' : ''}>
            Caregiver Portal
          </Link>
        )}
      </nav>
      
      {/* Outlet will render the current selected route */}
      <div className="dashboard-content">
        <Outlet />
      </div>
    </div>
  );
}

export default Dashboard;
