import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

function PrivateRoute({ children, requiredRole }) {
  const { authData } = useAuth();
  const location = useLocation();

  if (!authData) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole === 'caregiver' && !authData.isCaregiver) {
    return <Navigate to="/dashboard" replace />;
  }

  if (requiredRole === 'patient' && !authData.isPatient) {
    return <Navigate to="/caregiver" replace />;
  }

  return children;
}

export default PrivateRoute;
