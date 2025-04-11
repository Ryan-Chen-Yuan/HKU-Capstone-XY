# 知己AI助手小程序模块功能与接口设定

## 1. 主页面模块 (pages/index)

### 1.1 核心功能
- **智能对话系统**：支持用户与AI助手进行文本对话
- **动态角色系统**：可交互的"小怪兽"角色，具有情绪和动画
- **历史记录管理**：保存和加载聊天历史
- **勋章系统集成**：通过互动解锁勋章

### 1.2 数据接口
```javascript
data: {
  showSidebar: false,          // 侧边栏显示状态
  messages: [],                // 聊天消息列表
  inputMessage: '',            // 输入框内容
  isLoading: false,            // 加载状态
  scrollToMessage: '',         // 滚动到指定消息
  chatHistory: [],             // 聊天历史记录
  userInfo: {},                // 用户信息
  medals: [...],               // 勋章列表
  monsterPosition: {...},      // 怪物位置
  monsterSize: 120,            // 怪物大小
  currentEmotion: 'happy',     // 当前情绪
  emotionPoints: {...},        // 情绪点数
  earnedMedals: [],            // 已获得的勋章
  // ... 其他状态
}
```

### 1.3 主要接口
- **消息发送**：`sendMessage()`
- **历史记录加载**：`loadChatHistory()`
- **历史记录保存**：`saveChatHistory()`
- **怪物移动控制**：`startMonsterMovement()`, `performRandomMove()`
- **怪物动画控制**：`startMonsterAnimation()`, `triggerRandomAnimation()`
- **情绪系统**：`updateMonsterEmotion()`, `checkEmotionThreshold()`
- **触摸事件处理**：`touchStart()`, `touchMove()`, `touchEnd()`
- **键盘高度适配**：`handleKeyboardHeightChange()`

## 2. 登录模块 (pages/login)

### 2.1 核心功能
- **用户授权**：获取用户基本信息
- **登录状态管理**：处理登录流程和状态
- **导航控制**：登录成功后跳转到主页

### 2.2 数据接口
```javascript
data: {
  isLoading: false  // 加载状态
}
```

### 2.3 主要接口
- **登录处理**：`handleLogin()`
- **返回处理**：`handleBack()`
- **导航控制**：`navigateToHome()`

## 3. 勋章模块 (pages/medals)

### 3.1 核心功能
- **勋章展示**：显示用户已获得和未获得的勋章
- **勋章详情**：查看勋章详细信息和解锁条件
- **进度追踪**：显示勋章解锁进度
- **动画效果**：勋章解锁时的动画效果

### 3.2 数据接口
```javascript
data: {
  medals: [...],               // 勋章列表
  selectedMedal: null,         // 选中的勋章
  showDetailModal: false,      // 详情模态框显示状态
  currentMedal: null,          // 当前查看的勋章
  showDetail: false,           // 详情显示状态
  medalAnimations: []          // 勋章动画状态
}
```

### 3.3 主要接口
- **勋章数据加载**：`onLoad()`
- **勋章详情显示**：`showMedalDetail()`
- **勋章动画控制**：`playMedalAnimation()`
- **页面生命周期**：`onShow()`, `onHide()`, `onUnload()`

## 4. 个人中心模块 (pages/profile)

### 4.1 核心功能
- **用户信息展示**：显示用户头像、昵称和ID
- **功能导航**：提供各种功能入口
- **勋章预览**：显示用户已获得的勋章
- **设置管理**：提供各种设置选项

### 4.2 数据接口
```javascript
data: {
  userInfo: {
    avatarUrl: '/images/default-avatar.png',
    nickName: '用户'
  },
  userId: '',                  // 用户ID
  hasUserInfo: false,          // 是否有用户信息
  medals: []                   // 勋章列表
}
```

### 4.3 主要接口
- **用户ID生成**：`generateRandomUserId()`
- **登录处理**：`handleLogin()`
- **勋章数据获取**：`getMedals()`
- **导航控制**：`navigateBack()`, `navigateToHistory()`, `navigateToSettings()`, `navigateToAbout()`, `navigateToFeedback()`

## 5. 应用全局模块 (app.js)

### 5.1 核心功能
- **全局状态管理**：管理用户登录状态和信息
- **登录接口**：提供登录和用户信息获取方法
- **全局数据共享**：在不同页面间共享数据

### 5.2 数据接口
```javascript
globalData: {
  userInfo: null,              // 用户信息
  isLoggedIn: false            // 登录状态
}
```

### 5.3 主要接口
- **登录状态检查**：`checkLoginStatus()`
- **登录处理**：`login()`
- **用户信息获取**：`getUserInfo()`
- **登出处理**：`logout()`

## 6. 动态角色系统

### 6.1 核心功能
- **位置管理**：控制角色在屏幕上的位置
- **动画系统**：提供多种动画状态（idle, walking, running, resting）
- **情绪系统**：基于用户输入动态调整角色情绪
- **交互响应**：支持拖拽和自动移动

