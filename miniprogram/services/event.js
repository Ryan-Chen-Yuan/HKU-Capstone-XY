import API from './api.js';

// Mock事件数据 (保留作为fallback)
const mockEvents = [
  {
    id: '1',
    primaryType: 'emotional',
    subType: 'emotionalLow',
    title: '情绪低落',
    content: '感到特别焦虑和沮丧，无法控制自己的情绪波动',
    time: '2024-04-05 10:30',
    dialogContent: '最近我经常感到莫名的焦虑，特别是晚上一个人的时候，有时候会突然很沮丧，控制不住情绪。',
    sourceDialogId: 'dialog_001',  
    status: 'pending',
    tagColor: '#4192FF',
    createTime: '2024-04-05 10:30',
    updateTime: '2024-04-05 10:30'
  },
  {
    id: '2',
    primaryType: 'cognitive',
    subType: 'positiveThinking',  
    title: '积极思考',
    content: '回顾过去的成功经历，增强自信心',
    time: '2024-04-05 14:20',
    dialogContent: '我回想起去年那次成功的面试经历，这让我意识到只要努力准备，我完全有能力达成目标。这次经历给了我很大的信心。',
    sourceDialogId: 'dialog_002',
    status: 'pending',
    tagColor: '#9C27B0',
    createTime: '2024-04-05 14:20',
    updateTime: '2024-04-05 14:20'
  },
  {
    id: '3',
    primaryType: 'interpersonal',
    subType: 'conflict',
    title: '人际冲突',
    content: '与室友因生活习惯发生争执，感到被误解',
    time: '2024-04-06 09:15',
    dialogContent: '昨天我和室友又因为房间整理的事情吵架了，她总是认为我太挑剔，但我只是希望有个干净的环境。',
    sourceDialogId: 'dialog_003',
    status: 'pending',
    tagColor: '#4CAF50',
    createTime: '2024-04-06 09:15',
    updateTime: '2024-04-06 09:15'
  },
  {
    id: '4',
    primaryType: 'behavioral',
    subType: 'avoidance',
    title: '回避行为',
    content: '找借口推掉朋友聚会邀请，选择独处',
    time: '2024-04-06 16:40',
    dialogContent: '周末朋友邀请我去参加生日聚会，但我编了个加班的理由拒绝了，其实我只是害怕在人多的场合。',
    sourceDialogId: 'dialog_004',
    status: 'pending',
    tagColor: '#FF9800',
    createTime: '2024-04-06 16:40',
    updateTime: '2024-04-06 16:40'
  },
  {
    id: '5',
    primaryType: 'physiological',
    subType: 'sleepIssues',
    title: '睡眠问题',
    content: '连续三晚难以入睡，凌晨常常醒来',
    time: '2024-04-07 07:30',
    dialogContent: '这几天我睡得很不好，总是要躺很久才能入睡，而且半夜经常惊醒，感觉特别疲惫。',
    sourceDialogId: 'dialog_005',
    status: 'pending',
    tagColor: '#F44336',
    createTime: '2024-04-07 07:30',
    updateTime: '2024-04-07 07:30'
  },
  {
    id: '6',
    primaryType: 'lifeEvent',
    subType: 'transition',
    title: '生活转变',
    content: '考虑接受新城市的工作机会，但担心适应问题',
    time: '2024-04-07 15:20',
    dialogContent: '我收到了北京一家公司的offer，薪资很诱人，但我从没离开过家乡，不知道自己能否适应新环境。',
    sourceDialogId: 'dialog_006',
    status: 'pending',
    tagColor: '#FFC107',
    createTime: '2024-04-07 15:20',
    updateTime: '2024-04-07 15:20'
  }
];

// 配置是否使用Mock数据
const USE_MOCK = false; // 设为true使用Mock，false使用真实API

// 事件服务类
class EventService {
  constructor() {
    this.sessionId = null; // 当前会话ID
    
    if (USE_MOCK) {
      // Mock模式：初始化本地存储
      try {
        wx.setStorageSync('events', mockEvents);
      } catch (e) {
        console.error('初始化事件存储失败:', e);
      }
    }
  }

  // 设置会话ID
  setSessionId(sessionId) {
    this.sessionId = sessionId;
  }

