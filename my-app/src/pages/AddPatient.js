import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AddPatient.css';

function AddPatient() {
  const [patientEmail, setPatientEmail] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [step, setStep] = useState(1); // 1: Enter email, 2: Verify code
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSendVerification = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await axios.post('http://localhost:8000/api/caregiver/send-verification/', {
        patient_email: patientEmail
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setStep(2);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send verification');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyPatient = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await axios.post('http://localhost:8000/api/caregiver/verify-patient/', {
        patient_email: patientEmail,
        verification_code: verificationCode
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      navigate('/caregiver-dashboard', { state: { success: 'Patient added successfully!' } });
    } catch (err) {
      setError(err.response?.data?.message || 'Verification failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="add-patient-container">
      <h2>Add New Patient</h2>
      
      {step === 1 ? (
        <form onSubmit={handleSendVerification} className="patient-form">
          <div className="form-group">
            <label>Patient Email:</label>
            <input
              type="email"
              value={patientEmail}
              onChange={(e) => setPatientEmail(e.target.value)}
              required
              placeholder="Enter patient's registered email"
            />
          </div>
          
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Sending...' : 'Send Verification'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyPatient} className="verification-form">
          <p>We've sent a verification code to {patientEmail}</p>
          
          <div className="form-group">
            <label>Verification Code:</label>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              required
              placeholder="Enter 6-digit code"
            />
          </div>
          
          <div className="button-group">
            <button 
              type="button" 
              className="secondary"
              onClick={() => setStep(1)}
            >
              Back
            </button>
            <button 
              type="submit" 
              disabled={isLoading}
            >
              {isLoading ? 'Verifying...' : 'Verify Patient'}
            </button>
          </div>
        </form>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
}

export default AddPatient;