import { defineStore } from 'pinia'
import { getTodayCards, submitReview, startLearning, getProgress } from '@/api/learning'

export const useLearningStore = defineStore('learning', {
  state: () => ({
    mode: 'learn',        // learn=学习新词 | review=复习到期卡（默认学习）
    newCards: [],         // 今日可学新词（数量受 daily_target 限制）
    dueCards: [],         // 到期复习卡（next_review_at <= now）
    learnedCards: [],     // 今日已学新词（供键盘拼写，不受每日配额影响）
    summary: { daily_target: 0, learn_count: 0, total_new: 0, total_due: 0, mastered: 0 },
    queue: [],            // 当前卡片队列（按 mode 取 newCards / dueCards）
    queueIndex: 0,
    current: null,        // 当前卡片
    loaded: false
  }),
  actions: {
    async fetchTodayCards() {
      const data = await getTodayCards()
      this.newCards = data.new_cards || []
      this.dueCards = data.due_cards || []
      this.learnedCards = data.learned_cards || []
      this.summary = data.summary || { daily_target: 0, learn_count: 0, total_new: 0, total_due: 0, mastered: 0 }
      this.applyModeQueue()
      this.loaded = true
    },
    // 按当前模式把对应数据装入队列（学习→新词，复习→到期卡）
    applyModeQueue() {
      this.queue = this.mode === 'review' ? this.dueCards : this.newCards
      this.queueIndex = 0
      this.current = this.queue[0] || null
    },
    setMode(mode) {
      if (mode === this.mode) return
      this.mode = mode
      this.applyModeQueue()
    },
    nextCard() {
      this.queueIndex += 1
      this.current = this.queue[this.queueIndex] || null
    },
    async rateCard(quality) {
      if (!this.current || !this.current.record_id) {
        // 新卡片无 record_id，直接跳到下一张
        this.nextCard()
        return null
      }
      const res = await submitReview({ record_id: this.current.record_id, quality })
      this.nextCard()
      return res
    },
    reset() {
      this.mode = 'learn'
      this.queue = []
      this.queueIndex = 0
      this.current = null
      this.loaded = false
    }
  }
})