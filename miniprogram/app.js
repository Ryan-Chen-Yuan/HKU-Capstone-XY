App({
  onLaunch() {
    // 不再自动检查登录状态
  },

  globalData: {
    userInfo: null,
    isLoggedIn: false
  },

  // 保留检查登录状态的方法，但不自动调用
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.isLoggedIn = true;
      // 获取用户信息
      this.getUserInfo();
    }
  },

  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            // 发送 code 到后台换取 openId, sessionKey, unionId
            // TODO: 替换为你的后端接口地址
            wx.request({
              url: 'YOUR_BACKEND_API/login',
              method: 'POST',
              data: {
                code: res.code
              },
              success: (response) => {
                const { token, userInfo } = response.data;
                // 保存token
                wx.setStorageSync('token', token);
                this.globalData.isLoggedIn = true;
                this.globalData.userInfo = userInfo;
                resolve(userInfo);
              },
              fail: (error) => {
                reject(error);
              }
            });
          } else {
            reject(new Error('登录失败'));
          }
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  },

  getUserInfo() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          this.globalData.userInfo = res.userInfo;
          resolve(res.userInfo);
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  },

  logout() {
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    wx.removeStorageSync('token');
  }
}) 