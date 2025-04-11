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
  },

  onLoad: function() {
    this.loadChatHistory()
    this.loadMedals()
    this.startMonsterMovement()
    this.startMonsterAnimation()
    this.loadEarnedMedals()
    
    // 监听键盘高度变化
    wx.onKeyboardHeightChange(res => {
      this.handleKeyboardHeightChange(res.height)
    })
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

  // 删除单个对话
  deleteChat: function(e) {
    const chatId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条对话记录吗？',
      success: (res) => {
        if (res.confirm) {
          // 从聊天历史中过滤掉要删除的对话
          const chatHistory = this.data.chatHistory.filter(item => item.id !== chatId)
          wx.setStorageSync('chatHistory', chatHistory)
          this.setData({ chatHistory })
          
          // 如果删除的是当前对话，清空消息
          if (this.data.messages.length > 0 && this.data.messages[0].chatId === chatId) {
            this.setData({ messages: [] })
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
            inputMessage: ''
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
}) 