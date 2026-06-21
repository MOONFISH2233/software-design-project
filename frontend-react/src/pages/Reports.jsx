import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Calendar, TrendingUp, CheckCircle, AlertCircle, Eye } from 'lucide-react';
import api from '../api';

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadReports();
  }, [filterType]);

  const loadReports = async () => {
    try {
      const res = await api.get('/report/list?page=1&per_page=50');
      let data = res.data?.items || [];
      if (filterType !== 'all') {
        data = data.filter(r => r.report_type === filterType);
      }
      setReports(data);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (!score) return 'bg-gray-100 text-gray-600';
    if (score >= 80) return 'bg-green-100 text-green-600';
    if (score >= 60) return 'bg-yellow-100 text-yellow-600';
    return 'bg-red-100 text-red-600';
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'daily': return Calendar;
      case 'weekly': return TrendingUp;
      case 'monthly': return FileText;
      default: return FileText;
    }
  };

  const getTypeLabel = (type) => {
    switch(type) {
      case 'daily': return '日报';
      case 'weekly': return '周报';
      case 'monthly': return '月报';
      default: return '报告';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">健康报告</h1>
            <p className="text-gray-600">查看个性化皮肤健康分析报告</p>
          </div>
          <select 
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 bg-white rounded-lg shadow border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">全部类型</option>
            <option value="daily">日报</option>
            <option value="weekly">周报</option>
            <option value="monthly">月报</option>
          </select>
        </motion.div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {reports.map((report, index) => {
              const TypeIcon = getTypeIcon(report.report_type);
              return (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.03, y: -5 }}
                  className="bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-white/50 cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                      <TypeIcon className="w-7 h-7 text-white" />
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getScoreColor(report.score)}`}>
                      {report.score ? `${report.score}分` : '未评分'}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="text-lg font-bold text-gray-800 mb-2">{report.title || '健康报告'}</h3>
                    <p className="text-sm text-gray-600 mb-2">{getTypeLabel(report.report_type)}</p>
                    <p className="text-xs text-gray-500">{report.created_at?.substring(0, 19)}</p>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-gray-700 line-clamp-2">{report.summary || '暂无摘要'}</p>
                    </div>
                    {report.suggestion && (
                      <div className="flex items-start space-x-2">
                        <AlertCircle className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700 line-clamp-2">{report.suggestion}</p>
                      </div>
                    )}
                  </div>

                  <button className="w-full py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center justify-center space-x-2 group-hover:opacity-90">
                    <Eye className="w-4 h-4" />
                    <span>查看详情</span>
                  </button>
                </motion.div>
              );
            })}
          </div>
        )}

        {reports.length === 0 && !loading && (
          <div className="text-center py-20">
            <FileText className="w-20 h-20 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500 text-lg">暂无健康报告</p>
          </div>
        )}
      </div>
    </div>
  );
}
