// 获取应用实例
const app = getApp()

Page({
  data: {
    showSidebar: false,
    messages: [],
    inputMessage: '',
    isLoading: false,
    scrollToMessage: '',
    chatHistory: [],
    userInfo: {},
    medals: [
      {
        id: 1,
        name: '新手勋章',
        icon: 'https://mmbiz.qpic.cn/mmbiz_png/UicQ7HgWiaUb0Z1V9YjBZXHg5KwXZbP3ZrfbL8iciaDKQicLKlP7YtSAYWnYz3IcZBGJvVMVBZf4W3UgcJ5UqfRH2icw/0',
        description: '开启AI助手之旅'
      },
      {
        id: 2,
        name: '活跃勋章',
        icon: 'https://mmbiz.qpic.cn/mmbiz_png/UicQ7HgWiaUb0Z1V9YjBZXHg5KwXZbP3ZrPdvXt7GWoibqzfRMvR3yPmkjGR8yNIib3ib3uOBZqyaYNw7yNjRQUuiciaA/0',
        description: '与AI助手频繁互动'
      },
      {
        id: 3,
        name: '专家勋章',
        icon: 'https://mmbiz.qpic.cn/mmbiz_png/UicQ7HgWiaUb0Z1V9YjBZXHg5KwXZbP3ZrCkKzFEeKNBVt1Zd5IqBYdKicvibPSFxiaqnBJqd1wqnJNEAkO7bGmNx1Q/0',
        description: '成为AI交互专家'
      }
    ],
    medalPosition: {
      x: wx.getWindowInfo().windowWidth - 150,  // 初始位置设置在右上角
      y: 120  // 预留顶部状态栏和导航栏的空间
    },
    isDragging: false,
    startX: 0,
    startY: 0
  },

  onLoad: function() {
    // 不再自动加载用户信息
    this.loadChatHistory()
    this.loadMedals()
  },

  // 加载用户信息 - 修改为只从缓存获取，不再自动请求
  loadUserInfo: function() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.setData({ userInfo })
    }
    // 不再自动获取用户信息
  },

  // 加载聊天历史
  loadChatHistory: function() {
    const chatHistory = wx.getStorageSync('chatHistory') || []
    this.setData({ chatHistory })
  },

  // 加载勋章数据
  loadMedals: function() {
   
    const medals = [
      { id: 1, name: '初来乍到', icon: '/images/medals/newbie.png', unlocked: true },
      { id: 2, name: '活跃用户', icon: '/images/medals/active.png', unlocked: true },
      { id: 3, name: '知识达人', icon: '/images/medals/expert.png', unlocked: false }
    ]
    this.setData({ medals })
  },

  // 切换侧边栏
  toggleSidebar: function() {
    this.setData({
      showSidebar: !this.data.showSidebar
    })
  },

  // 关闭侧边栏
  closeSidebar: function() {
    this.setData({
      showSidebar: false
    })
  },

  // 开始新对话
  startNewChat: function() {
    this.setData({
      messages: [],
      inputMessage: ''
    })
    this.closeSidebar()
  },

  // 加载历史对话
  loadChat: function(e) {
    const chatId = e.currentTarget.dataset.id
    const chat = this.data.chatHistory.find(item => item.id === chatId)
    if (chat) {
      this.setData({
        messages: chat.messages,
        inputMessage: ''
      })
    }
    this.closeSidebar()
  },

  // 删除对话
  deleteChat: function(e) {
    const chatId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条对话记录吗？',
      success: (res) => {
        if (res.confirm) {
          const chatHistory = this.data.chatHistory.filter(item => item.id !== chatId)
          wx.setStorageSync('chatHistory', chatHistory)
          this.setData({ chatHistory })
          
          // 如果删除的是当前对话，清空消息
          if (this.data.messages.length > 0 && this.data.messages[0].chatId === chatId) {
            this.setData({ messages: [] })
          }
          
          wx.showToast({
            title: '删除成功',
            icon: 'success'
          })
        }
      }
    })
  },

  // 输入框内容变化
  onInputChange: function(e) {
    this.setData({
      inputMessage: e.detail.value
    })
  },

  // 发送消息
  sendMessage: function() {
    const content = this.data.inputMessage.trim()
    if (!content) return

    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: content,
      timestamp: new Date().toISOString()
    }

    this.setData({
      messages: [...this.data.messages, newMessage],
      inputMessage: '',
      isLoading: true
    })

    this.scrollToBottom()

    // 模拟AI回复
    setTimeout(() => {
      const aiResponse = {
        id: Date.now(),
        type: 'agent',
        content: '这是一个模拟的AI回复消息。在实际应用中，这里应该调用后端API获取真实的AI响应。',
        timestamp: new Date().toISOString()
      }

      this.setData({
        messages: [...this.data.messages, aiResponse],
        isLoading: false
      })

      this.scrollToBottom()
      this.saveChatHistory()
    }, 1000)
  },

  // 滚动到底部
  scrollToBottom: function() {
    const messages = this.data.messages
    if (messages.length > 0) {
      this.setData({
        scrollToMessage: `msg-${messages[messages.length - 1].id}`
      })
    }
  },

  // 保存聊天历史
  saveChatHistory: function() {
    const messages = this.data.messages
    if (messages.length > 0) {
      const chatId = messages[0].chatId || Date.now()
      const chat = {
        id: chatId,
        title: messages[0].content.slice(0, 20) + (messages[0].content.length > 20 ? '...' : ''),
        time: new Date().toLocaleString(),
        messages: messages
      }

      let chatHistory = this.data.chatHistory
      const existingIndex = chatHistory.findIndex(item => item.id === chatId)
      
      if (existingIndex !== -1) {
        chatHistory[existingIndex] = chat
      } else {
        chatHistory = [chat, ...chatHistory]
      }

      wx.setStorageSync('chatHistory', chatHistory)
      this.setData({ chatHistory })
    }
  },

  // 跳转到勋章页面
  navigateToMedals: function() {
    if (!this.data.isDragging) {
      wx.navigateTo({
        url: '/pages/medals/index',
        success: function() {
          console.log('成功跳转到勋章页面');
        },
        fail: function(error) {
          console.error('跳转到勋章页面失败:', error);
          wx.showToast({
            title: '跳转失败，请重试',
            icon: 'none'
          });
        }
      });
    }
  },
  
  // 触摸开始事件
  touchStart: function(e) {
    this.setData({
      isDragging: true,
      startX: e.touches[0].clientX - this.data.medalPosition.x,
      startY: e.touches[0].clientY - this.data.medalPosition.y
    })
  },
  
  // 触摸移动事件
  touchMove: function(e) {
    if (!this.data.isDragging) return
    
    const x = e.touches[0].clientX - this.data.startX
    const y = e.touches[0].clientY - this.data.startY
    
    // 使用新的API获取窗口信息
    const windowInfo = wx.getWindowInfo()
    const maxX = windowInfo.windowWidth - 60 // 勋章展示架宽度的一半，允许贴边
    const maxY = windowInfo.windowHeight - 120 // 预留底部空间
    
    // 限制勋章展示架不超出屏幕，允许完全贴边
    const boundedX = Math.max(0, Math.min(x, maxX))
    const boundedY = Math.max(88, Math.min(y, maxY)) // 顶部预留导航栏高度
    
    this.setData({
      medalPosition: {
        x: boundedX,
        y: boundedY
      }
    })
  },
  
  // 触摸结束事件
  touchEnd: function() {
    this.setData({
      isDragging: false
    })
  },
  
  // 跳转到个人中心
  navigateToProfile: function() {
    // 关闭侧边栏
    this.closeSidebar();
    // 使用navigateTo而不是switchTab，因为已经移除了tabBar
    wx.navigateTo({
      url: '/pages/profile/profile',
      success: function() {
        console.log('成功跳转到个人中心页面');
      },
      fail: function(error) {
        console.error('跳转到个人中心页面失败:', error);
        wx.showToast({
          title: '跳转失败，请重试',
          icon: 'none'
        });
      }
    });
  }
}) 