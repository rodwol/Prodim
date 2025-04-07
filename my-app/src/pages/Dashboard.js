import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const { authData } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);

  const isActive = (path) => {
    return location.pathname === `/dashboard/${path}` || 
           location.pathname.startsWith(`/dashboard/${path}/`);
  };
  // Fetch user dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/dashboard');
        if (response.ok) {
          const data = await response.json();
          setDashboardData(data);
        } else {
          console.error('Error fetching dashboard data');
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchDashboardData();
  }, []);
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
