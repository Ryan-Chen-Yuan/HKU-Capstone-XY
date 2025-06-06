const app = getApp();

Page({
  data: {
    isLoading: false
  },

  onLoad() {
    // 不再自动检查登录状态
  },

  // 处理返回按钮点击
  handleBack() {
    // 获取当前页面栈
    const pages = getCurrentPages();
    
    // 如果页面栈中有多个页面，则返回上一页
    if (pages.length > 1) {
      wx.navigateBack({
        delta: 1
      });
    } else {
      // 如果没有上一页，则跳转到首页
      wx.redirectTo({
        url: '/pages/index/index'
      });
    }
  },

  async handleLogin() {
    if (this.data.isLoading) return;
    
    this.setData({ isLoading: true });
    
    try {
      // 调用登录方法
      await app.login();
      // 获取用户信息
      await app.getUserInfo();
      
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });

      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        this.navigateToHome();
      }, 1500);
    } catch (error) {
      console.error('登录失败:', error);
      wx.showToast({
        title: '登录失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ isLoading: false });
    }
  },

  navigateToHome() {
    // 使用redirectTo而不是switchTab，因为已经移除了tabBar
    wx.redirectTo({
      url: '/pages/index/index'
    });
  }
}); 