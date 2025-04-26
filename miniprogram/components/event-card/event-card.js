Component({
  properties: {
    eventType: {
      type: String,
      value: '事件'
    },
    primaryType: {
      type: String,
      value: ''
    },
    title: {
      type: String,
      value: ''
    },
    content: {
      type: String,
      value: ''
    },
    time: {
      type: String,
      value: ''
    },
    dialogContent: {
      type: String,
      value: ''
    },
    tagColor: {
      type: String,
      value: '#07C160'
    }
  },

  data: {
    editing: false,
    showEditDialog: false,
    editContent: '',
    editTitle: '',
    confirmed: false,
    rejected: false,
    x: 0,
    eventTypes: ['情绪', '认知', '人际', '行为', '生理', '生活'],
    typeMapping: {
      'emotional': '情绪',
      'cognitive': '认知',
      'interpersonal': '人际',
      'behavioral': '行为',
      'physiological': '生理',
      'lifeEvent': '生活'
    },
    typeIndex: 0,
    deleteThreshold: -150
  },

  observers: {
    'primaryType': function(type) {
      // 当primaryType改变时，更新typeIndex
      const chineseType = this.data.typeMapping[type] || type;
      const index = this.data.eventTypes.indexOf(chineseType);
      if (index !== -1) {
        this.setData({ typeIndex: index });
      }
    }
  },

  methods: {
    // 获取显示用的类型文本
    getDisplayType() {
      return this.data.typeMapping[this.data.primaryType] || this.data.primaryType;
    },

    onChange(e) {
      const x = e.detail.x;
      if (x < this.data.deleteThreshold) {
        this.setData({ x: this.data.deleteThreshold });
      }
    },

    onCardTap() {
      if (this.data.x < 0) {
        this.setData({ x: 0 });
      }
    },

    onConfirm() {
      this.setData({
        confirmed: !this.data.confirmed,
        rejected: false,
        x: 0
      });
      this.triggerEvent('confirm', {
        eventId: this.dataset.eventId,
        confirmed: this.data.confirmed
      });
    },

    onReject() {
      this.setData({
        rejected: !this.data.rejected,
        confirmed: false,
        x: 0
      });
      this.triggerEvent('reject', {
        eventId: this.dataset.eventId,
        rejected: this.data.rejected
      });
    },

    onDelete() {
      wx.showModal({
        title: '确认删除',
        content: '是否确认删除该事件？',
        success: (res) => {
          if (res.confirm) {
            this.triggerEvent('delete', {
              eventId: this.dataset.eventId
            });
          }
          this.setData({ x: 0 });
        }
      });
    },

    onEdit() {
      this.setData({
        showEditDialog: true,
        editContent: this.data.content,
        editTitle: this.data.title,
        typeIndex: this.data.eventTypes.indexOf(this.data.typeMapping[this.data.primaryType] || this.data.primaryType),
        x: 0
      });
    },

    onEditCancel() {
      this.setData({
        showEditDialog: false,
        editContent: '',
        editTitle: ''
      });
    },

    onEditConfirm() {
      if (!this.data.editTitle.trim() || !this.data.editContent.trim()) {
        wx.showToast({
          title: '标题和内容不能为空',
          icon: 'none'
        });
        return;
      }

      // 获取英文类型
      const chineseType = this.data.eventTypes[this.data.typeIndex];
      const englishType = Object.keys(this.data.typeMapping).find(
        key => this.data.typeMapping[key] === chineseType
      );

      this.triggerEvent('edit', {
        eventId: this.dataset.eventId,
        title: this.data.editTitle,
        content: this.data.editContent,
        primaryType: englishType || chineseType
      });

      this.setData({
        showEditDialog: false
      });
    },

    onTitleInput(e) {
      this.setData({
        editTitle: e.detail.value
      });
    },

    onContentInput(e) {
      this.setData({
        editContent: e.detail.value
      });
    },

    onTypeChange(e) {
      this.setData({
        typeIndex: e.detail.value
      });
    }
  }
}); 