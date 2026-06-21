// pages/community/community.js
const { request } = require('../../utils/request');

Page({
  data: {
    posts: [],
    loading: true,
    page: 1,
    hasMore: true
  },

  onLoad() {
    this.loadPosts();
  },

  // 下拉刷新
  async onPullDownRefresh() {
    this.setData({ page: 1, hasMore: true });
    await this.loadPosts(true);
    wx.stopPullDownRefresh();
  },

  // 上拉加载更多
  async onReachBottom() {
    if (this.data.hasMore) {
      this.setData({ page: this.data.page + 1 });
      await this.loadPosts(false);
    }
  },

  async loadPosts(refresh = false) {
    if (!refresh) {
      wx.showLoading({ title: '加载中...' });
    }

    try {
      const res = await request({
        url: `/community/posts?page=${this.data.page}&per_page=10`,
        method: 'GET'
      });

      console.log('社区帖子:', res);

      const newPosts = res.posts || [];
      
      this.setData({
        posts: refresh ? newPosts : [...this.data.posts, ...newPosts],
        hasMore: newPosts.length >= 10,
        loading: false
      });

      wx.hideLoading();

    } catch (err) {
      console.error('加载帖子失败:', err);
      wx.hideLoading();
      wx.showToast({ 
        title: '加载失败', 
        icon: 'none' 
      });
      this.setData({ loading: false });
    }
  },

  // 发布帖子
  createPost() {
    wx.showToast({ 
      title: '发布功能开发中', 
      icon: 'none' 
    });
  },

  // 点赞
  async likePost(e) {
    const postId = e.currentTarget.dataset.id;
    
    try {
      await request({
        url: `/community/post/${postId}/like`,
        method: 'POST'
      });
      
      // 更新本地数据
      const posts = this.data.posts.map(post => {
        if (post.id === postId) {
          return {
            ...post,
            likes: post.likes + 1,
            is_liked: true
          };
        }
        return post;
      });
      
      this.setData({ posts });
      
      wx.showToast({ 
        title: '点赞成功', 
        icon: 'success' 
      });
      
    } catch (err) {
      console.error('点赞失败:', err);
      wx.showToast({ 
        title: '操作失败', 
        icon: 'none' 
      });
    }
  },

  // 评论
  commentPost(e) {
    const postId = e.currentTarget.dataset.id;
    wx.showToast({ 
      title: '评论功能开发中', 
      icon: 'none' 
    });
  }
});