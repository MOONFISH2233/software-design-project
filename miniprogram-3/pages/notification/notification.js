const { request } = require('../../utils/request');
const { getList, getPages } = require('../../utils/api-data');

const PAGE_SIZE = 20;

Page({
  data: {
    notifications: [],
    page: 1,
    hasMore: true,
    loading: false
  },

  onLoad() {
    this.loadNotifications(true);
  },

  async onPullDownRefresh() {
    await this.loadNotifications(true);
    wx.stopPullDownRefresh();
  },

  async onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      await this.loadNotifications(false);
    }
  },

  async loadNotifications(refresh = false) {
    const page = refresh ? 1 : this.data.page;
    this.setData({ loading: true });

    try {
      const res = await request({
        url: '/notification/list',
        method: 'GET',
        data: {
          page,
          per_page: PAGE_SIZE
        }
      });
      const items = getList(res, ['notifications']);

      this.setData({
        notifications: refresh ? items : this.data.notifications.concat(items),
        page: page + 1,
        hasMore: page < getPages(res, PAGE_SIZE, ['notifications']),
        loading: false
      });
    } catch (err) {
      console.error('获取通知失败:', err);
      this.setData({ loading: false });
    }
  },

  async markRead(e) {
    const id = e.currentTarget.dataset.id;
    if (!id) {
      return;
    }

    try {
      await request({
        url: `/notification/read/${id}`,
        method: 'PUT'
      });

      const notifications = this.data.notifications.map((item) => {
        if (`${item.notification_id}` === `${id}`) {
          return {
            ...item,
            is_read: true
          };
        }
        return item;
      });

      this.setData({ notifications });
    } catch (err) {
      console.error('标记通知失败:', err);
    }
  }
});
