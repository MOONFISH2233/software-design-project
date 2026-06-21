// index.js - 数据看板页面
const { request } = require('../../utils/util');
const { getList, getTotal } = require('../../utils/api-data');
const { isEnvironmentDevice, mergeRealtimeData, sortByTimeDesc } = require('../../utils/skin-data');

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
    loading: true,
    loaded: false,
    refreshTimer: null,
    connectionStatus: '连接中',
    lastUpdatedText: '--',
    latestDataText: '--',
    lastGood: {
      devicesRes: {},
      statsRes: [],
      notifRes: {},
      skinRes: {},
      environmentRes: {}
    }
  },

  async onLoad() {
    await this.loadData();
  },

  async onShow() {
    if (this.data.loaded) {
      await this.loadData(false);
    }
    this.startAutoRefresh();
  },

  onHide() {
    this.stopAutoRefresh();
  },

  onUnload() {
    this.stopAutoRefresh();
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await this.loadData();
    wx.stopPullDownRefresh();
  },

  startAutoRefresh() {
    this.stopAutoRefresh();
    const refreshTimer = setInterval(() => {
      this.loadData(false);
    }, 15000);
    this.setData({ refreshTimer });
  },

  stopAutoRefresh() {
    if (this.data.refreshTimer) {
      clearInterval(this.data.refreshTimer);
      this.setData({ refreshTimer: null });
    }
  },

  async loadData(showLoading = true) {
    if (showLoading) {
      wx.showLoading({ title: '加载中...' });
    }
    this.setData({ loading: true });
    
    const safeRequest = async (name, options) => {
      try {
        const res = await request({
        ...options,
        silent: !showLoading
        });
        return {
          ok: true,
          data: res
        };
      } catch (err) {
        console.warn(`${options.url} 加载失败:`, err);
        return {
          ok: false,
          data: this.data.lastGood[name] || {}
        };
      }
    };

    const devicesResult = await safeRequest('devicesRes', { url: '/device/list', method: 'GET' });
    const skinResult = await safeRequest('skinRes', { url: '/data/skin', method: 'GET', data: { days: 7, page: 1, per_page: 100 } });
    const environmentResult = await safeRequest('environmentRes', { url: '/data/environment', method: 'GET', data: { days: 7, page: 1, per_page: 100 } });
    const notifResult = await safeRequest('notifRes', { url: '/notification/list', method: 'GET', data: { is_read: false, page: 1, per_page: 1 } });
    const statsResult = await safeRequest('statsRes', { url: '/data/statistics', method: 'GET', data: { days: 7 } });

    const devicesRes = devicesResult.data;
    const statsRes = statsResult.data;
    const notifRes = notifResult.data;
    const skinRes = skinResult.data;
    const environmentRes = environmentResult.data;
    const requestResults = [devicesResult, skinResult, environmentResult, notifResult, statsResult];
    const failedCount = requestResults.filter((item) => !item.ok).length;

    console.log('看板设备列表:', devicesRes);
    console.log('看板统计数据:', statsRes);
    console.log('看板通知:', notifRes);
    console.log('看板皮肤数据:', skinRes);
    console.log('看板环境数据:', environmentRes);

    const allDevices = mergeRealtimeData(getList(devicesRes, ['devices']), skinRes, environmentRes);
    const skinDevices = allDevices.filter((device) => !isEnvironmentDevice(device));
    const skinRows = sortByTimeDesc(getList(skinRes, ['skinData', 'skin_data', 'records']));
    const dailyStats = getList(statsRes, ['statistics', 'stats']);
    const chartData = this.buildChartData(skinRows, dailyStats);
    const lastDataTime = this.getLatestDataTime(skinRows, dailyStats);
    const totalRecords = skinRows.length || dailyStats.reduce((sum, item) => {
      return sum + (item.total_records || item.records || 0);
    }, 0);

    this.setData({
      devices: skinDevices,
      chartData,
      statistics: {
        totalDevices: skinDevices.length,
        totalRecords,
        unreadNotifications: getTotal(notifRes, ['notifications'])
      },
      loading: false,
      loaded: true,
      connectionStatus: devicesRes && Object.keys(devicesRes).length > 0 ? '已连接' : '部分接口异常',
      lastUpdatedText: this.formatClock(new Date()),
      latestDataText: lastDataTime || '暂无实时数据',
      lastGood: {
        devicesRes: devicesResult.ok ? devicesRes : this.data.lastGood.devicesRes,
        statsRes: statsResult.ok ? statsRes : this.data.lastGood.statsRes,
        notifRes: notifResult.ok ? notifRes : this.data.lastGood.notifRes,
        skinRes: skinResult.ok ? skinRes : this.data.lastGood.skinRes,
        environmentRes: environmentResult.ok ? environmentRes : this.data.lastGood.environmentRes
      }
    });

    this.setData({
      connectionStatus: failedCount === 0 ? '已连接' : `已连接，${failedCount}个接口重试中`
    });

    if (showLoading) {
      wx.hideLoading();
    }
  },

  getLatestDataTime(skinRows, dailyStats) {
    const latestSkin = skinRows[0] || {};
    if (latestSkin.sensor_time || latestSkin.received_at) {
      return latestSkin.sensor_time || latestSkin.received_at;
    }

    const latestStat = dailyStats[0] || {};
    return latestStat.stat_date || '';
  },

  formatClock(date) {
    const pad = (value) => `${value}`.padStart(2, '0');
    return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  },

  buildChartData(skinRows, dailyStats) {
    if (skinRows.length > 0) {
      return skinRows.slice(0, 7).reverse().map((item) => ({
        date: item.sensor_time ? item.sensor_time.substring(5, 10) : '',
        moisture: Math.round(item.moisture || 0),
        oiliness: Math.round(item.oiliness || 0)
      }));
    }

    return dailyStats.map(item => ({
      date: item.stat_date ? item.stat_date.substring(5) : '',
      moisture: Math.round(item.avg_moisture || item.moisture || 0),
      oiliness: Math.round(item.avg_oiliness || item.oiliness || 0)
    }));
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
