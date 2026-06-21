import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Smartphone, Wifi, Battery, Signal, Plus, ArrowLeft } from 'lucide-react';
import api from '../api';
import { useNavigate } from 'react-router-dom';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      const res = await api.get('/device/list');
      setDevices(res.devices || []);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  const handleBindDevice = () => {
    // TODO: 打开绑定设备对话框
    alert('绑定设备功能开发中...');
  };

  return (
    <div className="pt-28 pb-12 px-6 max-w-7xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center space-x-4">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 bg-white rounded-lg shadow hover:shadow-lg transition-all"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">设备管理</h1>
          <p className="text-gray-600">管理您的皮肤监测设备</p>
        </div>
      </motion.div>

      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleBindDevice}
        className="mb-8 px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2"
      >
        <Plus className="w-5 h-5" />
        <span>绑定新设备</span>
      </motion.button>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {devices.map((device, index) => (
              <motion.div
                key={device.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.03, y: -5 }}
                className="bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-white/50"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                    <Smartphone className="w-7 h-7 text-white" />
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${device.status === 'online' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'}`}>
                    {device.status === 'online' ? '在线' : '离线'}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-gray-800 mb-2">{device.device_name || '未命名设备'}</h3>
                <p className="text-sm text-gray-600 mb-4">{device.device_id}</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <Battery className="w-4 h-4 mr-2" />
                    <span>电量: {device.battery_level || '-'}%</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <Signal className="w-4 h-4 mr-2" />
                    <span>信号: {device.signal_strength || '-'}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
    </div>
  );
}
