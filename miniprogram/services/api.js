// API 配置
const API_CONFIG = {
  baseURL: 'http://localhost:5858/api',
  timeout: 10000
};

// 构建查询字符串的辅助函数
const buildQueryString = (params) => {
  const queryParts = [];
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`);
    }
  }
  return queryParts.length > 0 ? queryParts.join('&') : '';
};

// 通用请求封装
const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_CONFIG.baseURL}${url}`,
      timeout: API_CONFIG.timeout,
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      ...options,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`));
        }
      },
      fail: (err) => {
        reject(new Error(`网络错误: ${err.errMsg}`));
      }
    });
  });
};

// API 方法
const API = {
  // 获取事件列表
  getEvents: (sessionId, limit) => {
    const params = { session_id: sessionId };
    if (limit) params.limit = limit;
    
    const queryString = buildQueryString(params);
    return request(`/events?${queryString}`, {
      method: 'GET'
    });
  },

  // 更新事件
  updateEvent: (sessionId, eventId, data) => {
    const queryString = buildQueryString({ session_id: sessionId });
    return request(`/events/${eventId}?${queryString}`, {
      method: 'PUT',
      data: data
    });
  },

  // 删除事件
  deleteEvent: (sessionId, eventId) => {
    const queryString = buildQueryString({ session_id: sessionId });
    return request(`/events/${eventId}?${queryString}`, {
      method: 'DELETE'
    });
  },

  // 发送聊天消息
  sendMessage: (data) => {
    return request('/chat', {
      method: 'POST',
      data: data
    });
  },

  // 获取聊天历史
  getChatHistory: (userId, sessionId) => {
    const queryString = buildQueryString({ 
      user_id: userId, 
      session_id: sessionId 
    });
    return request(`/chat/history?${queryString}`, {
      method: 'GET'
    });
  }
};

export default API; 