import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Users, MessageCircle, Heart, Share2, Plus } from 'lucide-react';
import api from '../api';

export default function Community() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const res = await api.get('/community/posts?page=1&per_page=20');
      setPosts(res.data?.items || []);
      setLoading(false);
    } catch (error) {
      console.error('加载失败:', error);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 pt-28 pb-12 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">社区互动</h1>
            <p className="text-gray-600">分享经验，交流心得</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>发布帖子</span>
          </motion.button>
        </motion.div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent"></div>
          </div>
        ) : (
          <div className="space-y-6">
            {posts.map((post, index) => (
              <motion.div
                key={post.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.01 }}
                className="bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-lg border border-white/50 cursor-pointer"
              >
                <div className="flex items-start space-x-4 mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {(post.author_name || 'U')[0]}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-800 mb-1">{post.title || '未命名帖子'}</h3>
                    <p className="text-sm text-gray-600">
                      {post.author_name || '匿名用户'} · {post.created_at?.substring(0, 19)}
                    </p>
                  </div>
                </div>

                <p className="text-gray-700 mb-4 line-clamp-3">{post.content || '暂无内容'}</p>

                <div className="flex items-center space-x-6 text-gray-600">
                  <button className="flex items-center space-x-2 hover:text-red-500 transition-colors">
                    <Heart className="w-5 h-5" />
                    <span>{post.likes || 0}</span>
                  </button>
                  <button className="flex items-center space-x-2 hover:text-blue-500 transition-colors">
                    <MessageCircle className="w-5 h-5" />
                    <span>{post.comments || 0}</span>
                  </button>
                  <button className="flex items-center space-x-2 hover:text-green-500 transition-colors">
                    <Share2 className="w-5 h-5" />
                    <span>分享</span>
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {posts.length === 0 && !loading && (
          <div className="text-center py-20">
            <Users className="w-20 h-20 mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500 text-lg">暂无帖子，快来发布第一条吧！</p>
          </div>
        )}
      </div>
    </div>
  );
}
