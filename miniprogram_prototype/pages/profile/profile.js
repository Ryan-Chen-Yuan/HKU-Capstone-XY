const app = getApp();

Page({
  data: {
    userInfo: {
      avatarUrl: '/images/default-avatar.png',
      nickName: '用户'
    },
    userId: '',
    hasUserInfo: false,
    medals: []
  },

  onLoad() {
    // 生成随机用户ID
    this.generateRandomUserId();
    // 获取奖章数据
    this.getMedals();
  },
  
  onShow() {
    // 不再自动更新用户信息
  },

  // 生成随机用户ID
  generateRandomUserId() {
    // 生成6位随机数字和字母组合
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let userId = '';
    for (let i = 0; i < 6; i++) {
      userId += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    this.setData({
      userId: userId
    });
  },

  // 处理登录 - 保留方法但不自动调用
  async handleLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },
  
  // 获取奖章数据
  getMedals() {
    // 这里可以从服务器获取奖章数据，这里使用模拟数据
    const mockMedals = [
      {
        id: 1,
        name: '初来乍到',
        icon: '/images/medals/newbie.png',
        date: '2023-05-01'
      },
      {
        id: 2,
        name: '对话达人',
        icon: '/images/medals/active.png',
        date: '2023-06-15'
      },
      {
        id: 3,
        name: '知识渊博',
        icon: '/images/medals/expert.png',
        date: '2023-07-20'
      }
    ];
    
    this.setData({
      medals: mockMedals
    });
  },
  
  // 返回上一页
  navigateBack() {
    wx.navigateBack({
      delta: 1,
      fail: function() {
        // 如果返回失败（例如，没有上一页），则导航到首页
        wx.redirectTo({
          url: '/pages/index/index'
        });
      }
    });
  },

  // 导航到对话历史页面
  navigateToHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    });
  },

  // 导航到设置页面
  navigateToSettings() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  // 导航到关于我们页面
  navigateToAbout() {
    wx.navigateTo({
      url: '/pages/about/about'
    });
  },

  // 导航到意见反馈页面
  navigateToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  }
}); 