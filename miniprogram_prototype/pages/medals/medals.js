// medals.js
Page({
  data: {
    medals: [
      {
        id: 1,
        name: '初来乍到',
        icon: '/images/medal-new.png',
        description: '完成首次对话',
        progress: 100,
        unlocked: true,
        unlockDate: '2024-03-15'
      },
      {
        id: 2,
        name: '对话达人',
        icon: '/images/medal-chat.png',
        description: '累计完成100次对话',
        progress: 45,
        unlocked: false
      },
      {
        id: 3,
        name: '知识渊博',
        icon: '/images/medal-knowledge.png',
        description: '累计提问1000次',
        progress: 30,
        unlocked: false
      },
      {
        id: 4,
        name: '坚持不懈',
        icon: '/images/medal-persistent.png',
        description: '连续使用7天',
        progress: 5,
        unlocked: false
      }
    ],
    selectedMedal: null,
    showDetailModal: false,
    currentMedal: null,
    showDetail: false
  },

  onLoad: function() {
    // 从本地存储获取勋章数据
    const storedMedals = wx.getStorageSync('medals');
    if (storedMedals) {
      this.setData({
        medals: storedMedals
      });
    }
  },

  // 显示勋章详情
  showMedalDetail: function(e) {
    const { id } = e.currentTarget.dataset;
    const medal = this.data.medals.find(m => m.id === id);
    
    if (medal) {
      this.setData({
        currentMedal: medal,
        showDetail: true
      });
    }
  },

  // 隐藏勋章详情
  hideMedalDetail: function() {
    this.setData({
      showDetail: false,
      currentMedal: null
    });
  },

  // 阻止事件冒泡
  preventBubble: function() {
    return;
  },

  // 返回上一页
  navigateBack: function() {
    wx.navigateBack();
  },

  // 分享
  onShareAppMessage: function() {
    return {
      title: '我的勋章墙',
      path: '/pages/medals/medals'
    };
  },

  // 页面显示时触发动画
  onShow: function() {
    // 为每个勋章添加延迟动画
    this.data.medals.forEach((medal, index) => {
      setTimeout(() => {
        const medalItem = wx.createSelectorQuery()
          .select(`#medal-${medal.id}`)
          .boundingClientRect();
        
        medalItem.exec((res) => {
          if (res[0]) {
            res[0].node.animate([
              { transform: 'scale(0)', opacity: 0 },
              { transform: 'scale(1)', opacity: 1 }
            ], {
              duration: 500,
              easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
              fill: 'forwards'
            });
          }
        });
      }, index * 100);
    });
  }
}); 