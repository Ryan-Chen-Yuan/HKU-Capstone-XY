// pages/medals/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    medals: [
      {
        id: 1,
        name: '初来乍到',
        icon: '/images/medals/newbie.png',
        description: '完成首次对话',
        progress: 100,
        unlocked: true,
        unlockDate: '2024-03-15'
      },
      {
        id: 2,
        name: '对话达人',
        icon: '/images/medals/active.png',
        description: '累计完成100次对话',
        progress: 45,
        unlocked: false
      },
      {
        id: 3,
        name: '知识渊博',
        icon: '/images/medals/expert.png',
        description: '累计提问1000次',
        progress: 30,
        unlocked: false
      },
      {
        id: 4,
        name: '坚持不懈',
        icon: '/images/medals/newbie.png', // 使用现有图标
        description: '连续使用7天',
        progress: 5,
        unlocked: false
      }
    ],
    selectedMedal: null,
    showDetailModal: false,
    currentMedal: null,
    showDetail: false,
    medalAnimations: []
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 从本地存储获取勋章数据
    const storedMedals = wx.getStorageSync('medals');
    if (storedMedals) {
      this.setData({
        medals: storedMedals
      });
    }
    
    // 初始化动画状态数组
    const medalAnimations = this.data.medals.map(() => false);
    this.setData({ medalAnimations });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 使用setTimeout模拟动画效果
    const medalAnimations = this.data.medalAnimations.map(() => false);
    this.setData({ medalAnimations });
    
    // 为每个勋章添加延迟动画
    this.data.medals.forEach((medal, index) => {
      setTimeout(() => {
        const newMedalAnimations = [...this.data.medalAnimations];
        newMedalAnimations[index] = true;
        this.setData({ medalAnimations: newMedalAnimations });
      }, index * 200);
    });
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: '我的勋章墙',
      path: '/pages/medals/index'
    };
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
  }
})