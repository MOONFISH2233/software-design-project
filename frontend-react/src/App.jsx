import { BrowserRouter } from 'react-router-dom';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import { useUserStore } from './stores/userStore';

// 占位页面组件
const PlaceholderPage = ({ title }) => (
  <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center">
    <div className="text-center">
      <h2 className="text-4xl font-bold text-gray-800 mb-4">{title}</h2>
      <p className="text-gray-600">页面开发中...</p>
    </div>
  </div>
);

function ProtectedRoute({ children }) {
  const token = useUserStore((state) => state.token);
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 登录页面 */}
        <Route path="/login" element={<Login />} />
        
        {/* 受保护的路由 - 官网风格 */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Routes>
                <Route index element={<Dashboard />} />
                <Route path="devices" element={<PlaceholderPage title="设备管理" />} />
                <Route path="skin-data" element={<PlaceholderPage title="皮肤数据" />} />
                <Route path="environment" element={<PlaceholderPage title="环境数据" />} />
                <Route path="reports" element={<PlaceholderPage title="健康报告" />} />
                <Route path="notifications" element={<PlaceholderPage title="通知中心" />} />
                <Route path="community" element={<PlaceholderPage title="社区互动" />} />
                <Route path="profile" element={<PlaceholderPage title="个人资料" />} />
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
