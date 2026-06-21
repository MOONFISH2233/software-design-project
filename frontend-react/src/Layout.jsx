import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Smartphone, Droplets, Wind, FileText, Bell, Users, User, LogOut } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUserStore } from '../stores/userStore';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  const logout = useUserStore((state) => state.logout);
  const user = useUserStore((state) => state.user);

  const navItems = [
    { label: '概览', path: '/', icon: Activity },
    { label: '设备', path: '/devices', icon: Smartphone },
    { label: '数据', path: '/skin-data', icon: Droplets },
    { label: '环境', path: '/environment', icon: Wind },
    { label: '报告', path: '/reports', icon: FileText },
    { label: '通知', path: '/notifications', icon: Bell },
    { label: '社区', path: '/community', icon: Users },
    { label: '我的', path: '/profile', icon: User }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* 顶部导航栏 */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              智能皮肤监测
            </h1>
          </div>
          
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <motion.button
                key={item.path}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate(item.path)}
                className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                  location.pathname === item.path 
                    ? 'bg-indigo-100 text-indigo-600' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-indigo-600'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </motion.button>
            ))}
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user?.nickname || user?.username}</span>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => { logout(); navigate('/login'); }}
              className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:shadow-lg transition-all flex items-center space-x-2"
            >
              <LogOut className="w-4 h-4" />
              <span>退出</span>
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* 子页面内容 */}
      {children}
    </div>
  );
}