### 6.2 数据接口
```javascript
// 角色位置和大小
monsterPosition: {
  x: wx.getWindowInfo().windowWidth - 120,
  y: 120
},
monsterSize: 120,

// 移动控制
moveInterval: null,
isMoving: false,
lastMoveTime: 0,
minMoveInterval: 5000,
maxMoveInterval: 15000,
moveStep: 60,
movementState: 'idle',
consecutiveMoves: 0,
maxConsecutiveMoves: 3,
restDuration: 10000,

// 情绪系统
currentEmotion: 'happy',
emotionPoints: {
  happy: 0,
  sad: 0,
  angry: 0,
  sleepy: 0
},
emotionThreshold: 10,

// 动画控制
currentAnimation: '',
animationInterval: null,
animationTimeout: null,
lastAnimationTime: 0,
minAnimationInterval: 5000,
lastMoveDirection: null
```

### 6.3 主要接口
- **移动控制**：`startMonsterMovement()`, `performRandomMove()`
- **动画控制**：`startMonsterAnimation()`, `triggerRandomAnimation()`
- **情绪系统**：`updateMonsterEmotion()`, `checkEmotionThreshold()`
- **触摸事件处理**：`touchStart()`, `touchMove()`, `touchEnd()`
- **位置调整**：`adjustMonsterPositionForWindow()`, `adjustMonsterPositionForKeyboard()`

## 7. 聊天系统

### 7.1 核心功能
- **消息发送和接收**：支持文本消息的发送和接收
- **历史记录管理**：保存和加载聊天历史
- **自动滚动**：新消息自动滚动到底部
- **输入控制**：支持键盘高度自适应

### 7.2 数据接口
```javascript
messages: [],                // 聊天消息列表
inputMessage: '',            // 输入框内容
isLoading: false,            // 加载状态
scrollToMessage: '',         // 滚动到指定消息
chatHistory: [],             // 聊天历史记录
keyboardHeight: 0,           // 键盘高度
isKeyboardVisible: false     // 键盘是否可见
```

### 7.3 主要接口
- **消息发送**：`sendMessage()`
- **历史记录加载**：`loadChatHistory()`
- **历史记录保存**：`saveChatHistory()`
- **滚动控制**：`scrollToBottom()`
- **键盘高度适配**：`handleKeyboardHeightChange()`

## 8. 勋章系统

### 8.1 核心功能
- **勋章解锁**：通过特定条件解锁勋章
- **进度追踪**：显示勋章解锁进度
- **奖励展示**：解锁勋章时的奖励展示
- **数据持久化**：保存勋章解锁状态

### 8.2 数据接口
```javascript
medals: [...],               // 勋章列表
earnedMedals: [],            // 已获得的勋章
showMedalReward: false,      // 显示勋章奖励
lastRewardMedal: null,       // 最后获得的勋章
emotionPoints: {...},        // 情绪点数
emotionThreshold: 10         // 情绪阈值
```

### 8.3 主要接口
- **勋章数据加载**：`loadMedals()`, `loadEarnedMedals()`
- **勋章数据保存**：`saveEarnedMedals()`
- **勋章解锁检查**：`checkEmotionThreshold()`
- **勋章奖励展示**：`showMedalReward()`

## 9. 数据存储系统

### 9.1 核心功能
- **本地存储**：使用微信小程序的存储API保存数据
- **数据持久化**：确保数据在应用重启后仍然可用
- **数据同步**：在不同页面间同步数据

### 9.2 存储数据类型
- **用户信息**：`userInfo`
- **聊天历史**：`chatHistory`
- **勋章数据**：`earnedMedals`
- **键盘高度**：`keyboardHeight`

### 9.3 主要接口
- **数据保存**：`wx.setStorageSync()`
- **数据读取**：`wx.getStorageSync()`
- **数据删除**：`wx.removeStorageSync()`

## 10. 页面导航系统

### 10.1 核心功能
- **页面跳转**：在不同页面间进行导航
- **参数传递**：在页面跳转时传递参数
- **返回控制**：处理返回按钮和手势

### 10.2 主要接口
- **页面跳转**：`wx.navigateTo()`, `wx.redirectTo()`, `wx.switchTab()`
- **页面返回**：`wx.navigateBack()`
- **页面重载**：`wx.reLaunch()`

## 11. 样式系统

### 11.1 核心功能
- **响应式布局**：适配不同屏幕尺寸
- **主题样式**：统一的配色和样式
- **动画效果**：流畅的过渡动画
- **组件样式**：统一的组件样式

### 11.2 主要样式文件
- **全局样式**：`app.wxss`
- **页面样式**：`pages/*/index.wxss`
- **组件样式**：`components/*/index.wxss`

## 12. 工具函数

### 12.1 核心功能
- **图片压缩**：`compress-images.js`
- **图标生成**：`create-icons.js`
- **数据格式化**：日期、时间等格式化
- **工具函数**：各种辅助函数

### 12.2 主要工具
- **图片压缩工具**：`compress-images.js`
- **图标生成工具**：`create-icons.js`
