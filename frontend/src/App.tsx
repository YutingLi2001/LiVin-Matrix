import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import DataEntryPage from './pages/DataEntryPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* 默认路由重定向到登录页 */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* 登录页面 */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* 仪表盘 */}
          <Route path="/dashboard" element={<DashboardPage />} />
          
          {/* 数据录入页面 */}
          <Route path="/data-entry" element={<DataEntryPage />} />
          
          {/* 404 页面 - 重定向到登录页 */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;