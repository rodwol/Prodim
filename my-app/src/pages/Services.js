import React from 'react';
import './Services.css'; // Import the CSS file for styling
import './Layout.js';
function Services() {
  return (
    <div className="services-page">
      {/* Cognitive Assessments Section */}
      <div className="service-section cognitive-assessments">
        <h2>Cognitive Assessments</h2>
        <p>Take AI-driven tests to evaluate your memory, attention, and reasoning.</p>
      </div>

      {/* Health Dashboard Section */}
      <div className="service-section health-dashboard">
        <h2>Health Dashboard</h2>
        <p>Track your brain health score and get personalized recommendations.</p>
      </div>

      {/* Community Support Section */}
      <div className="service-section community-support">
        <h2>Community Support</h2>
        <p>Connect with others and share experiences in a supportive community.</p>
      </div>
    </div>
  );
}

export default Services;