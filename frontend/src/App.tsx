import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import VerifyEmailPage from './pages/VerifyEmailPage';
import DashboardPage from './pages/DashboardPage';
import DataEntryPage from './pages/DataEntryPage';
import AuthCallback from './components/auth/AuthCallback';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* 默认路由重定向到仪表盘 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 认证相关页面 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />

            {/* GitHub OAuth回调处理 */}
            <Route
              path="/auth/callback"
              element={
                <AuthCallback
                  onSuccess={() => (window.location.href = '/dashboard')}
                  onError={() => (window.location.href = '/login')}
                />
              }
            />

            {/* 受保护的仪表盘 */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute fallback={<Navigate to="/login" replace />}>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* 受保护的数据录入页面 */}
            <Route
              path="/data-entry"
              element={
                <ProtectedRoute fallback={<Navigate to="/login" replace />}>
                  <DataEntryPage />
                </ProtectedRoute>
              }
            />

            {/* 404 页面 - 重定向到仪表盘 */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
