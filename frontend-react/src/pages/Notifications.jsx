import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, Check, Filter, Trash2 } from 'lucide-react';
import api from '../api';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterRead, setFilterRead] = useState('all');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadNotifications();
  }, [filterRead, filterType]);

  const loadNotifications = async () => {
    try {
      const res = await api.get('/notification/list?page=1&per_page=50');
      let data = res.data?.items || [];
      
      if (filterRead !== 'all') {
        const isRead = filterRead === 'read';
        data = data.filter(n => n.is_read === isRead);
      }
      
      if (filterType !== 'all') {
        data = data.filter(n => n.notification_type === filterType);
      }
      
      setNotifications(data);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.put(`/notification/${id}/read`);
      loadNotifications();
    } catch (error) {
      console.error('标记已读失败:', error);
    }
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'system': return '🔧';
      case 'device': return '📱';
      case 'report': return '📊';
      default: return '🔔';
    }
  };

  const getTypeLabel = (type) => {
    switch(type) {
      case 'system': return '系统';
      case 'device': return '设备';
      case 'report': return '报告';
      default: return '其他';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">通知中心</h1>
            <p className="text-gray-600">查看系统消息和提醒</p>
          </div>
          <div className="flex space-x-3">
            <select 
              value={filterRead}
              onChange={(e) => setFilterRead(e.target.value)}
              className="px-4 py-2 bg-white rounded-lg shadow border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">全部</option>
              <option value="unread">未读</option>
              <option value="read">已读</option>
            </select>
            <select 
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 bg-white rounded-lg shadow border border-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">全部类型</option>
              <option value="system">系统</option>
              <option value="device">设备</option>
              <option value="report">报告</option>
            </select>
          </div>
        </motion.div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notif, index) => (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border ${notif.is_read ? 'border-white/50' : 'border-indigo-200'} hover:shadow-xl transition-all`}
              >
                <div className="flex items-start space-x-4">
                  <div className="text-3xl">{getTypeIcon(notif.notification_type)}</div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className={`font-semibold ${notif.is_read ? 'text-gray-800' : 'text-indigo-600'}`}>
                          {notif.title || '通知'}
                        </h3>
                        <span className="inline-block mt-1 px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                          {getTypeLabel(notif.notification_type)}
                        </span>
                      </div>
                      {!notif.is_read && (
                        <button
                          onClick={() => markAsRead(notif.id)}
                          className="px-3 py-1 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200 transition-colors flex items-center space-x-1"
                        >
                          <Check className="w-4 h-4" />
                          <span className="text-sm">标记已读</span>
                        </button>
                      )}
                    </div>
                    <p className="text-gray-600 mb-2">{notif.content || '暂无内容'}</p>
                    <p className="text-xs text-gray-500">{notif.created_at?.substring(0, 19)}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {notifications.length === 0 && !loading && (
          <div className="text-center py-20">
            <Bell className="w-20 h-20 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500 text-lg">暂无通知消息</p>
          </div>
        )}
      </div>
    </div>
  );
}
