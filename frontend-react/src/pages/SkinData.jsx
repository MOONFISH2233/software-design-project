import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Droplets, Filter, Download } from 'lucide-react';
import api from '../api';

export default function SkinData() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await api.get('/data/list?page=1&per_page=50');
      setData(res.data?.items || []);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">皮肤数据</h1>
            <p className="text-gray-600">查看历史监测记录</p>
          </div>
          <div className="flex space-x-3">
            <button className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-lg transition-all flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <span>筛选</span>
            </button>
            <button className="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center space-x-2">
              <Download className="w-4 h-4" />
              <span>导出</span>
            </button>
          </div>
        </motion.div>

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
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">水分(%)</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">油性(%)</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-600">弹性</th>
                </tr>
              </thead>
              <tbody>
                {data.map((item, index) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                    className="border-t border-gray-100 hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-6 py-4 text-sm text-gray-800">{item.created_at?.substring(0, 19)}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{item.moisture || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{item.oiliness || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-800">{item.elasticity || '-'}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
