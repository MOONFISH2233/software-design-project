const BASE_URL = 'https://dierzunb666.cn/api/miniprogram';
const DEFAULT_TIMEOUT = 45000;

function getCurrentRoute() {
  const pages = getCurrentPages();
  const current = pages[pages.length - 1];
  return current ? `/${current.route}` : '';
}

function toQueryString(params = {}) {
  return Object.keys(params)
    .filter((key) => params[key] !== undefined && params[key] !== null && params[key] !== '')
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&');
}

function buildUrl(url, method, data) {
  if (/^https?:\/\//.test(url)) {
    return url;
  }

  const fullUrl = `${BASE_URL}${url}`;

  if ((method || 'GET').toUpperCase() !== 'GET' || !data || Object.keys(data).length === 0) {
    return fullUrl;
  }

  const query = toQueryString(data);
  if (!query) {
    return fullUrl;
  }

  return `${fullUrl}${fullUrl.includes('?') ? '&' : '?'}${query}`;
}

function redirectToLogin() {
  wx.removeStorageSync('token');
  wx.removeStorageSync('userInfo');

  if (getCurrentRoute() === '/pages/login/login') {
    return;
  }

  wx.reLaunch({ url: '/pages/login/login' });
}

function request(options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const silent = !!options.silent;
  const token = wx.getStorageSync('token');
  const header = Object.assign(
    {
      'Content-Type': 'application/json'
    },
    options.header || {}
  );

  if (token) {
    header.Authorization = `Bearer ${token}`;
  }

  return new Promise((resolve, reject) => {
    const requestUrl = buildUrl(options.url, method, options.data);

    wx.request({
      url: requestUrl,
      method,
      data: method === 'GET' ? {} : (options.data || {}),
      header,
      timeout: options.timeout || DEFAULT_TIMEOUT,
      success(res) {
        const body = res.data || {};

        if (res.statusCode === 401) {
          if (!silent) {
            wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          }
          redirectToLogin();
          reject(body);
          return;
        }

        if (res.statusCode < 200 || res.statusCode >= 300) {
          if (!silent) {
            wx.showToast({ title: body.message || '服务器请求失败', icon: 'none' });
          }
          reject(body);
          return;
        }

        if (body.success === false) {
          if (!silent) {
            wx.showToast({ title: body.message || '操作失败', icon: 'none' });
          }
          reject(body);
          return;
        }

        resolve(body.data !== undefined ? body.data : body);
      },
      fail(err) {
        if (!silent) {
          const message = err && `${err.errMsg || ''}`.includes('timeout')
            ? '服务器响应超时，请稍后重试'
            : '网络连接失败，请检查网络';
          wx.showToast({ title: message, icon: 'none' });
        }
        console.warn('请求失败:', requestUrl, err);
        reject(err);
      }
    });
  });
}

module.exports = {
  BASE_URL,
  DEFAULT_TIMEOUT,
  request
};
