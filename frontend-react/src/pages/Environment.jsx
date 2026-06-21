import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wind, Thermometer, Droplets, Cloud, Filter, Download } from 'lucide-react';
import api from '../api';

export default function Environment() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterDays, setFilterDays] = useState(7);

  useEffect(() => {
    loadData();
  }, [filterDays]);

  const loadData = async () => {
    try {
      const res = await api.get(`/environment/list?days=${filterDays}&page=1&per_page=50`);
      setData(res.data?.items || []);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  const getPM25Badge = (pm25) => {
    if (!pm25) return { text: '-', color: 'bg-gray-100 text-gray-600' };
    if (pm25 <= 35) return { text: '优', color: 'bg-green-100 text-green-600' };
    if (pm25 <= 75) return { text: '良', color: 'bg-yellow-100 text-yellow-600' };
    return { text: '差', color: 'bg-red-100 text-red-600' };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">环境数据监测</h1>
            <p className="text-gray-600">实时监测温度、湿度、空气质量等环境指标</p>
          </div>
          <div className="flex space-x-3">
            <select 
              value={filterDays}
              onChange={(e) => setFilterDays(Number(e.target.value))}
              className="px-4 py-2 bg-white rounded-lg shadow border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value={7}>最近7天</option>
              <option value={30}>最近30天</option>
              <option value={90}>最近90天</option>
            </select>
            <button className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>导出</span>
            </button>
          </div>
        </motion.div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: '平均温度', value: data.length > 0 ? (data.reduce((sum, d) => sum + (d.temperature || 0), 0) / data.length).toFixed(1) : '-', unit: '°C', icon: Thermometer, color: 'from-blue-500 to-cyan-600' },
            { label: '平均湿度', value: data.length > 0 ? (data.reduce((sum, d) => sum + (d.humidity || 0), 0) / data.length).toFixed(1) : '-', unit: '%', icon: Droplets, color: 'from-indigo-500 to-purple-600' },
            { label: '平均PM2.5', value: data.length > 0 ? (data.reduce((sum, d) => sum + (d.pm25 || 0), 0) / data.length).toFixed(0) : '-', unit: '', icon: Cloud, color: 'from-emerald-500 to-teal-600' },
            { label: '平均CO2', value: data.length > 0 ? (data.reduce((sum, d) => sum + (d.co2 || 0), 0) / data.length).toFixed(0) : '-', unit: 'ppm', icon: Wind, color: 'from-amber-500 to-orange-600' }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-white/50"
            >
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center mb-4`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <p className="text-sm text-gray-600 mb-2">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-800">
                {stat.value}<span className="text-lg text-gray-600 ml-1">{stat.unit}</span>
              </p>
            </motion.div>
          ))}
        </div>

        {/* 数据表格 */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : (
          <div className="bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg border border-white/50 overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50/50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">时间</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">温度(°C)</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">湿度(%)</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">PM2.5</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">空气质量</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">CO2(ppm)</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => {
                  const pm25Badge = getPM25Badge(item.pm25);
                  return (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-t border-gray-100 hover:bg-gray-50/50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-800">{item.created_at?.substring(0, 19)}</td>
                      <td className="px-6 py-4 text-sm text-gray-800">{item.temperature || '-'}</td>
                      <td className="px-6 py-4 text-sm text-gray-800">{item.humidity || '-'}</td>
                      <td className="px-6 py-4 text-sm text-gray-800">{item.pm25 || '-'}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${pm25Badge.color}`}>
                          {pm25Badge.text}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-800">{item.co2 || '-'}</td>
                    </motion.tr>
                  );
                })}
              </tbody>
            </table>
            {data.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <Wind className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p>暂无环境数据</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
