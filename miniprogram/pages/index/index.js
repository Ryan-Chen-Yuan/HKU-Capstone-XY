// 获取应用实例
const app = getApp()

// 添加后端API基础URL
const API_BASE_URL = 'http://localhost:5858/api'

function getRecentMessages(messages, windowSize = 7) {
  return messages.slice(-windowSize);
}

Page({
  data: {
    showSidebar: false,
    messages: [],
    inputMessage: '',
    isLoading: false,
    scrollToMessage: '',
    chatHistory: [],
    userInfo: {},
    moodData: null, 
    medals: [
      {
        id: 1,
        name: '新手勋章',
        icon: '/images/default-avatar.png',
        description: '开启AI助手之旅'
      },
      {
        id: 2,
        name: '活跃勋章',
        icon: '/images/default-avatar.png',
        description: '与AI助手频繁互动'
      },
      {
        id: 3,
        name: '专家勋章',
        icon: '/images/default-avatar.png',
        description: '成为AI交互专家'
      }
    ],
    monsterPosition: {
      x: wx.getWindowInfo().windowWidth - 120,
      y: 120
    },
    medalBubblePosition: {
      x: wx.getWindowInfo().windowWidth - 100,
      y: 140
    },
    medalBubbleSize: 80,
    medalBubbleDragging: false,
    medalBubbleStartX: 0,
    medalBubbleStartY: 0,

    thermometerIcon: '/images/thermometer-icon.jpg', // Path to the thermometer icon
    thermometerIconAnimation: false, 
    thermometerBubblePosition: {
      x: wx.getWindowInfo().windowWidth - 80, // Initial X position
      y: 200, // Initial Y position
    },
    thermometerBubbleSize: 60, // Icon size
    thermometerBubbleDragging: false, // Dragging state
    thermometerBubbleStartX: 0, // Start X position for dragging
    thermometerBubbleStartY: 0, // Start Y position for dragging
  
    monsterSize: 120,
    moveInterval: null,
    isMoving: false,
    lastMoveTime: 0,
    minMoveInterval: 5000,    // 最小移动间隔改为5秒
    maxMoveInterval: 15000,   // 最大移动间隔改为15秒
    moveStep: 60,             // 基础移动步长
    movementState: 'idle',    // 移动状态：idle, walking, running, resting
    consecutiveMoves: 0,      // 连续移动次数
    maxConsecutiveMoves: 3,   // 最大连续移动次数
    restDuration: 10000,      // 休息时长（毫秒）
    currentEmotion: 'happy',
    currentAnimation: '',
    isDragging: false,
    startX: 0,
    startY: 0,
    animationInterval: null,
    emotionPoints: {
      happy: 0,
      sad: 0,
      angry: 0,
      sleepy: 0
    },
    emotionThreshold: 10,
    earnedMedals: [],
    showMedalReward: false,
    lastRewardMedal: null,
    animationTimeout: null,
    lastAnimationTime: 0,
    minAnimationInterval: 5000, // 最小动画间隔时间（毫秒）
    lastMoveDirection: null,
    keyboardHeight: 0,         // 键盘高度
    windowHeight: wx.getWindowInfo().windowHeight, // 窗口高度
    windowWidth: wx.getWindowInfo().windowWidth,   // 窗口宽度
    isKeyboardVisible: false,  // 键盘是否可见
    session_id: '',
    user_id: '',
  },

  onLoad: function() {
    this.loadChatHistory()
    this.loadMedals()
    // this.startMonsterMovement()
    // this.startMonsterAnimation()
    this.loadEarnedMedals()
    
    // 监听键盘高度变化
    wx.onKeyboardHeightChange(res => {
      this.handleKeyboardHeightChange(res.height)
    })

    // 生成唯一用户ID（如果没有）
    this.initUserID()
  },

  onShow: function() {
    // 页面显示时，检查键盘状态
    const keyboardHeight = wx.getStorageSync('keyboardHeight') || 0
    if (keyboardHeight > 0) {
      this.handleKeyboardHeightChange(keyboardHeight)
    }
  },
  
  onHide: function() {
    // 页面隐藏时，保存键盘高度
    if (this.data.keyboardHeight > 0) {
      wx.setStorageSync('keyboardHeight', this.data.keyboardHeight)
    }
  },

  onUnload: function() {
    // 清理定时器
    if (this.data.moveInterval) {
      clearInterval(this.data.moveInterval)
    }
    if (this.data.animationInterval) {
      clearInterval(this.data.animationInterval)
    }
    
    // 移除键盘高度变化监听
    wx.offKeyboardHeightChange()
  },
  
  // 处理键盘高度变化
  handleKeyboardHeightChange: function(height) {
    const isKeyboardVisible = height > 0
    const windowHeight = wx.getWindowInfo().windowHeight
    
    this.setData({
      keyboardHeight: height,
      isKeyboardVisible: isKeyboardVisible
    })
    
    // 保存键盘高度到存储
    if (height > 0) {
      wx.setStorageSync('keyboardHeight', height)
    } else {
      wx.removeStorageSync('keyboardHeight')
    }
    
    // 如果键盘可见，调整怪物位置确保在可见区域内
    if (isKeyboardVisible) {
      this.adjustMonsterPositionForKeyboard(height)
    }
    
    // 滚动到底部
    this.scrollToBottom()
    
    // 如果键盘可见且没有消息，调整欢迎界面位置
    if (isKeyboardVisible && this.data.messages.length === 0) {
      // 这里不需要额外代码，因为我们已经在CSS中处理了欢迎界面的移动
    }
  },
  
  // 调整怪物位置以适应键盘
  adjustMonsterPositionForKeyboard: function(keyboardHeight) {
    const { monsterPosition, monsterSize, windowHeight, windowWidth } = this.data
    const visibleHeight = windowHeight - keyboardHeight
    
    // 如果怪物在键盘下方，将其移动到可见区域
    if (monsterPosition.y + monsterSize > visibleHeight) {
      const newY = Math.max(100, visibleHeight - monsterSize - 20)
      
      this.setData({
        monsterPosition: {
          x: monsterPosition.x,
          y: newY
        }
      })
    }
  },
  
  // 调整怪物位置以适应窗口大小变化
  adjustMonsterPositionForWindow: function() {
    const { monsterPosition, monsterSize, windowWidth, windowHeight, keyboardHeight } = this.data
    const visibleHeight = windowHeight - keyboardHeight
    
    // 确保怪物在可见区域内
    let newX = monsterPosition.x
    let newY = monsterPosition.y
    
    // 水平方向调整
    if (newX + monsterSize > windowWidth) {
      newX = windowWidth - monsterSize - 20
    }
    
    // 垂直方向调整
    if (newY + monsterSize > visibleHeight) {
      newY = visibleHeight - monsterSize - 20
    }
    
    this.setData({
      monsterPosition: {
        x: newX,
        y: newY
      }
    })
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

  // 加载已获得的勋章
  loadEarnedMedals: function() {
    const earnedMedals = wx.getStorageSync('earnedMedals') || []
    this.setData({ earnedMedals })
  },

  // 保存已获得的勋章
  saveEarnedMedals: function() {
    wx.setStorageSync('earnedMedals', this.data.earnedMedals)
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
      inputMessage: '',
      session_id: '' // 清空会话ID，重新开始对话
    })
    this.closeSidebar()
  },

  // 加载历史对话
  loadChat: function(e) {
    const sessionId = e.currentTarget.dataset.id
    // 先从本地缓存加载对话
    const localChat = this.data.chatHistory.find(item => item.id === sessionId)
    
    if (localChat) {
      this.setData({
        messages: localChat.messages,
        inputMessage: '',
        session_id: sessionId // 设置当前会话ID
      })
      
      // 尝试从服务器获取最新对话记录
      this.fetchChatHistoryFromServer(sessionId)
    } else {
      // 如果本地没有缓存，直接从服务器获取
      this.fetchChatHistoryFromServer(sessionId, true)
    }
    
    this.closeSidebar()
  },

  // 从服务器获取聊天历史记录
  fetchChatHistoryFromServer: function(sessionId, showLoading = false) {
    // 如果需要显示加载中提示
    if (showLoading) {
      wx.showLoading({
        title: '加载中...',
      })
    }
    
    // 调用后端API获取聊天历史
    wx.request({
      url: `${API_BASE_URL}/chat/history`,
      method: 'GET',
      data: {
        user_id: this.data.user_id,
        session_id: sessionId
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.messages && res.data.messages.length > 0) {
          // 将服务器返回的消息格式转换为本地格式
          const formattedMessages = this.formatServerMessages(res.data.messages, sessionId)
          
          this.setData({
            messages: formattedMessages,
            session_id: sessionId
          })
          
          // 滚动到底部显示最新消息
          this.scrollToBottom()
          
          // 更新本地缓存
          this.updateLocalChatHistory(sessionId, formattedMessages)
        }
      },
      fail: (error) => {
        console.error('获取历史记录失败:', error)
        // 失败时不做特殊处理，继续使用本地缓存
      },
      complete: () => {
        if (showLoading) {
          wx.hideLoading()
        }
      }
    })
  },
  
  // 格式化服务器返回的消息
  formatServerMessages: function(serverMessages, sessionId) {
    return serverMessages.map((msg, index) => ({
      id: Date.now() + index, // 生成唯一ID
      type: msg.role === 'user' ? 'user' : 'agent',
      content: msg.content,
      timestamp: msg.timestamp,
      sessionId: sessionId // 添加sessionId到消息中
    }))
  },
  
  // 更新本地聊天历史缓存
  updateLocalChatHistory: function(sessionId, messages) {
    const chatHistory = this.data.chatHistory
    const existingIndex = chatHistory.findIndex(item => item.id === sessionId)
    
    // 创建更新后的聊天对象
    const updatedChat = {
      id: sessionId,
      title: messages.find(msg => msg.type === 'user')?.content.slice(0, 20) + 
             (messages.find(msg => msg.type === 'user')?.content.length > 20 ? '...' : ''),
      time: new Date().toLocaleString(),
      messages: messages,
      lastUpdateTime: new Date().toISOString(),
      messageCount: messages.length,
      user_id: this.data.user_id
    }
    
    if (existingIndex !== -1) {
      // 更新已存在的聊天
      chatHistory[existingIndex] = updatedChat
    } else {
      // 添加新的聊天到列表最前面
      chatHistory.unshift(updatedChat)
    }
    
    // 更新本地存储和状态
    wx.setStorageSync('chatHistory', chatHistory)
    this.setData({ chatHistory })
  },

  // 删除单个对话
  deleteChat: function(e) {
    const sessionId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条对话记录吗？',
      success: (res) => {
        if (res.confirm) {
          // 从聊天历史中过滤掉要删除的对话
          const chatHistory = this.data.chatHistory.filter(item => item.id !== sessionId)
          wx.setStorageSync('chatHistory', chatHistory)
          this.setData({ chatHistory })
          
          // 如果删除的是当前对话，清空消息和会话ID
          if (this.data.session_id === sessionId) {
            this.setData({ 
              messages: [],
              session_id: '' // 清空当前会话ID
            })
          }
          
          wx.showToast({
            title: '已删除',
            icon: 'success'
          })
        }
      }
    })
  },

  // 清除所有对话
  clearAllChats: function() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除所有对话记录吗？此操作不可恢复。',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          // 清除本地存储中的聊天历史
          wx.setStorageSync('chatHistory', [])
          
          // 更新页面状态
          this.setData({
            chatHistory: [],
            messages: [], // 同时清除当前对话
            inputMessage: '',
            session_id: '' // 清空当前会话ID
          })
          
          // 显示成功提示
          wx.showToast({
            title: '已清除全部对话',
            icon: 'success'
          })
          
          // 关闭侧边栏
          this.closeSidebar()
        }
      }
    })
  },

  // 输入框内容变化
  onInputChange: function(e) {
    const text = e.detail.value
    this.setData({ inputMessage: text })
    this.updateMonsterEmotion(text)
  },

  // 发送消息
  sendMessage: function() {
    const content = this.data.inputMessage.trim();
    if (!content) return;

    const timestamp = new Date().toISOString();
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: content,
      timestamp: timestamp,
      sessionId: this.data.session_id || null // 添加会话ID，可能为空
    }

    this.setData({
        messages: [...this.data.messages, newMessage],
        inputMessage: '',
        isLoading: true
    });

    this.scrollToBottom();

    // Prepare history for context
    const history = this.data.messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'agent',
        content: msg.content,
        timestamp: msg.timestamp
    }));

    // Call /chat API
    wx.request({
      url: `${API_BASE_URL}/chat`,
      method: 'POST',
      data: {
        user_id: this.data.user_id,
        session_id: this.data.session_id, // 如果是新对话，可能为空
        message: content,
        timestamp: timestamp,
        history: history
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          // 保存会话ID，用于维持上下文
          const responseSessionId = res.data.session_id
          console.log('Response session ID:', responseSessionId)
          if (responseSessionId) {
            this.setData({
              session_id: responseSessionId
            })
            
            // 更新所有消息的sessionId
            const updatedMessages = this.data.messages.map(msg => ({
              ...msg,
              sessionId: responseSessionId
            }))
            
            const aiResponse = {
              id: Date.now(),
              type: 'agent',
              content: res.data.content,
              timestamp: res.data.timestamp,
              sessionId: responseSessionId
            }

            this.setData({
              messages: [...updatedMessages, aiResponse],
              isLoading: false
            })
          } else {
            // 如果服务器没有返回sessionId，使用响应数据添加消息
            const aiResponse = {
              id: Date.now(),
              type: 'agent',
              content: res.data.content,
              timestamp: res.data.timestamp,
              sessionId: this.data.session_id
            }

            this.setData({
              messages: [...this.data.messages, aiResponse],
              isLoading: false
            })
          }

          // 如果AI响应包含情绪信息，更新小怪物的情绪
          // if (res.data.emotion) {
          //   this.updateMonsterEmotionState(res.data.emotion)
          // }

          this.scrollToBottom()
          // 保存聊天历史
          this.saveChatHistory()
        } else {
          // 处理错误情况
          this.handleApiError(res)
        }
      },
      fail: (error) => {
        console.error('API请求失败:', error)
        this.handleApiError()
      }
    })

    // Call /mood API

    // 获取最近N条用户消息内容，批量情绪分析
    const recentUserMessages = getRecentMessages(
      [...this.data.messages, newMessage].filter(m => m.type === 'user'), 
      7
    ).map(m => m.content);
    this.fetchMoodAnalysis(recentUserMessages);
    // this.fetchMoodAnalysis(content);
  },

  // Fetch mood analysis and make the thermometer icon flicker
  fetchMoodAnalysis: function(messages) {
    wx.request({
      url: `${API_BASE_URL}/mood`,
      method: 'POST',
      data: {
          user_id: this.data.user_id,
          session_id: this.data.session_id,
          messages: [messages]
      },
      header: {
          'content-type': 'application/json'
      },
      success: (res) => {
          if (res.statusCode === 200 && res.data) {
              const newMood = res.data;
              const lastMood = this.data.moodData;

              // 只在情绪强度大于0.8且类别发生变化时才更新
              if (
                newMood.moodIntensity > 0.8 &&
                (!lastMood || newMood.moodCategory !== lastMood.moodCategory)
              ) {
                  this.setData({
                      moodData: newMood,
                      // 让温度计图标闪烁/高亮
                      thermometerIconAnimation: true
                  });
                  // 3秒后关闭动画
                  setTimeout(() => {
                    this.setData({ thermometerIconAnimation: false });
                  }, 5000);
              }
              // 否则不更新
          } else {
              wx.showToast({
                  title: 'Failed to fetch mood data',
                  icon: 'none'
              });
          }
      },
      fail: (error) => {
          console.error('Mood API request failed:', error);
          wx.showToast({
              title: 'Request failed',
              icon: 'none'
          });
      }
    });
  },

  // 处理API错误
  handleApiError: function(res) {
    let errorMsg = '网络连接错误，请稍后再试'
    
    if (res && res.data && res.data.error_message) {
      errorMsg = res.data.error_message
    }

    const aiResponse = {
      id: Date.now(),
      type: 'agent',
      content: `抱歉，我遇到了一些问题：${errorMsg}`,
      timestamp: new Date().toISOString(),
      sessionId: this.data.session_id // 添加当前会话ID
    }

    this.setData({
      messages: [...this.data.messages, aiResponse],
      isLoading: false
    })

    this.scrollToBottom()
    this.saveChatHistory()

    wx.showToast({
      title: '连接失败',
      icon: 'none'
    })
  },

  // 更新小怪物情绪状态（基于API返回的情绪）
  updateMonsterEmotionState: function(emotion) {
    if (['happy', 'sad', 'angry', 'sleepy', 'neutral'].includes(emotion)) {
      this.setData({
        currentEmotion: emotion
      })
      
      // 根据情绪触发相应的动画
      switch(emotion) {
        case 'happy':
          this.playAnimation('bounce')
          break
        case 'sad':
          this.playAnimation('shake')
          break
        case 'angry':
          this.playAnimation('pulse')
          break
        case 'sleepy':
          this.playAnimation('wobble')
          break
        default:
          this.playAnimation('idle')
      }
    }
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
      // 使用服务器返回的 session_id，如果没有则使用本地生成的ID
      const sessionId = this.data.session_id || Date.now().toString()
      
      // 创建聊天记录对象
      const chat = {
        id: sessionId,
        // 使用第一条用户消息作为标题，截取前20个字符
        title: messages.find(msg => msg.type === 'user')?.content.slice(0, 20) + 
               (messages.find(msg => msg.type === 'user')?.content.length > 20 ? '...' : ''),
        time: new Date().toLocaleString(),
        messages: messages,
        // 添加更多有用信息
        lastUpdateTime: new Date().toISOString(),
        messageCount: messages.length,
        user_id: this.data.user_id
      }

      let chatHistory = this.data.chatHistory
      const existingIndex = chatHistory.findIndex(item => item.id === sessionId)
      
      if (existingIndex !== -1) {
        // 更新已存在的聊天记录
        chatHistory[existingIndex] = chat
      } else {
        // 添加新的聊天记录到列表最前面
        chatHistory = [chat, ...chatHistory]
      }

      // 保存到本地缓存
      wx.setStorageSync('chatHistory', chatHistory)
      this.setData({ 
        chatHistory,
        session_id: sessionId  // 确保session_id被设置
      })
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

  // Navigate to Mood Score page
  navigateToMoodScore: function () {
    if (!this.data.thermometerIconDragging) {
      wx.navigateTo({
        url: '/pages/mood_score/index', // Replace with the actual path to the Mood Score page
        success: function () {
          console.log('Successfully navigated to Mood Score page');
        },
        fail: function (error) {
          console.error('Failed to navigate to Mood Score page:', error);
          wx.showToast({
            title: 'Navigation failed, please try again',
            icon: 'none',
          });
        },
      });
    }
  },
 
  // 开始怪物随机移动
  startMonsterMovement: function() {
    // 清除现有的移动间隔
    if (this.data.moveInterval) {
      clearInterval(this.data.moveInterval)
    }

    // 设置新的移动检查间隔
    const moveInterval = setInterval(() => {
      if (!this.data.isDragging && !this.data.isMoving) {
        const now = Date.now()
        const { lastMoveTime, minMoveInterval, maxMoveInterval, movementState } = this.data
        
        // 如果在休息状态，不执行移动
        if (movementState === 'resting') {
          return
        }

        // 根据情绪调整移动间隔
        let actualMinInterval = minMoveInterval
        let actualMaxInterval = maxMoveInterval

        switch (this.data.currentEmotion) {
          case 'happy':
            // 开心时更频繁地移动
            actualMinInterval *= 0.8
            actualMaxInterval *= 0.8
            break
          case 'sad':
            // 悲伤时移动频率降低
            actualMinInterval *= 1.5
            actualMaxInterval *= 1.5
            break
          case 'angry':
            // 生气时移动更频繁
            actualMinInterval *= 0.6
            actualMaxInterval *= 0.6
            break
          case 'sleepy':
            // 困倦时移动频率大幅降低
            actualMinInterval *= 2
            actualMaxInterval *= 2
            break
        }
        
        // 随机决定是否移动
        const randomInterval = Math.random() * (actualMaxInterval - actualMinInterval) + actualMinInterval
        
        if (now - lastMoveTime > randomInterval) {
          this.performRandomMove()
        }
      }
    }, 1000) // 每秒检查一次是否需要移动

    this.setData({ moveInterval })
  },

  // 执行随机移动
  performRandomMove: function() {
    // 如果正在休息，不执行移动
    if (this.data.movementState === 'resting') {
      return
    }

    const windowWidth = wx.getWindowInfo().windowWidth
    const windowHeight = wx.getWindowInfo().windowHeight
    const { monsterSize, moveStep, currentEmotion, keyboardHeight } = this.data
    const margin = 20 // 统一设置所有方向的边距
    const visibleHeight = windowHeight - keyboardHeight

    // 获取当前位置
    let { x, y } = this.data.monsterPosition

    // 根据情绪调整移动步长和动画
    let actualMoveStep = moveStep
    let moveAnimation = 'walking'
    
    switch (currentEmotion) {
      case 'happy':
        // 开心时移动更活跃，步长稍大
        actualMoveStep = moveStep * 1.2
        moveAnimation = Math.random() > 0.5 ? 'jumping' : 'walking'
        break
      case 'sad':
        // 悲伤时移动缓慢
        actualMoveStep = moveStep * 0.6
        moveAnimation = 'walking'
        break
      case 'angry':
        // 生气时移动迅速
        actualMoveStep = moveStep * 1.5
        moveAnimation = 'running'
        break
      case 'sleepy':
        // 困倦时移动非常缓慢
        actualMoveStep = moveStep * 0.4
        moveAnimation = 'walking'
        break
    }

    // 随机选择移动方向（增加连续同向移动的概率）
    const directions = []
    const lastMove = this.data.lastMoveDirection
    
    if (lastMove) {
      // 60%概率保持同向
      if (Math.random() < 0.6) {
        directions.push(lastMove)
      }
    }

    // 添加其他可能的方向
    directions.push(
      { dx: actualMoveStep, dy: 0 },    // 右
      { dx: -actualMoveStep, dy: 0 },   // 左
      { dx: 0, dy: actualMoveStep },    // 下
      { dx: 0, dy: -actualMoveStep }    // 上
    )
    
    // 随机选择一个方向
    const randomDir = directions[Math.floor(Math.random() * directions.length)]
    
    // 计算新位置
    let newX = x + randomDir.dx
    let newY = y + randomDir.dy

    // 统一边界检查逻辑，所有方向使用相同的边距
    newX = Math.max(margin, Math.min(windowWidth - monsterSize - margin, newX))
    newY = Math.max(margin, Math.min(visibleHeight - monsterSize - margin, newY))

    // 记录这次的移动方向
    this.setData({ lastMoveDirection: randomDir })

    // 更新连续移动次数
    const consecutiveMoves = this.data.consecutiveMoves + 1
    
    // 检查是否需要休息
    if (consecutiveMoves >= this.data.maxConsecutiveMoves) {
      this.setData({
        movementState: 'resting',
        consecutiveMoves: 0
      })
      
      // 休息一段时间后恢复移动
      setTimeout(() => {
        this.setData({ 
          movementState: 'idle',
          currentAnimation: 'wiggling' // 休息结束时伸个懒腰
        })
        
        setTimeout(() => {
          this.setData({ currentAnimation: '' })
        }, 1000)
      }, this.data.restDuration)
    } else {
      this.setData({ consecutiveMoves })
    }

    // 标记开始移动
    this.setData({ 
      isMoving: true,
      lastMoveTime: Date.now(),
      currentAnimation: moveAnimation,
      monsterPosition: {
        x: newX,
        y: newY
      }
    })

    // 移动和动画结束后重置状态
    const animationDuration = moveAnimation === 'running' ? 800 : 1200
    setTimeout(() => {
      this.setData({
        isMoving: false,
        currentAnimation: ''
      })
    }, animationDuration)
  },

  // 开始怪物随机动画
  startMonsterAnimation: function() {
    // 清除现有的动画间隔
    if (this.data.animationInterval) {
      clearInterval(this.data.animationInterval)
    }
    
    // 设置新的动画间隔
    const animationInterval = setInterval(() => {
      this.triggerRandomAnimation()
    }, 8000) // 每8秒尝试触发一次随机动画
    
    this.setData({ animationInterval })
  },

  // 触发随机动画
  triggerRandomAnimation: function() {
    const now = Date.now()
    const { lastAnimationTime, minAnimationInterval } = this.data
    
    // 检查是否满足最小动画间隔
    if (now - lastAnimationTime < minAnimationInterval) {
      return
    }
    
    // 如果正在拖动，不触发动画
    if (this.data.isDragging) {
      return
    }
    
    // 可用的动画列表
    const animations = ['jumping', 'wiggling', 'spinning']
    
    // 根据当前情绪增加特定动画的权重
    if (this.data.currentEmotion === 'happy') {
      animations.push('jumping', 'spinning') // 开心时更容易跳跃和旋转
    } else if (this.data.currentEmotion === 'sleepy') {
      animations.push('wiggling', 'wiggling') // 困倦时更容易摇摆
    }
    
    // 随机选择一个动画
    const randomAnimation = animations[Math.floor(Math.random() * animations.length)]
    
    // 清除之前的超时器
    if (this.data.animationTimeout) {
      clearTimeout(this.data.animationTimeout)
    }
    
    // 设置新的动画
    this.setData({
      currentAnimation: randomAnimation,
      lastAnimationTime: now
    })
    
    // 设置动画持续时间
    const animationDuration = randomAnimation === 'spinning' ? 1500 : 1000
    const animationTimeout = setTimeout(() => {
      this.setData({ currentAnimation: '' })
    }, animationDuration)
    
    this.setData({ animationTimeout })
  },

  // 模拟获取情绪反馈的API
  getEmotionFeedback: function(text) {
    // 模拟API调用延迟
    return new Promise((resolve) => {
      setTimeout(() => {
        // 模拟情绪分析结果
        const emotions = ['happy', 'sad', 'angry', 'sleepy']
        const randomEmotion = emotions[Math.floor(Math.random() * emotions.length)]
        
        // 根据文本内容增加特定情绪的概率
        let emotion = randomEmotion
        if (text.includes('?') || text.includes('？')) {
          emotion = Math.random() > 0.5 ? 'sleepy' : randomEmotion
        } else if (text.includes('!') || text.includes('！')) {
          emotion = Math.random() > 0.5 ? 'angry' : randomEmotion
        } else if (text.includes('...') || text.includes('。。。')) {
          emotion = Math.random() > 0.5 ? 'sad' : randomEmotion
        } else if (text.includes('谢谢') || text.includes('感谢')) {
          emotion = Math.random() > 0.5 ? 'happy' : randomEmotion
        }
        
        resolve(emotion)
      }, 500)
    })
  },

  // 更新怪物情绪并累积情绪点
  updateMonsterEmotion: function(text) {
    if (!text || text.trim() === '') return
    
    // 调用模拟API获取情绪反馈
    this.getEmotionFeedback(text).then(emotion => {
      // 如果情绪发生变化，触发过渡动画
      if (emotion !== this.data.currentEmotion) {
        // 先清除当前动画
        this.setData({ currentAnimation: '' })
        
        // 短暂延迟后设置新情绪，让过渡更自然
        setTimeout(() => {
          this.setData({ currentEmotion: emotion })
          
          // 根据新情绪触发对应的动画
          if (emotion === 'happy') {
            this.triggerRandomAnimation()
          }
        }, 100)
      }
      
      // 累积情绪点
      const emotionPoints = { ...this.data.emotionPoints }
      emotionPoints[emotion] += 1
      
      this.setData({ emotionPoints })
      
      // 检查是否达到阈值并奖励勋章
      this.checkEmotionThreshold(emotion)
    })
  },

  // 检查情绪阈值并奖励勋章
  checkEmotionThreshold: function(emotion) {
    const { emotionPoints, emotionThreshold, earnedMedals, medals } = this.data
    
    // 检查是否达到阈值
    if (emotionPoints[emotion] >= emotionThreshold) {
      // 查找未获得的对应情绪勋章
      const availableMedals = medals.filter(medal => {
        // 根据情绪类型匹配勋章
        const isEmotionMatch = 
          (emotion === 'happy' && medal.name.includes('活跃')) ||
          (emotion === 'sad' && medal.name.includes('新手')) ||
          (emotion === 'angry' && medal.name.includes('专家')) ||
          (emotion === 'sleepy' && medal.name.includes('新手'))
        
        // 检查是否已获得
        const isAlreadyEarned = earnedMedals.some(earned => earned.id === medal.id)
        
        return isEmotionMatch && !isAlreadyEarned
      })
      
      if (availableMedals.length > 0) {
        // 随机选择一个勋章
        const rewardMedal = availableMedals[Math.floor(Math.random() * availableMedals.length)]
        
        // 添加到已获得勋章列表
        const newEarnedMedals = [...earnedMedals, rewardMedal]
        
        // 更新状态
        this.setData({
          earnedMedals: newEarnedMedals,
          showMedalReward: true,
          lastRewardMedal: rewardMedal
        })
        
        // 保存到本地存储
        this.saveEarnedMedals()
        
        // 重置该情绪的点数
        emotionPoints[emotion] = 0
        this.setData({ emotionPoints })
        
        // 3秒后隐藏奖励提示
        setTimeout(() => {
          this.setData({ showMedalReward: false })
        }, 3000)
      }
    }
  },

  // 触摸开始
  touchStart: function(e) {
    // 使用微信小程序的事件处理方法
    if (e && e.type === 'touchstart') {
      e.preventDefault && e.preventDefault()
    }

    const windowWidth = wx.getWindowInfo().windowWidth
    const windowHeight = wx.getWindowInfo().windowHeight
    const { monsterSize, keyboardHeight } = this.data
    const margin = 20 // 统一设置所有方向的边距
    const visibleHeight = windowHeight - keyboardHeight

    // 获取当前位置
    let currentX = this.data.monsterPosition.x
    let currentY = this.data.monsterPosition.y

    // 统一边界检查逻辑，所有方向使用相同的边距
    // 确保小怪物不会超出屏幕边界
    // Math.max(margin,...) 确保不小于左/上边距
    // Math.min(..., windowWidth/visibleHeight - monsterSize - margin) 确保不超过右/下边距
    currentX = Math.max(margin, Math.min(windowWidth - monsterSize - margin, currentX))
    currentY = Math.max(margin, Math.min(visibleHeight - monsterSize - margin, currentY))

    this.setData({
      isDragging: true,
      currentAnimation: '', // 清除当前动画
      isMoving: false,     // 停止自动移动
      monsterPosition: {
        x: currentX,
        y: currentY
      },
      startX: e.touches[0].clientX - currentX,
      startY: e.touches[0].clientY - currentY
    })
  },

  // 触摸移动
  touchMove: function(e) {
    // 使用微信小程序的事件处理方法
    if (e && e.type === 'touchmove') {
      e.preventDefault && e.preventDefault()
    }

    if (this.data.isDragging) {
      const windowWidth = wx.getWindowInfo().windowWidth
      const windowHeight = wx.getWindowInfo().windowHeight
      const { monsterSize, keyboardHeight } = this.data
      const margin = 20 // 统一设置所有方向的边距
      const visibleHeight = windowHeight - keyboardHeight

      // 计算新位置
      let newX = e.touches[0].clientX - this.data.startX
      let newY = e.touches[0].clientY - this.data.startY

      // 统一边界检查逻辑，所有方向使用相同的边距
      // 确保小怪物不会超出屏幕边界
      // Math.max(margin,...) 确保不小于左/上边距
      // Math.min(..., windowWidth/visibleHeight - monsterSize - margin) 确保不超过右/下边距
      newX = Math.max(margin, Math.min(windowWidth - monsterSize - margin, newX))
      newY = Math.max(margin, Math.min(visibleHeight - monsterSize - margin, newY))
      
      this.setData({
        monsterPosition: {
          x: newX,
          y: newY
        }
      })
    }
  },

  // 触摸结束
  touchEnd: function(e) {
    // 使用微信小程序的事件处理方法
    if (e && e.type === 'touchend') {
      e.preventDefault && e.preventDefault()
    }

    this.setData({
      isDragging: false,
      lastMoveTime: Date.now() // 重置最后移动时间，避免刚放下就自动移动
    })
    
    // 拖动结束后，延迟一段时间再恢复随机动画
    setTimeout(() => {
      if (!this.data.isDragging) {
        this.triggerRandomAnimation()
      }
    }, 1000)
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
  },

  // 勋章气泡触摸开始
  medalBubbleTouchStart: function(e) {
    if (e && e.type === 'touchstart') {
      e.preventDefault && e.preventDefault()
    }

    const windowWidth = wx.getWindowInfo().windowWidth
    const windowHeight = wx.getWindowInfo().windowHeight
    const { medalBubbleSize, keyboardHeight } = this.data
    const margin = 10 // 边距
    const visibleHeight = windowHeight - keyboardHeight

    // 获取当前位置
    let currentX = this.data.medalBubblePosition.x
    let currentY = this.data.medalBubblePosition.y

    // 边界检查
    currentX = Math.max(margin, Math.min(windowWidth - medalBubbleSize - margin, currentX))
    currentY = Math.max(margin, Math.min(visibleHeight - medalBubbleSize - margin, currentY))

    this.setData({
      medalBubbleDragging: true,
      medalBubblePosition: {
        x: currentX,
        y: currentY
      },
      medalBubbleStartX: e.touches[0].clientX - currentX,
      medalBubbleStartY: e.touches[0].clientY - currentY
    })
  },

  // 勋章气泡触摸移动
  medalBubbleTouchMove: function(e) {
    if (e && e.type === 'touchmove') {
      e.preventDefault && e.preventDefault()
    }

    if (this.data.medalBubbleDragging) {
      const windowWidth = wx.getWindowInfo().windowWidth
      const windowHeight = wx.getWindowInfo().windowHeight
      const { medalBubbleSize, keyboardHeight } = this.data
      const margin = 10 // 边距
      const visibleHeight = windowHeight - keyboardHeight

      // 计算新位置
      let newX = e.touches[0].clientX - this.data.medalBubbleStartX
      let newY = e.touches[0].clientY - this.data.medalBubbleStartY

      // 边界检查
      newX = Math.max(margin, Math.min(windowWidth - medalBubbleSize - margin, newX))
      newY = Math.max(margin, Math.min(visibleHeight - medalBubbleSize - margin, newY))
      
      this.setData({
        medalBubblePosition: {
          x: newX,
          y: newY
        }
      })
    }
  },

  // 勋章气泡触摸结束
  medalBubbleTouchEnd: function(e) {
    if (e && e.type === 'touchend') {
      e.preventDefault && e.preventDefault()
    }

    this.setData({
      medalBubbleDragging: false
    })
  },

  // 勋章气泡点击
  onMedalBubbleTap: function() {
    if (!this.data.medalBubbleDragging) {
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

  // 初始化用户ID
  initUserID: function() {
    let userId = wx.getStorageSync('user_id')
    if (!userId) {
      userId = 'user_' + Date.now() + Math.floor(Math.random() * 1000)
      wx.setStorageSync('user_id', userId)
    }
    this.setData({ user_id: userId })
  },

  // Navigate to Mood Score page with data
  onThermometerBubbleTap: function() {
    if (!this.data.thermometerBubbleDragging) {
        wx.navigateTo({
            url: `/pages/mood_score/index?data=${encodeURIComponent(JSON.stringify(this.data.moodData))}`,
            success: function() {
                console.log('Successfully navigated to Mood Score page');
            },
            fail: function(error) {
                console.error('Failed to navigate to Mood Score page:', error);
                wx.showToast({
                    title: 'Navigation failed, please try again',
                    icon: 'none'
                });
            }
        });
    }
  },

  // Touch start for thermometer icon
  thermometerIconTouchStart: function (e) {
    const { thermometerIconPosition } = this.data;

    this.setData({
      thermometerIconDragging: true,
      thermometerIconStartX: e.touches[0].clientX - thermometerIconPosition.x,
      thermometerIconStartY: e.touches[0].clientY - thermometerIconPosition.y,
    });
  },

  // Touch move for thermometer icon
  thermometerIconTouchMove: function (e) {
    if (this.data.thermometerIconDragging) {
      const windowWidth = wx.getWindowInfo().windowWidth;
      const windowHeight = wx.getWindowInfo().windowHeight;
      const { thermometerIconSize } = this.data;

      let newX = e.touches[0].clientX - this.data.thermometerIconStartX;
      let newY = e.touches[0].clientY - this.data.thermometerIconStartY;

      // Boundary checks
      newX = Math.max(0, Math.min(windowWidth - thermometerIconSize, newX));
      newY = Math.max(0, Math.min(windowHeight - thermometerIconSize, newY));

      this.setData({
        thermometerIconPosition: {
          x: newX,
          y: newY,
        },
      });
    }
  },

  // Touch end for thermometer icon
  thermometerIconTouchEnd: function () {
    this.setData({
      thermometerIconDragging: false,
    });
  },

  // 跳转到事件分析页面
  navigateToEvents() {
    wx.navigateTo({
      url: '/pages/events/index'
    })
  },

    
  
})