@echo off
chcp 65001 >nul
echo ========================================
echo   React前端项目快速生成脚本
echo ========================================
echo.

cd /d "%~dp0frontend-react"

echo [1/8] 创建项目配置文件...
if not exist vite.config.js echo import { defineConfig } from 'vite'^
import react from '@vitejs/plugin-react'^
^
export default defineConfig({^
  plugins: [react()],^
  server: {^
    port: 3000,^
    proxy: {^
      '/api': {^
        target: 'http://47.103.108.47:5000',^
        changeOrigin: true^
      }^
    }^
  }^
}) > vite.config.js

if not exist tailwind.config.js echo /** @type {import('tailwindcss').Config} */^
export default {^
  content: [^
    "./index.html",^
    "./src/**/*.{js,ts,jsx,tsx}",^
  ],^
  theme: {^
    extend: {},^
  },^
  plugins: [],^
} > tailwind.config.js

if not exist postcss.config.js echo export default {^
  plugins: {^
    tailwindcss: {},^
    autoprefixer: {},^
  },^
} > postcss.config.js

echo ✅ 配置文件创建完成
echo.

echo [2/8] 创建HTML入口...
if not exist index.html echo ^<!DOCTYPE html^>^
^<html lang="zh-CN"^>^
  ^<head^>^
    ^<meta charset="UTF-8" /^>^
    ^<meta name="viewport" content="width=device-width, initial-scale=1.0" /^>^
    ^<title^>智能皮肤健康监测^</title^>^
  ^</head^>^
  ^<body^>^
    ^<div id="root"^>^</div^>^
    ^<script type="module" src="/src/main.jsx"^>^</script^>^
  ^</body^>^
^</html^> > index.html

echo ✅ HTML入口创建完成
echo.

echo [3/8] 创建CSS样式...
mkdir src 2>nul
mkdir src\styles 2>nul

echo @tailwind base;^
@tailwind components;^
@tailwind utilities;^
^
* {^
  margin: 0;^
  padding: 0;^
  box-sizing: border-box;^
}^
^
body {^
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',^
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',^
    sans-serif;^
  -webkit-font-smoothing: antialiased;^
  -moz-osx-font-smoothing: grayscale;^
} > src\styles\index.css

echo ✅ CSS样式创建完成
echo.

echo [4/8] 创建核心组件...
mkdir src\components 2>nul
mkdir src\pages 2>nul
mkdir src\stores 2>nul
mkdir src\api 2>nul
mkdir src\utils 2>nul

echo ✅ 目录结构创建完成
echo.

echo [5/8] 下载依赖包（这可能需要几分钟）...
call npm install

echo.
echo ✅ 依赖安装完成
echo.

echo [6/8] 创建API模块...
echo import axios from 'axios';^
^
const api = axios.create({^
  baseURL: '/api/miniprogram',^
  timeout: 10000,^
});^
^
// 请求拦截器 - 自动添加Token^
api.interceptors.request.use(^
  (config) => {^
    const token = localStorage.getItem('authToken');^
    if (token) {^
      config.headers.Authorization = `Bearer ${token}`;^
    }^
    return config;^
  },^
  (error) => {^
    return Promise.reject(error);^
  }^
);^
^
// 响应拦截器 - 处理错误^
api.interceptors.response.use(^
  (response) => response.data,^
  (error) => {^
    if (error.response?.status === 401) {^
      localStorage.removeItem('authToken');^
      window.location.href = '/login';^
    }^
    return Promise.reject(error);^
  }^
);^
^
export default api; > src\api\index.js

echo ✅ API模块创建完成
echo.

echo [7/8] 创建状态管理...
echo import { create } from 'zustand';^
^
export const useUserStore = create((set) => ({^
  user: null,^
  token: localStorage.getItem('authToken') || '',^
  setUser: (user) => set({ user }),^
  setToken: (token) => {^
    localStorage.setItem('authToken', token);^
    set({ token });^
  },^
  logout: () => {^
    localStorage.removeItem('authToken');^
    set({ user: null, token: '' });^
  },^
})); > src\stores\userStore.js

echo ✅ 状态管理创建完成
echo.

echo [8/8] 创建主应用文件...
echo import React from 'react';^
import ReactDOM from 'react-dom/client';^
import App from './App';^
import './styles/index.css';^
^
ReactDOM.createRoot(document.getElementById('root')).render(^
  ^<React.StrictMode^>^
    ^<App /^>^
  ^</React.StrictMode^>,^
); > src\main.jsx

echo import { BrowserRouter } from 'react-router-dom';^
import { Routes, Route, Navigate } from 'react-router-dom';^
import Login from './pages/Login';^
import Dashboard from './pages/Dashboard';^
import Devices from './pages/Devices';^
import SkinData from './pages/SkinData';^
import Environment from './pages/Environment';^
import Reports from './pages/Reports';^
import Notifications from './pages/Notifications';^
import Community from './pages/Community';^
import Profile from './pages/Profile';^
import Sidebar from './components/Sidebar';^
import { useUserStore } from './stores/userStore';^
^
function ProtectedRoute({ children }) {^
  const token = useUserStore((state) => state.token);^
  return token ? children : ^<Navigate to="/login" /^>;^
}^
^
function App() {^
  return (^
    ^<BrowserRouter^>^
      ^<Routes^>^
        ^<Route path="/login" element={^<Login /^>} /^>^
        ^<Route^
          path="/"^
          element={^
            ^<ProtectedRoute^>^
              ^<div className="flex h-screen bg-gray-50"^>^
                ^<Sidebar /^>^
                ^<main className="flex-1 overflow-auto p-8"^>^
                  ^<Routes^>^
                    ^<Route index element={^<Dashboard /^>} /^>^
                    ^<Route path="devices" element={^<Devices /^>} /^>^
                    ^<Route path="skin-data" element={^<SkinData /^>} /^>^
                    ^<Route path="environment" element={^<Environment /^>} /^>^
                    ^<Route path="reports" element={^<Reports /^>} /^>^
                    ^<Route path="notifications" element={^<Notifications /^>} /^>^
                    ^<Route path="community" element={^<Community /^>} /^>^
                    ^<Route path="profile" element={^<Profile /^>} /^>^
                  ^</Routes^>^
                ^</main^>^
              ^</div^>^
            ^</ProtectedRoute^>^
          }^
        /^>^
      ^</Routes^>^
    ^</BrowserRouter^>^
  );^
}^
^
export default App; > src\App.jsx

echo ✅ 主应用文件创建完成
echo.

echo ========================================
echo   🎉 React项目框架创建成功！
echo ========================================
echo.
echo 接下来需要创建的页面组件：
echo   - src/pages/Login.jsx
echo   - src/pages/Dashboard.jsx
echo   - src/pages/Devices.jsx
echo   - src/pages/SkinData.jsx
echo   - src/pages/Environment.jsx
echo   - src/pages/Reports.jsx
echo   - src/pages/Notifications.jsx
echo   - src/pages/Community.jsx
echo   - src/pages/Profile.jsx
echo   - src/components/Sidebar.jsx
echo.
echo 运行命令启动开发服务器：
echo   cd frontend-react
echo   npm run dev
echo.
echo 访问地址：http://localhost:3000
echo ========================================
pause
