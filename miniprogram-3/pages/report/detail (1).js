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
      const details = report.details || {};

      this.setData({
        report: {
          ...report,
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
