const { request } = require('../../utils/request');
const { getTotal, getList } = require('../../utils/api-data');

function normalizeUser(user = {}) {
  const nickname = user.nickname || user.username || '用户';

  return {
    ...user,
    avatar: user.avatar || user.avatar_url || '',
    nickname,
    avatarText: nickname.slice(0, 1),
    skin_type: user.skin_type || '未设置'
  };
}

Page({
  data: {
    userInfo: {},
    stats: {
      totalDevices: 0,
      totalReports: 0,
      totalDays: 0,
      unreadNotifications: 0
    },
    loading: false
  },

  onShow() {
    this.loadProfileData();
  },

  async loadProfileData() {
    const cachedUser = wx.getStorageSync('userInfo') || {};
    if (cachedUser && Object.keys(cachedUser).length > 0) {
      this.setData({ userInfo: normalizeUser(cachedUser) });
    }

    this.setData({ loading: true });
    wx.showLoading({ title: '加载中...' });

    try {
      const [profile, devices, reports, notifications, stats] = await Promise.all([
        request({ url: '/user/profile', method: 'GET' }),
        request({ url: '/device/list', method: 'GET', data: { page: 1, per_page: 1 } }),
        request({ url: '/report/list', method: 'GET', data: { page: 1, per_page: 1 } }),
        request({ url: '/notification/list', method: 'GET', data: { is_read: false, page: 1, per_page: 1 } }),
        request({ url: '/data/statistics', method: 'GET', data: { days: 30 } })
      ]);

      const userInfo = normalizeUser(profile);
      wx.setStorageSync('userInfo', userInfo);

      this.setData({
        userInfo,
        stats: {
          totalDevices: getTotal(devices, ['devices']),
          totalReports: getTotal(reports, ['reports']),
          totalDays: getList(stats, ['statistics', 'stats']).length,
          unreadNotifications: getTotal(notifications, ['notifications'])
        },
        loading: false
      });
    } catch (err) {
      console.error('加载我的页面失败:', err);
      this.setData({ loading: false });
    } finally {
      wx.hideLoading();
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
