const { request } = require('../../utils/request');
const { getList, getPages } = require('../../utils/api-data');

const PAGE_SIZE = 10;

Page({
  data: {
    reports: [],
    page: 1,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadReports(true);
  },

  async onPullDownRefresh() {
    await this.loadReports(true);
    wx.stopPullDownRefresh();
  },

  async onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      await this.loadReports(false);
    }
  },

  async loadReports(refresh = false) {
    const page = refresh ? 1 : this.data.page;

    this.setData({ loading: true });
    if (refresh) {
      wx.showLoading({ title: '加载中...' });
    }

    try {
      const res = await request({
        url: '/report/list',
        method: 'GET',
        data: {
          page,
          per_page: PAGE_SIZE
        }
      });

      const reports = getList(res, ['reports']);
      const normalizedReports = reports.map((item) => ({
        ...item,
        report_id: item.report_id !== undefined ? item.report_id : item.id,
        title: item.title || '健康分析',
        summary: item.summary || item.suggestions || '暂无摘要',
        generate_time: item.generate_time || item.generated_at || item.report_date || '',
        report_type: item.report_type || 'report'
      }));

      this.setData({
        reports: refresh ? normalizedReports : this.data.reports.concat(normalizedReports),
        page: page + 1,
        hasMore: page < getPages(res, PAGE_SIZE, ['reports']),
        loading: false
      });
    } catch (err) {
      console.error('获取报告列表失败:', err);
      this.setData({ loading: false });
    } finally {
      wx.hideLoading();
    }
  },

  viewDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/report/detail?id=${id}` });
  }
});
