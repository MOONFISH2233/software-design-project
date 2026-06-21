const { request } = require('../../utils/request');

Page({
  data: {
    report: null,
    recommendations: []
  },

  onLoad(options) {
    if (options.id) {
      this.loadReport(options.id);
    }
  },

  async loadReport(id) {
    wx.showLoading({ title: '加载中...' });

    try {
      const report = await request({
        url: `/report/detail/${id}`,
        method: 'GET'
      });
      const payload = report.report || report || {};
      const details = payload.details || {};

      this.setData({
        report: {
          ...payload,
          details
        },
        recommendations: details.recommendations || []
      });
    } catch (err) {
      console.error('获取报告详情失败:', err);
    } finally {
      wx.hideLoading();
    }
  }
});
