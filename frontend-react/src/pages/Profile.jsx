import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, MapPin, Calendar, Edit2, Save } from 'lucide-react';
import api from '../api';
import { useUserStore } from '../stores/userStore';

export default function Profile() {
  const user = useUserStore((state) => state.user);
  const setUser = useUserStore((state) => state.setUser);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    nickname: '',
    phone: '',
    email: '',
    address: ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        nickname: user.nickname || '',
        phone: user.phone || '',
        email: user.email || '',
        address: user.address || ''
      });
    }
  }, [user]);

  const handleSave = async () => {
    try {
      const res = await api.put('/user/profile', formData);
      if (res.success) {
        setUser({ ...user, ...formData });
        setIsEditing(false);
        alert('保存成功');
      }
    } catch (error) {
      console.error('保存失败:', error);
      alert('保存失败');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-3xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">个人资料</h1>
            <p className="text-gray-600">管理您的个人信息</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => isEditing ? handleSave() : setIsEditing(true)}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2"
          >
            {isEditing ? <Save className="w-5 h-5" /> : <Edit2 className="w-5 h-5" />}
            <span>{isEditing ? '保存' : '编辑'}</span>
          </motion.button>
        </motion.div>

        {/* 头像卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/70 backdrop-blur-xl rounded-2xl p-8 shadow-lg border border-white/50 mb-6"
        >
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg">
              {(user?.nickname || user?.username || 'U')[0]}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">{user?.nickname || user?.username}</h2>
              <p className="text-gray-600">用户名: {user?.username}</p>
              <p className="text-sm text-gray-500 mt-1">注册时间: {user?.created_at?.substring(0, 19) || '-'}</p>
            </div>
          </div>
        </motion.div>

        {/* 信息表单 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/70 backdrop-blur-xl rounded-2xl p-8 shadow-lg border border-white/50"
        >
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <User className="w-4 h-4 mr-2" />
                昵称
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => setFormData({...formData, nickname: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入昵称"
                />
              ) : (
                <p className="text-gray-800 py-3">{formData.nickname || '未设置'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <Phone className="w-4 h-4 mr-2" />
                手机号
              </label>
              {isEditing ? (
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入手机号"
                />
              ) : (
                <p className="text-gray-800 py-3">{formData.phone || '未设置'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <Mail className="w-4 h-4 mr-2" />
                邮箱
              </label>
              {isEditing ? (
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入邮箱"
                />
              ) : (
                <p className="text-gray-800 py-3">{formData.email || '未设置'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                地址
              </label>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  placeholder="请输入地址"
                />
              ) : (
                <p className="text-gray-800 py-3">{formData.address || '未设置'}</p>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
