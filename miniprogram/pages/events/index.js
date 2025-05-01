import EventService from '../../services/event';

Page({
  data: {
    events: [],
    loading: false,
    hasMore: true,
    page: 1,
    pageSize: 10,
    currentFilter: {
      status: '',
      type: ''
    }
  },

  onLoad() {
    this.loadEvents();
  },

  onPullDownRefresh() {
    this.setData({
      page: 1,
      hasMore: true
    }, () => {
      this.loadEvents(true);
    });
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadEvents();
    }
  },

  async loadEvents(isPullDown = false) {
    if (this.data.loading) return;

    this.setData({ loading: true });

    try {
      const { events, total } = await EventService.getEvents({
        page: this.data.page,
        pageSize: this.data.pageSize,
        ...this.data.currentFilter
      });

      const hasMore = this.data.page * this.data.pageSize < total;

      this.setData({
        events: isPullDown ? events : [...this.data.events, ...events],
        hasMore,
        page: hasMore ? this.data.page + 1 : this.data.page
      });
    } catch (error) {
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    } finally {
      this.setData({ loading: false });
      if (isPullDown) {
        wx.stopPullDownRefresh();
      }
    }
  },

  async handleEventConfirm(e) {
    const { eventId } = e.currentTarget.dataset;
    try {
      await EventService.updateEventStatus(eventId, 'confirmed');
      this.updateLocalEvent(eventId, { status: 'confirmed' });
      wx.showToast({
        title: '已确认',
        icon: 'success'
      });
    } catch (error) {
      wx.showToast({
        title: '操作失败',
        icon: 'error'
      });
    }
  },

  async handleEventReject(e) {
    const { eventId } = e.currentTarget.dataset;
    try {
      await EventService.updateEventStatus(eventId, 'rejected');
      this.updateLocalEvent(eventId, { status: 'rejected' });
      wx.showToast({
        title: '已否定',
        icon: 'error'
      });
    } catch (error) {
      wx.showToast({
        title: '操作失败',
        icon: 'error'
      });
    }
  },

  async handleEventEdit(e) {
    const { eventId, title, content, type } = e.detail;
    try {
      await EventService.updateEvent(eventId, { title, content, type });
      this.updateLocalEvent(eventId, { title, content, type });
      wx.showToast({
        title: '已更新',
        icon: 'success'
      });
    } catch (error) {
      wx.showToast({
        title: '更新失败',
        icon: 'error'
      });
    }
  },

  async handleEventDelete(e) {
    const { eventId } = e.currentTarget.dataset;
    try {
      await EventService.deleteEvent(eventId);
      this.removeLocalEvent(eventId);
      wx.showToast({
        title: '已删除',
        icon: 'success'
      });
    } catch (error) {
      wx.showToast({
        title: '删除失败',
        icon: 'error'
      });
    }
  },

  // 更新本地事件数据
  updateLocalEvent(eventId, data) {
    const events = this.data.events.map(event => {
      if (event.id === eventId) {
        return { ...event, ...data };
      }
      return event;
    });
    this.setData({ events });
  },

  // 移除本地事件数据
  removeLocalEvent(eventId) {
    const events = this.data.events.filter(event => event.id !== eventId);
    this.setData({ events });
  },

  // 返回上一页
  navigateBack() {
    wx.navigateBack({
      delta: 1,
      success: function() {
        console.log('成功返回上一页');
      },
      fail: function(error) {
        console.error('返回上一页失败:', error);
        wx.showToast({
          title: '返回失败，请重试',
          icon: 'none'
        });
      }
    });
  }
}); 