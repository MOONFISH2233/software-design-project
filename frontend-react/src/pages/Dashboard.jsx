import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Smartphone, Wifi, Droplets, Bell, LogOut, ChevronRight, Activity, TrendingUp, Calendar } from 'lucide-react';
import api from '../api';
import { useUserStore } from '../stores/userStore';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [stats, setStats] = useState({
    deviceCount: 0,
    onlineCount: 0,
    dataCount: 0,
    notificationCount: 0
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const navigate = useNavigate();
  const logout = useUserStore((state) => state.logout);
  const user = useUserStore((state) => state.user);

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

  const navItems = [
    { id: 'overview', label: '概览', icon: Activity },
    { id: 'devices', label: '设备', icon: Smartphone },
    { id: 'data', label: '数据', icon: Droplets },
    { id: 'reports', label: '报告', icon: Calendar }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* 顶部导航栏 - 透明玻璃态 */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/50"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              智能皮肤监测
            </h1>
          </div>
          
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${
                  activeTab === item.id 
                    ? 'bg-indigo-100 text-indigo-600' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <item.icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
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

      {/* 主内容区 */}
      <main className="pt-24 pb-12 px-6 max-w-7xl mx-auto">
        {/* Hero区域 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 text-center"
        >
          <h2 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
            欢迎回来，{user?.nickname || user?.username}
          </h2>
          <p className="text-xl text-gray-600">您的皮肤健康数据实时监测中</p>
        </motion.div>

        {/* 统计卡片网格 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { title: '绑定设备', value: stats.deviceCount, icon: Smartphone, color: 'from-indigo-500 to-purple-600', trend: '+12%' },
            { title: '在线设备', value: stats.onlineCount, icon: Wifi, color: 'from-emerald-500 to-teal-600', trend: '98%' },
            { title: '数据记录', value: stats.dataCount, icon: Droplets, color: 'from-blue-500 to-cyan-600', trend: '今日' },
            { title: '未读通知', value: stats.notificationCount, icon: Bell, color: 'from-amber-500 to-orange-600', trend: '新' }
          ].map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -8 }}
              className="bg-white/70 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50 cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-6">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${card.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                  <card.icon className="w-8 h-8 text-white" />
                </div>
                <span className="text-xs font-semibold text-green-600 bg-green-100 px-3 py-1 rounded-full">
                  {card.trend}
                </span>
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-2">{card.title}</h3>
              <p className="text-5xl font-bold text-gray-800">{card.value}</p>
            </motion.div>
          ))}
        </div>

        {/* 图表区域 - 全屏宽度 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/70 backdrop-blur-xl rounded-3xl p-8 shadow-xl border border-white/50 mb-12"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">最近7天皮肤数据趋势</h3>
              <p className="text-gray-600">水分与油性变化分析</p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={loadDashboardData}
              className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2"
            >
              <TrendingUp className="w-5 h-5" />
              <span>刷新数据</span>
            </motion.button>
          </div>
          
          {loading ? (
            <div className="h-96 flex items-center justify-center">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
            </div>
          ) : chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorMoisture" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorOiliness" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: 'none', 
                    borderRadius: '16px',
                    boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                    padding: '12px 16px'
                  }} 
                />
                <Legend />
                <Area type="monotone" dataKey="moisture" stroke="#6366f1" fillOpacity={1} fill="url(#colorMoisture)" name="水分(%)" strokeWidth={3} />
                <Area type="monotone" dataKey="oiliness" stroke="#10b981" fillOpacity={1} fill="url(#colorOiliness)" name="油性(%)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-96 flex items-center justify-center text-gray-500">
              暂无数据
            </div>
          )}
        </motion.div>

        {/* 快捷操作卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { title: '查看设备', desc: '管理您的监测设备', icon: Smartphone, path: '/devices', color: 'from-indigo-500 to-purple-600' },
            { title: '数据分析', desc: '查看详细数据报告', icon: Droplets, path: '/skin-data', color: 'from-blue-500 to-cyan-600' },
            { title: '健康报告', desc: '生成个性化建议', icon: Calendar, path: '/reports', color: 'from-emerald-500 to-teal-600' }
          ].map((item, index) => (
            <motion.div
              key={item.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              whileHover={{ scale: 1.03, y: -5 }}
              onClick={() => navigate(item.path)}
              className="bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-white/50 cursor-pointer group"
            >
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                <item.icon className="w-7 h-7 text-white" />
              </div>
              <h4 className="text-lg font-bold text-gray-800 mb-2">{item.title}</h4>
              <p className="text-gray-600 text-sm mb-4">{item.desc}</p>
              <div className="flex items-center text-indigo-600 font-semibold group-hover:translate-x-2 transition-transform">
                <span>立即查看</span>
                <ChevronRight className="w-5 h-5 ml-1" />
              </div>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
