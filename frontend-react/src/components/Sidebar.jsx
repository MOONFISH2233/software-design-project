import React from 'react';
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
