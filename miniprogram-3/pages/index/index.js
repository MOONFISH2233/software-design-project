// index.js - 数据看板页面
const { request } = require('../../utils/util');
const { getList, getTotal } = require('../../utils/api-data');
const { mergeRealtimeData, sortByTimeDesc } = require('../../utils/skin-data');

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
    refreshing: false,
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
    }, 60000);
    this.setData({ refreshTimer });
  },

  stopAutoRefresh() {
    if (this.data.refreshTimer) {
      clearInterval(this.data.refreshTimer);
      this.setData({ refreshTimer: null });
    }
  },

  async loadData(showLoading = true) {
    if (this.data.refreshing) {
      return;
    }
    if (showLoading) {
      wx.showLoading({ title: '加载中...' });
    }
    this.setData({ loading: true, refreshing: true });
    
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

    const [
      devicesResult,
      skinResult,
      environmentResult,
      notifResult,
      statsResult
    ] = await Promise.all([
      safeRequest('devicesRes', { url: '/device/list', method: 'GET', data: { page: 1, per_page: 20 } }),
      safeRequest('skinRes', { url: '/data/skin', method: 'GET', data: { days: 7, page: 1, per_page: 50 } }),
      safeRequest('environmentRes', { url: '/data/environment', method: 'GET', data: { days: 7, page: 1, per_page: 50 } }),
      safeRequest('notifRes', { url: '/notification/list', method: 'GET', data: { is_read: false, page: 1, per_page: 1 } }),
      safeRequest('statsRes', { url: '/data/statistics', method: 'GET', data: { days: 7 } })
    ]);

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
    const skinRows = sortByTimeDesc(getList(skinRes, ['skinData', 'skin_data', 'records']));
    const dailyStats = getList(statsRes, ['statistics', 'stats']);
    const chartData = this.buildChartData(skinRows, dailyStats);
    const lastDataTime = this.getLatestDataTime(skinRows, dailyStats);
    const totalRecords = skinRows.length || dailyStats.reduce((sum, item) => {
      return sum + (item.total_records || item.records || 0);
    }, 0);

    this.setData({
      devices: allDevices,
      chartData,
      statistics: {
        totalDevices: allDevices.length,
        totalRecords,
        unreadNotifications: getTotal(notifRes, ['notifications'])
      },
      loading: false,
      loaded: true,
      refreshing: false,
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

    const latestStat = dailyStats
      .slice()
      .sort((a, b) => `${b.stat_date || b.date || ''}`.localeCompare(`${a.stat_date || a.date || ''}`))[0] || {};
    return latestStat.stat_date || latestStat.date || '';
  },

  formatClock(date) {
    const pad = (value) => `${value}`.padStart(2, '0');
    return `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
  },

  formatTrendDate(value) {
    const text = `${value || ''}`;
    if (/^\d{4}-\d{2}-\d{2}/.test(text)) {
      return text.substring(5, 10);
    }
    return text.substring(0, 5);
  },

  toChartValue(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) {
      return 0;
    }
    return Math.max(0, Math.min(100, Math.round(num)));
  },

  buildChartData(skinRows, dailyStats) {
    const stats = dailyStats
      .filter((item) => item && (item.stat_date || item.date))
      .slice()
      .sort((a, b) => `${a.stat_date || a.date}`.localeCompare(`${b.stat_date || b.date}`))
      .slice(-7)
      .map((item) => ({
        date: this.formatTrendDate(item.stat_date || item.date),
        moisture: this.toChartValue(item.avg_moisture || item.moisture),
        oiliness: this.toChartValue(item.avg_oiliness || item.oiliness),
        totalRecords: Number(item.total_records || item.records || item.record_count || 0)
      }));

    if (stats.some((item) => item.totalRecords > 0 || item.moisture > 0 || item.oiliness > 0)) {
      return stats;
    }

    const buckets = {};
    skinRows.forEach((item) => {
      const timeText = `${item.sensor_time || item.received_at || ''}`;
      const dateKey = timeText.substring(0, 10);
      if (!/^\d{4}-\d{2}-\d{2}$/.test(dateKey)) {
        return;
      }
      if (!buckets[dateKey]) {
        buckets[dateKey] = { date: dateKey, moistureSum: 0, oilinessSum: 0, count: 0 };
      }
      buckets[dateKey].moistureSum += Number(item.moisture || 0);
      buckets[dateKey].oilinessSum += Number(item.oiliness || 0);
      buckets[dateKey].count += 1;
    });

    return Object.keys(buckets)
      .sort()
      .slice(-7)
      .map((dateKey) => {
        const bucket = buckets[dateKey];
        return {
          date: this.formatTrendDate(bucket.date),
          moisture: this.toChartValue(bucket.moistureSum / bucket.count),
          oiliness: this.toChartValue(bucket.oilinessSum / bucket.count)
        };
      });
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
