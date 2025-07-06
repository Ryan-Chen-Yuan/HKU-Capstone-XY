const API_BASE_URL = 'http://localhost:5858/api'
Page({
  data: {
    moodIntensity: 8/10, // Mood intensity (0-10)
    moodCategory: '沮丧', // Detected mood category
    thinking: '我真是一事无成', // Current thinking
    scene: '在朋友圈看到朋友的分享', // Current scene or context
    ec: {
      lazyLoad: true // Enable lazy loading for the chart
    },
    disabled: true, 
    buttonDisabled: false, // Button state
    session_id: 0, // Session ID
    user_id: 0, // User ID
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
    // Save session_id and user_id if present
    if (options.session_id) {
        this.setData({ session_id: JSON.parse(decodeURIComponent(options.session_id)) });
    }
    if (options.user_id) {
        this.setData({ user_id:JSON.parse(decodeURIComponent(options.user_id)) });
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
  },

  onEdit() {
    this.setData({ disabled: false });
    wx.showToast({
      title: '现在可以点击表格内容编辑啦',
      icon: 'none'
    });
  },
  onAccept() {
    const { moodIntensity, moodCategory, thinking, scene, session_id } = this.data;
    wx.request({
      url: `${API_BASE_URL}/save_mood_data`,
      method: 'POST',
      data: {
        // user_id,
        session_id,
        mood_data: {
          moodIntensity,
          moodCategory,
          thinking,
          scene
        }
      },
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ disabled: true, buttonDisabled: true });
          wx.showToast({
            title: '保存成功',
            icon: 'success'
          });
          setTimeout(() => {
            wx.navigateBack({ delta: 1 });
          }, 2000);
        } else {
          wx.showToast({
            title: '保存失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        });
      }
    });
  },
  onReject() {
    this.setData({ disabled: true, buttonDisabled: true});
    wx.showToast({
      title: '好的，已知悉你不采纳本次情绪分析结果',
      icon: 'none'
    });
    setTimeout(() => {
      wx.navigateBack({ delta: 1 });
    }, 2000);
  },
});