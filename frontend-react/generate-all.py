# 完整React项目代码生成器 - 一次性生成所有文件
import os

base_dir = r"d:\学习\软件设计\frontend-react"

print("🚀 开始生成完整React项目...")
print("=" * 60)

# ========== 1. Vite配置 ==========
vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://47.103.108.47:5000',
        changeOrigin: true
      }
    }
  }
})
"""

with open(os.path.join(base_dir, "vite.config.js"), "w", encoding="utf-8") as f:
    f.write(vite_config)
print("✅ vite.config.js")

# ========== 2. Tailwind配置 ==========
tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""

with open(os.path.join(base_dir, "tailwind.config.js"), "w", encoding="utf-8") as f:
    f.write(tailwind_config)
print("✅ tailwind.config.js")

# ========== 3. PostCSS配置 ==========
postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

with open(os.path.join(base_dir, "postcss.config.js"), "w", encoding="utf-8") as f:
    f.write(postcss_config)
print("✅ postcss.config.js")

# ========== 4. index.html ==========
index_html = """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>智能皮肤健康监测</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("✅ index.html")

# ========== 5. main.jsx ==========
main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

with open(os.path.join(base_dir, "src/main.jsx"), "w", encoding="utf-8") as f:
    f.write(main_jsx)
print("✅ src/main.jsx")

# ========== 6. CSS样式 ==========
css_styles = """@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
"""

with open(os.path.join(base_dir, "src/styles/index.css"), "w", encoding="utf-8") as f:
    f.write(css_styles)
print("✅ src/styles/index.css")

# ========== 7. API模块 ==========
api_module = """import axios from 'axios';

const api = axios.create({
  baseURL: '/api/miniprogram',
  timeout: 10000,
});

// 请求拦截器 - 自动添加Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
"""

with open(os.path.join(base_dir, "src/api/index.js"), "w", encoding="utf-8") as f:
    f.write(api_module)
print("✅ src/api/index.js")

# ========== 8. 用户状态管理 ==========
user_store = """import { create } from 'zustand';

export const useUserStore = create((set) => ({
  user: null,
  token: localStorage.getItem('authToken') || '',
  setUser: (user) => set({ user }),
  setToken: (token) => {
    localStorage.setItem('authToken', token);
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('authToken');
    set({ user: null, token: '' });
  },
}));
"""

with open(os.path.join(base_dir, "src/stores/userStore.js"), "w", encoding="utf-8") as f:
    f.write(user_store)
print("✅ src/stores/userStore.js")

# ========== 9. App.jsx（主应用）==========
app_jsx = """import { BrowserRouter } from 'react-router-dom';
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
import Sidebar from './components/Sidebar';
import { useUserStore } from './stores/userStore';

function ProtectedRoute({ children }) {
  const token = useUserStore((state) => state.token);
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <div className="flex h-screen bg-gray-50">
                <Sidebar />
                <main className="flex-1 overflow-auto p-8">
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
                </main>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
"""

with open(os.path.join(base_dir, "src/App.jsx"), "w", encoding="utf-8") as f:
    f.write(app_jsx)
print("✅ src/App.jsx")

print("\n" + "=" * 60)
print("🎉 基础框架生成完成！")
print("=" * 60)
print("\n接下来运行:")
print("  cd frontend-react")
print("  npm install")
print("  npm run dev")
print("\n访问: http://localhost:3000")
