const { request } = require('../../utils/request');

Page({
  data: {
    username: '',
    password: ''
  },
  
  // 输入框绑定
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    });
  },
  
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },
  
  async handleLogin() {
    if (!this.data.username || !this.data.password) {
      return wx.showToast({ title: '请输入账号和密码', icon: 'none' });
    }
    
    wx.showLoading({ title: '登录中...' });
    
    try {
      const res = await request({
        url: '/api/auth/login',
        method: 'POST',
        data: {
          username: this.data.username,
          password: this.data.password
        }
      });
      
      console.log('登录成功:', res);
      
      // 保存 Token 和用户信息
      wx.setStorageSync('token', res.token);
      wx.setStorageSync('userInfo', res.user);
      
      wx.hideLoading();
      wx.showToast({ 
        title: '登录成功', 
        icon: 'success',
        duration: 1500
      });
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        wx.switchTab({ 
          url: '/pages/index/index',
          fail: (err) => {
            console.error('跳转失败:', err);
            wx.showToast({ title: '页面跳转失败', icon: 'none' });
          }
        });
      }, 1500);
      
    } catch (err) {
      console.error('登录失败:', err);
      wx.hideLoading();
      
      // 显示具体错误信息
      const errorMsg = err.message || err.errMsg || '登录失败，请重试';
      wx.showToast({ 
        title: errorMsg, 
        icon: 'none',
        duration: 2000
      });
    }
  }
});