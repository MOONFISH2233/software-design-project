// utils/request.js
const BASE_URL = 'http://47.103.108.47:5000'; // API base URL

function request(options) {
    return new Promise((resolve, reject) => {
        const token = wx.getStorageSync('token'); // 每次请求自动携带 Token
        
        wx.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            header: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : '' 
            },
            data: options.data || {},
            success(res) {
                if (res.statusCode === 200) {
                    if (res.data.success) {
                        resolve(res.data);
                    } else {
                        wx.showToast({
                            title: res.data.message || '操作失败',
                            icon: 'none'
                        });
                        reject(res.data);
                    }
                } else if (res.statusCode === 401) {
                    // Token 过期或未登录，踢回登录页
                    wx.showToast({ title: '请先登录', icon: 'none' });
                    wx.removeStorageSync('token');
                    wx.reLaunch({ url: '/pages/login/login' });
                } else {
                    wx.showToast({ title: '服务器开小差了', icon: 'none' });
                    reject(res);
                }
            },
            fail(err) {
                wx.showToast({ title: '网络连接断开', icon: 'none' });
                reject(err);
            }
        });
    });
}

module.exports = {
    request
};