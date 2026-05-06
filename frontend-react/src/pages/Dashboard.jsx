import React, { useState, useEffect } from 'react';
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
