// Mock事件数据
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
    subType: 'negativeThinking',
    title: '消极思考',
    content: '反复思考过去的失败经历，认为自己不够好',
    time: '2024-04-05 14:20',
    dialogContent: '我总是想起去年那次面试失败的经历，觉得自己永远也比不上别人，无论多努力都是徒劳。',
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

// 模拟延迟
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 事件服务类
class EventService {
  constructor() {
    // 初始化本地存储
    try {
      const events = wx.getStorageSync('events');
      if (!events) {
        wx.setStorageSync('events', mockEvents);
      }
    } catch (e) {
      console.error('初始化事件存储失败:', e);
    }
  }

  // 获取事件列表
  async getEvents({ page = 1, pageSize = 10, status, type } = {}) {
    await delay(500); // 模拟网络延迟

    try {
      let events = wx.getStorageSync('events') || [];
      
      // 筛选
      if (status) {
        events = events.filter(event => event.status === status);
      }
      if (type) {
        events = events.filter(event => event.type === type);
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
      console.error('获取事件列表失败:', e);
      throw new Error('获取事件列表失败');
    }
  }

  // 更新事件状态
  async updateEventStatus(eventId, status) {
    await delay(300);

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
      console.error('更新事件状态失败:', e);
      throw new Error('更新事件状态失败');
    }
  }

  // 更新事件内容
  async updateEvent(eventId, data) {
    await delay(300);

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
      console.error('更新事件失败:', e);
      throw new Error('更新事件失败');
    }
  }

  // 删除事件
  async deleteEvent(eventId) {
    await delay(300);

    try {
      const events = wx.getStorageSync('events') || [];
      const updatedEvents = events.filter(event => event.id !== eventId);
      wx.setStorageSync('events', updatedEvents);
    } catch (e) {
      console.error('删除事件失败:', e);
      throw new Error('删除事件失败');
    }
  }

  // 模拟从对话中提取事件
  async extractEventsFromDialog(dialogContent) {
    await delay(800); // 模拟API调用延迟

    // 模拟事件提取逻辑
    const newEvent = {
      id: `event_${Date.now()}`,
      type: '待分类',
      title: dialogContent.slice(0, 20) + (dialogContent.length > 20 ? '...' : ''),
      content: dialogContent,
      time: new Date().toISOString().slice(0, 16).replace('T', ' '),
      dialogContent,
      sourceDialogId: `dialog_${Date.now()}`,
      status: 'pending',
      tagColor: '#848484',
      createTime: new Date().toISOString(),
      updateTime: new Date().toISOString()
    };

    try {
      const events = wx.getStorageSync('events') || [];
      events.unshift(newEvent);
      wx.setStorageSync('events', events);
      return newEvent;
    } catch (e) {
      console.error('保存提取的事件失败:', e);
      throw new Error('保存提取的事件失败');
    }
  }
}

export default new EventService(); 