const { request } = require('../../utils/util');

Page({
  data: {
    username: '123',
    password: '123456',
    nickname: '',
    isRegisterMode: false,
    demoAccounts: [
      { label: '默认用户', username: '123', password: '123456' },
      { label: '李骏逸', username: 'alice', password: '123456' },
      { label: '刘湘渝', username: 'bob', password: '123456' },
      { label: '刘卓雅', username: 'teacher', password: '123456' }
    ]
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

  onNicknameInput(e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  selectDemoAccount(e) {
    const index = Number(e.currentTarget.dataset.index);
    const account = this.data.demoAccounts[index];
    if (!account) return;
    this.setData({
      username: account.username,
      password: account.password,
      nickname: account.label,
      isRegisterMode: false
    });
  },

  toggleRegisterMode() {
    this.setData({
      isRegisterMode: !this.data.isRegisterMode,
      nickname: this.data.isRegisterMode ? '' : this.data.nickname
    });
  },
  
  async handleLogin() {
    if (!this.data.username || !this.data.password) {
      return wx.showToast({ title: '请输入账号和密码', icon: 'none' });
    }
    
    wx.showLoading({ title: '登录中...' });
    
    try {
      const res = await request({
        url: '/user/login',
        method: 'POST',
        data: {
          username: this.data.username,
          password: this.data.password
        }
      });
      
      console.log('登录成功:', res);
      
      // 保存 Token 和用户信息
      wx.setStorageSync('token', res.token);
      wx.setStorageSync('userInfo', res.user || {});
      
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
  },

  async handleRegister() {
    if (!this.data.username || !this.data.password) {
      return wx.showToast({ title: '请输入账号和密码', icon: 'none' });
    }

    wx.showLoading({ title: '注册中...' });

    try {
      await request({
        url: '/user/register',
        method: 'POST',
        data: {
          username: this.data.username,
          password: this.data.password,
          nickname: this.data.nickname || this.data.username
        }
      });

      wx.hideLoading();
      wx.showToast({
        title: '注册成功',
        icon: 'success',
        duration: 1200
      });

      this.setData({ isRegisterMode: false });
      setTimeout(() => this.handleLogin(), 1200);
    } catch (err) {
      console.error('注册失败:', err);
      wx.hideLoading();
      wx.showToast({
        title: err.message || err.errMsg || '注册失败，请重试',
        icon: 'none',
        duration: 2000
      });
    }
  }
});
