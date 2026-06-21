const { request } = require('../../utils/request');

Page({
  data: {
    userInfo: {},
    stats: {
      totalDevices: 0,
      totalReports: 0,
      totalDays: 0
    }
  },
  
  onShow() {
    this.getUserProfile();
    this.loadStats();
  },

  async getUserProfile() {
    wx.showLoading({ title: '加载中...' });
    
    try {
      const res = await request({
        url: '/user/profile',
        method: 'GET'
      });
      
      console.log('用户信息:', res);
      
      this.setData({ 
        userInfo: res.user || {}
      });
      
      wx.hideLoading();
      
    } catch (err) {
      console.error('获取用户信息失败:', err);
      wx.hideLoading();
      
      // 从本地存储获取
      const localUserInfo = wx.getStorageSync('userInfo');
      if (localUserInfo) {
        this.setData({ userInfo: localUserInfo });
      }
    }
  },
  
  async loadStats() {
    try {
      // 获取设备数量
      const devicesRes = await request({
        url: '/device/list',
        method: 'GET'
      });
      
      // 获取报告数量
      const reportsRes = await request({
        url: '/report/list?page=1&per_page=1',
        method: 'GET'
      });
      
      this.setData({
        stats: {
          totalDevices: (devicesRes.devices || []).length,
          totalReports: reportsRes.total || 0,
          totalDays: 30 // 默认显示30天
        }
      });
      
    } catch (err) {
      console.error('加载统计失败:', err);
    }
  },

  viewReports() {
    wx.navigateTo({ url: '/pages/report/list' });
  },
  
  viewNotifications() {
    wx.navigateTo({ url: '/pages/notification/notification' });
  },
  
  viewDevices() {
    wx.switchTab({ url: '/pages/device/device' });
  },
  
  settings() {
    wx.showToast({ 
      title: '设置功能开发中', 
      icon: 'none' 
    });
  },
  
  about() {
    wx.showModal({
      title: '关于智能化妆镜',
      content: '版本：v1.0.0\n\n智能化妆镜系统，实时监测您的肌肤状态，提供科学的护肤建议。',
      showCancel: false
    });
  },
  
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          wx.reLaunch({ url: '/pages/login/login' });
        }
      }
    });
  }
});