  // 获取事件列表
  async getEvents({ page = 1, pageSize = 10, status, type } = {}) {
    if (USE_MOCK) {
      return this._getMockEvents({ page, pageSize, status, type });
    }

    try {
      if (!this.sessionId) {
        throw new Error('会话ID未设置');
      }

      const result = await API.getEvents(this.sessionId, pageSize);
      let events = result.events || [];
      
      // 客户端筛选
      if (status) {
        events = events.filter(event => event.status === status);
      }
      if (type) {
        events = events.filter(event => event.primaryType === type);
      }

      // 客户端分页
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      const pagedEvents = events.slice(start, end);

      return {
        events: pagedEvents,
        total: events.length
      };
    } catch (e) {
      console.error('获取事件列表失败:', e);
      // 降级到Mock数据
      return this._getMockEvents({ page, pageSize, status, type });
    }
  }

  // Mock数据获取方法
  async _getMockEvents({ page = 1, pageSize = 10, status, type } = {}) {
    try {
      let events = wx.getStorageSync('events') || mockEvents;
      
      // 筛选
      if (status) {
        events = events.filter(event => event.status === status);
      }
      if (type) {
        events = events.filter(event => event.primaryType === type);
      }

      // 分页
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      const pagedEvents = events.slice(start, end);

      return {
        events: pagedEvents,
        total: events.length
      };
    } catch (e) {
      console.error('获取Mock事件失败:', e);
      return { events: [], total: 0 };
    }
  }

  // 更新事件状态
  async updateEventStatus(eventId, status) {
    if (USE_MOCK) {
      return this._updateMockEventStatus(eventId, status);
    }

    try {
      if (!this.sessionId) {
        throw new Error('会话ID未设置');
      }

      await API.updateEvent(this.sessionId, eventId, { status });
    } catch (e) {
      console.error('更新事件状态失败:', e);
      // 降级到Mock
      return this._updateMockEventStatus(eventId, status);
    }
  }

  // Mock事件状态更新
  async _updateMockEventStatus(eventId, status) {
    try {
      const events = wx.getStorageSync('events') || [];
      const updatedEvents = events.map(event => {
        if (event.id === eventId) {
          return {
            ...event,
            status,
            updateTime: new Date().toISOString()
          };
        }
        return event;
      });

      wx.setStorageSync('events', updatedEvents);
    } catch (e) {
      console.error('更新Mock事件状态失败:', e);
      throw new Error('更新事件状态失败');
    }
  }

  // 更新事件内容
  async updateEvent(eventId, data) {
    if (USE_MOCK) {
      return this._updateMockEvent(eventId, data);
    }

    try {
      if (!this.sessionId) {
        throw new Error('会话ID未设置');
      }

      await API.updateEvent(this.sessionId, eventId, data);
    } catch (e) {
      console.error('更新事件失败:', e);
      // 降级到Mock
      return this._updateMockEvent(eventId, data);
    }
  }

  // Mock事件更新
  async _updateMockEvent(eventId, data) {
    try {
      const events = wx.getStorageSync('events') || [];
      const updatedEvents = events.map(event => {
        if (event.id === eventId) {
          return {
            ...event,
            ...data,
            updateTime: new Date().toISOString()
          };
        }
        return event;
      });

      wx.setStorageSync('events', updatedEvents);
    } catch (e) {
      console.error('更新Mock事件失败:', e);
      throw new Error('更新事件失败');
    }
  }

  // 删除事件
  async deleteEvent(eventId) {
    if (USE_MOCK) {
      return this._deleteMockEvent(eventId);
    }

    try {
      if (!this.sessionId) {
        throw new Error('会话ID未设置');
      }

      await API.deleteEvent(this.sessionId, eventId);
    } catch (e) {
      console.error('删除事件失败:', e);
      // 降级到Mock
      return this._deleteMockEvent(eventId);
    }
  }

  // Mock事件删除
  async _deleteMockEvent(eventId) {
    try {
      const events = wx.getStorageSync('events') || [];
      const updatedEvents = events.filter(event => event.id !== eventId);
      wx.setStorageSync('events', updatedEvents);
    } catch (e) {
      console.error('删除Mock事件失败:', e);
      throw new Error('删除事件失败');
    }
  }
}

export default new EventService(); 