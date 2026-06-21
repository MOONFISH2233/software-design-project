const { request } = require('../../utils/request');

Page({
  data: {
    devices: [],
    loading: true
  },
  
  onShow() {
    this.fetchDeviceList();
  },
  
  // 下拉刷新
  async onPullDownRefresh() {
    await this.fetchDeviceList();
    wx.stopPullDownRefresh();
  },
  
  async fetchDeviceList() {
    wx.showLoading({ title: '加载中...' });
    
    try {
      const res = await request({
        url: '/device/list?page=1&per_page=20',
        method: 'GET'
      });
      
      console.log('设备列表:', res);
      
      this.setData({ 
        devices: res.devices || [],
        loading: false
      });
      
      wx.hideLoading();
      
    } catch (err) {
      console.error('获取设备失败:', err);
      wx.hideLoading();
      wx.showToast({ 
        title: '加载失败', 
        icon: 'none' 
      });
      this.setData({ loading: false });
    }
  },
  
  goToBind() {
    wx.navigateTo({ url: '/pages/device/bind' });
  },
  
  // 查看设备详情
  viewDeviceDetail(e) {
    const deviceId = e.currentTarget.dataset.id;
    wx.showToast({ 
      title: '查看详情功能开发中', 
      icon: 'none' 
    });
  },
  
  // 删除设备
  async deleteDevice(e) {
    const deviceId = e.currentTarget.dataset.id;
    const deviceName = e.currentTarget.dataset.name;
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除设备"${deviceName}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await request({
              url: `/device/${deviceId}`,
              method: 'DELETE'
            });
            
            wx.showToast({ 
              title: '删除成功', 
              icon: 'success' 
            });
            
            // 重新加载列表
            this.fetchDeviceList();
            
          } catch (err) {
            console.error('删除失败:', err);
            wx.showToast({ 
              title: '删除失败', 
              icon: 'none' 
            });
          }
        }
      }
    });
  }
});