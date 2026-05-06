import { BrowserRouter } from 'react-router-dom';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import SkinData from './pages/SkinData';
import Environment from './pages/Environment';
import Reports from './pages/Reports';
import Notifications from './pages/Notifications';
import Community from './pages/Community';
import Profile from './pages/Profile';
import { useUserStore } from './stores/userStore';

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
                <Route path="devices" element={<Devices />} />
                <Route path="skin-data" element={<SkinData />} />
                <Route path="environment" element={<Environment />} />
                <Route path="reports" element={<Reports />} />
                <Route path="notifications" element={<Notifications />} />
                <Route path="community" element={<Community />} />
                <Route path="profile" element={<Profile />} />
              </Routes>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
