const { request } = require('../../utils/util');
const { getList } = require('../../utils/api-data');
const { mergeRealtimeData } = require('../../utils/skin-data');

Page({
  data: {
    devices: [],
    loading: true,
    refreshing: false,
    refreshTimer: null,
    lastGood: {
      deviceRes: {},
      skinRes: {},
      environmentRes: {}
    }
  },
  
  onShow() {
    this.fetchDeviceList();
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
    await this.fetchDeviceList();
    wx.stopPullDownRefresh();
  },
  
  startAutoRefresh() {
    this.stopAutoRefresh();
    const refreshTimer = setInterval(() => {
      this.fetchDeviceList(false);
    }, 60000);
    this.setData({ refreshTimer });
  },

  stopAutoRefresh() {
    if (this.data.refreshTimer) {
      clearInterval(this.data.refreshTimer);
      this.setData({ refreshTimer: null });
    }
  },
  
  async fetchDeviceList(showLoading = true) {
    if (this.data.refreshing) {
      return;
    }
    if (showLoading) {
      wx.showLoading({ title: '加载中...' });
    }
    this.setData({ refreshing: true });
    
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
    
    try {
      const [deviceResult, skinResult, environmentResult] = await Promise.all([
        safeRequest('deviceRes', {
          url: '/device/list',
          method: 'GET',
          data: { page: 1, per_page: 20 }
        }),
        safeRequest('skinRes', {
          url: '/data/skin',
          method: 'GET',
          data: { days: 7, page: 1, per_page: 50 }
        }),
        safeRequest('environmentRes', {
          url: '/data/environment',
          method: 'GET',
          data: { days: 7, page: 1, per_page: 50 }
        })
      ]);
      const deviceRes = deviceResult.data;
      const skinRes = skinResult.data;
      const environmentRes = environmentResult.data;
      
      console.log('设备列表:', deviceRes);
      console.log('皮肤数据:', skinRes);
      console.log('环境数据:', environmentRes);

      const devices = getList(deviceRes, ['devices']);
      
      this.setData({ 
        devices: mergeRealtimeData(devices, skinRes, environmentRes),
        loading: false,
        refreshing: false,
        lastGood: {
          deviceRes: deviceResult.ok ? deviceRes : this.data.lastGood.deviceRes,
          skinRes: skinResult.ok ? skinRes : this.data.lastGood.skinRes,
          environmentRes: environmentResult.ok ? environmentRes : this.data.lastGood.environmentRes
        }
      });
      
      if (showLoading) {
        wx.hideLoading();
      }
      
    } catch (err) {
      console.error('获取设备失败:', err);
      if (showLoading) {
        wx.hideLoading();
      }
      wx.showToast({ 
        title: '加载失败', 
        icon: 'none' 
      });
      this.setData({ loading: false });
      this.setData({ refreshing: false });
    }
  },
  
  goToBind() {
    wx.navigateTo({ url: '/pages/device/bind' });
  },
  
  // 查看设备详情
  viewDeviceDetail(e) {
    const deviceId = e.currentTarget.dataset.id;
    wx.showModal({
      title: '设备详情',
      content: `设备ID：${deviceId}`,
      showCancel: false
    });
  },
  
  // 删除设备
  async deleteDevice(e) {
    const deviceName = e.currentTarget.dataset.name;

    wx.showToast({
      title: `${deviceName || '设备'}暂不支持解绑`,
      icon: 'none'
    });
  }
});
