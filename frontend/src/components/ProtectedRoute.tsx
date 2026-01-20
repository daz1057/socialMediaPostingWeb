import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuthStore } from '@/store/authStore';
import { useCurrentUser } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const location = useLocation();
  const { isAuthenticated, accessToken } = useAuthStore();
  const { isLoading } = useCurrentUser();

  // If no token at all, redirect to login
  if (!accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // If we have a token but still loading user data, show spinner
  if (isLoading) {
    return (
      <div className="tw-flex tw-items-center tw-justify-center tw-min-h-screen">
        <Spin size="large" />
      </div>
    );
  }

  // If authenticated, render children
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // Fallback redirect
  return <Navigate to="/login" state={{ from: location }} replace />;
}
