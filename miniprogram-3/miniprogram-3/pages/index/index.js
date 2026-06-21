// index.js - 数据看板页面
const { request } = require('../../utils/request');

Page({
  data: {
    // 统计数据
    statistics: {
      totalDevices: 0,
      totalRecords: 0,
      unreadNotifications: 0
    },
    
    // 设备列表
    devices: [],
    
    // 图表数据（最近7天）
    chartData: [],
    
    // 加载状态
    loading: true
  },

  async onLoad() {
    await this.loadData();
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await this.loadData();
    wx.stopPullDownRefresh();
  },

  async loadData() {
    wx.showLoading({ title: '加载中...' });
    
    try {
      // 并行请求多个接口
      const [devicesRes, statsRes, notifRes] = await Promise.all([
        request({ url: '/device/list', method: 'GET' }),
        request({ url: '/data/statistics?days=7', method: 'GET' }),
        request({ url: '/notification/list?is_read=false&page=1&per_page=1', method: 'GET' })
      ]);

      console.log('设备列表:', devicesRes);
      console.log('统计数据:', statsRes);
      console.log('通知:', notifRes);

      // 处理设备列表
      const devices = devicesRes.devices || [];
      
      // 处理统计数据
      const statistics = statsRes.statistics || [];
      
      // 格式化图表数据
      const chartData = statistics.map(item => ({
        date: item.stat_date.substring(5), // 只显示月-日
        moisture: Math.round(item.avg_moisture || 0),
        oiliness: Math.round(item.avg_oiliness || 0)
      }));

      // 计算总记录数
      const totalRecords = statistics.reduce((sum, item) => {
        return sum + (item.total_records || 0);
      }, 0);

      this.setData({
        devices,
        chartData,
        statistics: {
          totalDevices: devices.length,
          totalRecords: totalRecords,
          unreadNotifications: notifRes.total || 0
        },
        loading: false
      });

      wx.hideLoading();
      
    } catch (err) {
      console.error('加载数据失败:', err);
      wx.hideLoading();
      wx.showToast({ 
        title: '数据加载失败', 
        icon: 'none' 
      });
      this.setData({ loading: false });
    }
  },

  // 跳转到设备管理
  goToDevices() {
    wx.switchTab({ url: '/pages/device/device' });
  },

  // 跳转到通知中心
  goToNotifications() {
    wx.navigateTo({ url: '/pages/notification/notification' });
  },

  // 跳转到健康报告
  goToReports() {
    wx.navigateTo({ url: '/pages/report/list' });
  }
});
