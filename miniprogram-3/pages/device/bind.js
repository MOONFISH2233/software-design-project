const { request } = require('../../utils/request');

Page({
  data: {
    device_id: '',
    device_name: '',
    location: ''
  },

  onDeviceIdInput(e) {
    this.setData({ device_id: e.detail.value });
  },

  onDeviceNameInput(e) {
    this.setData({ device_name: e.detail.value });
  },

  onLocationInput(e) {
    this.setData({ location: e.detail.value });
  },

  async submitBind() {
    const { device_id, device_name, location } = this.data;

    if (!device_id.trim()) {
      wx.showToast({ title: '请输入设备ID', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '绑定中...' });

    try {
      await request({
        url: '/device/bind',
        method: 'POST',
        data: {
          device_id: device_id.trim(),
          device_name: device_name.trim(),
          location: location.trim()
        }
      });

      wx.showToast({ title: '绑定成功', icon: 'success' });
      setTimeout(() => {
        wx.navigateBack();
      }, 800);
    } catch (err) {
      console.error('绑定设备失败:', err);
    } finally {
      wx.hideLoading();
    }
  }
});
