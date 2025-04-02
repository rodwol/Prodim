import React from 'react';
import { useAuth } from './context/AuthContext';
import axios from 'axios';

function CaregiverDashboard() {
  const { authData } = useAuth();

  const fetchCaregiverData = async () => {
    try {
      const response = await axios.get('/api/caregiver-dashboard/', {
        withCredentials: true
      });
      // Handle response
    } catch (error) {
      console.error('Error fetching caregiver data:', error);
    }
  };

  return (
    <div className="caregiver-dashboard">
      <h3>Caregiver Portal</h3>
      {/* Dashboard content */}
    </div>
  );
}

export default CaregiverDashboard;