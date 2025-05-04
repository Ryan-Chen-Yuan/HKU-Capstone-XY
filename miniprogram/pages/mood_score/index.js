Page({
  data: {
    moodIntensity: 8/10, // Mood intensity (0-10)
    moodCategory: '沮丧', // Detected mood category
    thinking: '我真是一事无成', // Current thinking
    scene: '在朋友圈看到朋友的分享', // Current scene or context
    ec: {
      lazyLoad: true // Enable lazy loading for the chart
    },
  },

  onLoad(options) {
    if (options.data) {
        const moodData = JSON.parse(decodeURIComponent(options.data));
        this.setData({
            moodIntensity: moodData.moodIntensity,
            moodCategory: moodData.moodCategory,
            thinking: moodData.thinking,
            scene: moodData.scene
        });
    }
},

  /**
   * Handle user feedback
   */
  handleFeedback: function (e) {
    const { feedback } = e.currentTarget.dataset;

    if (feedback === 'Provide Feedback') {
      this.setData({ showFeedbackModal: true });
    } else {
      this.setData({ userFeedback: feedback });
      wx.showToast({
        title: `Feedback: ${feedback}`,
        icon: 'success'
      });
    }
  },

  /**
   * Hide feedback modal
   */
  hideFeedbackModal: function () {
    this.setData({ showFeedbackModal: false });
  },

  /**
   * Submit edited feedback
   */
  submitEditedFeedback: function (e) {
    const { value } = e.detail;
    this.setData({
      userFeedback: value,
      showFeedbackModal: false
    });
    wx.showToast({
      title: 'Feedback updated',
      icon: 'success'
    });
  },

  /**
   * Navigate back to the home page
   */
  navigateToHome: function () {
    wx.reLaunch({
      url: '/pages/index/index'
    });
  },

  // 返回上一页
  navigateBack: function() {
    wx.navigateBack();
  }
});