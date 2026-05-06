#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
React前端项目完整代码生成器
参考zhencaitang-site项目结构
"""

import os
import json

BASE_DIR = r"d:\学习\软件设计\frontend-react"

def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)

def write_file(filepath, content):
    """写入文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {os.path.relpath(filepath, BASE_DIR)}")

# 创建目录结构
dirs = [
    "src",
    "src/components",
    "src/pages",
    "src/stores",
    "src/api",
    "src/utils",
    "src/styles",
    "src/hooks",
    "public"
]

for d in dirs:
    ensure_dir(os.path.join(BASE_DIR, d))

print("🚀 开始生成React项目...\n")

# ========== 1. Vite配置 ==========
write_file(os.path.join(BASE_DIR, "vite.config.js"), """import { defineConfig } from 'vite'
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
""")

# ========== 2. Tailwind配置 ==========
write_file(os.path.join(BASE_DIR, "tailwind.config.js"), """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366f1',
        secondary: '#8b5cf6',
      }
    },
  },
  plugins: [],
}
""")

# ========== 3. PostCSS配置 ==========
write_file(os.path.join(BASE_DIR, "postcss.config.js"), """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")

# ========== 4. index.html ==========
write_file(os.path.join(BASE_DIR, "index.html"), """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>智能皮肤健康监测</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

# ========== 5. main.jsx ==========
write_file(os.path.join(BASE_DIR, "src/main.jsx"), """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""")

# ========== 6. CSS样式 ==========
write_file(os.path.join(BASE_DIR, "src/styles/index.css"), """@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
""")

# ========== 7. API模块 ==========
write_file(os.path.join(BASE_DIR, "src/api/index.js"), """import axios from 'axios';

const api = axios.create({
  baseURL: '/api/miniprogram',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
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
""")

# ========== 8. 用户状态管理 ==========
write_file(os.path.join(BASE_DIR, "src/stores/userStore.js"), """import { create } from 'zustand';

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
""")

# ========== 9. Sidebar组件 ==========
write_file(os.path.join(BASE_DIR, "src/components/Sidebar.jsx"), """import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, Smartphone, Droplets, Wind, 
  FileText, Bell, Users, User, LogOut 
} from 'lucide-react';
import { useUserStore } from '../stores/userStore';

const menuItems = [
  { path: '/', icon: LayoutDashboard, label: '仪表板' },
  { path: '/devices', icon: Smartphone, label: '设备管理' },
  { path: '/skin-data', icon: Droplets, label: '皮肤数据' },
  { path: '/environment', icon: Wind, label: '环境数据' },
  { path: '/reports', icon: FileText, label: '健康报告' },
  { path: '/notifications', icon: Bell, label: '通知中心' },
  { path: '/community', icon: Users, label: '社区互动' },
  { path: '/profile', icon: User, label: '个人资料' },
];

export default function Sidebar() {
  const location = useLocation();
  const logout = useUserStore((state) => state.logout);

  return (
    <aside className="w-72 bg-white shadow-xl h-screen fixed left-0 top-0 overflow-y-auto">
      {/* Logo区域 */}
      <div className="p-8 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
        <h1 className="text-2xl font-bold">皮肤健康监测</h1>
        <p className="text-sm opacity-90 mt-2">Smart Skin Monitor</p>
      </div>
      
      {/* 导航菜单 */}
      <nav className="py-4">
        {menuItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                className={`flex items-center px-6 py-4 cursor-pointer transition-all mx-2 rounded-lg mb-1 ${
                  isActive 
                    ? 'bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-600 border-l-4 border-indigo-600' 
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <item.icon className="w-5 h-5 mr-3" />
                <span className="font-medium">{item.label}</span>
              </motion.div>
            </Link>
          );
        })}
        
        {/* 退出登录 */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={logout}
          className="w-full flex items-center px-6 py-4 text-gray-600 hover:bg-red-50 hover:text-red-600 transition-colors mx-2 rounded-lg mt-4"
        >
          <LogOut className="w-5 h-5 mr-3" />
          <span className="font-medium">退出登录</span>
        </motion.button>
      </nav>
    </aside>
  );
}
""")

# ========== 10. Login页面 ==========
write_file(os.path.join(BASE_DIR, "src/pages/Login.jsx"), """import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api';
import { useUserStore } from '../stores/userStore';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    phone: '',
    nickname: ''
  });
  const navigate = useNavigate();
  const setUser = useUserStore((state) => state.setUser);
  const setToken = useUserStore((state) => state.setToken);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isLogin) {
        const response = await api.post('/user/login', {
          username: formData.username,
          password: formData.password
        });
        
        if (response.success) {
          setUser(response.user);
          setToken(response.token);
          navigate('/');
        }
      } else {
        const response = await api.post('/user/register', formData);
        if (response.success) {
          alert('注册成功！请登录');
          setIsLogin(true);
        }
      }
    } catch (error) {
      alert(error.response?.data?.message || '操作失败');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative overflow-hidden">
      {/* 动态背景 */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)',
          backgroundSize: '50px 50px',
          animation: 'moveGrid 20s linear infinite'
        }}></div>
      </div>
      
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white/95 backdrop-blur-lg rounded-3xl shadow-2xl p-10 w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
            {isLogin ? '欢迎回来' : '创建账号'}
          </h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">用户名</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="请输入用户名"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">密码</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="请输入密码"
              required
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">手机号</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入手机号"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">昵称（可选）</label>
                <input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => setFormData({...formData, nickname: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入昵称"
                />
              </div>
            </>
          )}

          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            {isLogin ? '登 录' : '注 册'}
          </motion.button>
        </form>

        <p className="text-center mt-6 text-gray-600">
          {isLogin ? '还没有账号？' : '已有账号？'}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-indigo-600 hover:text-indigo-700 font-semibold ml-2 transition-colors"
          >
            {isLogin ? '立即注册' : '去登录'}
          </button>
        </p>
      </motion.div>
    </div>
  );
}
""")

# ========== 11. Dashboard页面 ==========
write_file(os.path.join(BASE_DIR, "src/pages/Dashboard.jsx"), """import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Smartphone, Wifi, Droplets, Bell } from 'lucide-react';
import api from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    deviceCount: 0,
    onlineCount: 0,
    dataCount: 0,
    notificationCount: 0
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const devicesRes = await api.get('/device/list');
      const devices = devicesRes.devices || [];
      
      const statsRes = await api.get('/data/statistics?days=7');
      const statistics = statsRes.statistics || [];
      
      const notifRes = await api.get('/notification/list?is_read=false&page=1&per_page=1');
      
      setStats({
        deviceCount: devices.length,
        onlineCount: devices.filter(d => d.status === 'online').length,
        dataCount: statistics.reduce((sum, s) => sum + (s.total_records || 0), 0),
        notificationCount: notifRes.pagination?.total || 0
      });

      if (statistics.length > 0) {
        const formatted = statistics.map(s => ({
          date: s.stat_date,
          moisture: s.avg_moisture || 0,
          oiliness: s.avg_oiliness || 0
        })).reverse();
        setChartData(formatted);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  const statCards = [
    { title: '绑定设备', value: stats.deviceCount, icon: Smartphone, color: 'from-indigo-500 to-purple-600' },
    { title: '在线设备', value: stats.onlineCount, icon: Wifi, color: 'from-emerald-500 to-teal-600' },
    { title: '数据记录', value: stats.dataCount, icon: Droplets, color: 'from-blue-500 to-cyan-600' },
    { title: '未读通知', value: stats.notificationCount, icon: Bell, color: 'from-amber-500 to-orange-600' }
  ];

  return (
    <div className="space-y-8">
      {/* 标题 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-4xl font-bold text-gray-800">仪表板</h1>
          <p className="text-gray-600 mt-2">欢迎使用智能皮肤健康监测系统</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={loadDashboardData}
          className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all"
        >
          刷新数据
        </motion.button>
      </motion.div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.05, y: -5 }}
            className="bg-white rounded-2xl shadow-lg p-6 cursor-pointer border-t-4"
            style={{ borderTopColor: card.color.includes('indigo') ? '#6366f1' : card.color.includes('emerald') ? '#10b981' : card.color.includes('blue') ? '#3b82f6' : '#f59e0b' }}
          >
            <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-4 shadow-lg`}>
              <card.icon className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-gray-600 text-sm font-medium mb-2">{card.title}</h3>
            <p className="text-4xl font-bold text-gray-800">{card.value}</p>
          </motion.div>
        ))}
      </div>

      {/* 图表区域 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-2xl shadow-lg p-8"
      >
        <h2 className="text-2xl font-bold mb-6 text-gray-800">最近7天皮肤数据趋势</h2>
        {loading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
          </div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: 'none', 
                  borderRadius: '12px',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }} 
              />
              <Legend />
              <Line type="monotone" dataKey="moisture" stroke="#6366f1" name="水分(%)" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="oiliness" stroke="#10b981" name="油性(%)" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-80 flex items-center justify-center text-gray-500">
            暂无数据
          </div>
        )}
      </motion.div>
    </div>
  );
}
""")

print("\n" + "="*60)
print("🎉 React项目基础框架生成完成！")
print("="*60)
print("\n接下来需要:")
print("1. cd frontend-react")
print("2. npm install")
print("3. npm run dev")
print("\n访问: http://localhost:3000")
