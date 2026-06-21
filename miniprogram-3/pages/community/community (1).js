Page({
  data: {
    posts: [],
    loading: false,
    page: 1,
    hasMore: false
  },

  onLoad() {
    this.loadPosts();
  },

  onPullDownRefresh() {
    this.loadPosts();
    wx.stopPullDownRefresh();
  },

  loadPosts() {
    this.setData({
      posts: [],
      loading: false,
      hasMore: false
    });
  },

  createPost() {
    wx.showToast({
      title: '后端暂未提供社区接口',
      icon: 'none'
    });
  },

  likePost() {
    wx.showToast({
      title: '后端暂未提供社区接口',
      icon: 'none'
    });
  },

  commentPost() {
    wx.showToast({
      title: '后端暂未提供社区接口',
      icon: 'none'
    });
  },

  previewImage(e) {
    const url = e.currentTarget.dataset.url;
    if (url) {
      wx.previewImage({
        current: url,
        urls: [url]
      });
    }
  }
});
