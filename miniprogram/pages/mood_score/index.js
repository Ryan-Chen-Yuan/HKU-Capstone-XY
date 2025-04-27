import * as echarts from '../../utils/ec-canvas/echarts';

Page({
  data: {
    moodScore: 75, // Single mood score (0-100)
    moodCategory: 'Happiness', // Detected mood category
    ec: {
      lazyLoad: true // Enable lazy loading for the chart
    },
    suggestions: '', // Personalized suggestions
    feedbackOptions: ['Satisfied', 'Not Satisfied', 'Provide Feedback'], // Updated feedback options
    userFeedback: null, // User's feedback
    showFeedbackModal: false // Modal for editing feedback
  },

  onLoad(options) {
    this.loadMoodAnalysis();
    this.initChart();
  },

  /**
   * Load mood analysis result
   */
  loadMoodAnalysis: function () {
    const moodScore = 75; // Example score
    const moodCategory = this.getMoodCategory(moodScore);
    const suggestions = this.getSuggestions(moodCategory);

    this.setData({ moodScore, moodCategory, suggestions });
  },

  /**
   * Initialize the ECharts chart
   */
  initChart: function () {
    this.selectComponent('#moodScoreChart').init((canvas, width, height, dpr) => {
      const chart = echarts.init(canvas, null, {
        width: width,
        height: height,
        devicePixelRatio: dpr
      });
      this.setChartOptions(chart);
      return chart;
    });
  },

  /**
   * Set chart options
   */
  setChartOptions: function (chart) {
    const { moodScore } = this.data;

    const option = {
      title: {
        text: '情绪评分',
        left: 'center'
      },
      xAxis: {
        type: 'category',
        data: ['情绪评分']
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '情绪评分',
          type: 'bar',
          data: [moodScore],
          itemStyle: {
            color: '#4caf50' // Green for positive mood
          }
        }
      ]
    };

    chart.setOption(option);
  },

  /**
   * Get mood category based on mood score
   */
  getMoodCategory: function (score) {
    if (score >= 80) return 'Happiness';
    if (score >= 60) return 'Calmness';
    if (score >= 40) return 'Neutral';
    if (score >= 20) return 'Sadness';
    return 'Anger';
  },

  /**
   * Get personalized suggestions based on mood category
   */
  getSuggestions: function (category) {
    const suggestionsMap = {
      Happiness: 'You’re feeling great! Keep spreading positivity!',
      Calmness: 'You’re calm and composed. Enjoy the moment!',
      Neutral: 'Feeling neutral? Maybe try something fun or relaxing.',
      Sadness: 'Feeling down? Talk to a friend or listen to uplifting music.',
      Anger: 'Feeling angry? Take deep breaths or go for a walk to cool down.'
    };
    return suggestionsMap[category] || 'Keep going!';
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

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: '情绪分析结果',
      path: '/pages/mood_score/index'
    };
  },

  // 返回上一页
  navigateBack: function() {
    wx.navigateBack();
  }

});