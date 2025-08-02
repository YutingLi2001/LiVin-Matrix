import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DataEntryPage from './pages/DataEntryPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* 默认路由重定向到仪表盘 */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 登录页面 */}
            <Route path="/login" element={<LoginPage />} />

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
