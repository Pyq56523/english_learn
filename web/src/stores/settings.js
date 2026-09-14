import { defineStore } from 'pinia'
import { getSettings, updateSettings } from '@/api/settings'

const DAILY_KEY = 'el_daily_target'
const THEME_KEY = 'el_theme'

/** 读取已保存主题；无则跟随系统深色偏好，默认 light */
function loadTheme() {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  return 'light'
}

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    dailyTarget: Number(localStorage.getItem(DAILY_KEY) || 20),
    theme: loadTheme(),
    currentBookId: null  // 当前所选单词书 id（后端持久化）
  }),
  actions: {
    applyTheme() {
      const root = document.documentElement
      if (this.theme === 'dark') {
        root.classList.add('dark')
      } else {
        root.classList.remove('dark')
      }
    },
    /** 从后端加载已持久化的设置 */
    async init() {
      try {
        const s = await getSettings()
        if (s?.daily_target) {
          this.dailyTarget = Number(s.daily_target)
          localStorage.setItem(DAILY_KEY, String(this.dailyTarget))
        }
        if (s?.current_book_id) {
          this.currentBookId = Number(s.current_book_id)
        }
      } catch (e) {
        /* 未登录或网络失败时保持本地默认值 */
      }
    },
    async setDailyTarget(value) {
      this.dailyTarget = Number(value)
      localStorage.setItem(DAILY_KEY, String(this.dailyTarget))
      try {
        await updateSettings({ daily_target: this.dailyTarget })
      } catch (e) { /* ignore */ }
    },
    async setCurrentBook(bookId) {
      this.currentBookId = bookId
      try {
        await updateSettings({ daily_target: this.dailyTarget, current_book_id: bookId })
      } catch (e) { /* ignore */ }
    },
    setTheme(theme) {
      this.theme = theme === 'dark' ? 'dark' : 'light'
      localStorage.setItem(THEME_KEY, this.theme)
      this.applyTheme()
    }
  }
})