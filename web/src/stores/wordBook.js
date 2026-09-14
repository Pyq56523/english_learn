import { defineStore } from 'pinia'
import { getWordBooks, getWordBookDetail } from '@/api/wordBook'
import { useSettingsStore } from './settings'

export const useWordBookStore = defineStore('wordBook', {
  state: () => ({
    books: [],
    current: null,        // 当前选中单词书
    progress: null
  }),
  actions: {
    async fetchBooks(params = {}) {
      this.books = await getWordBooks(params)
    },
    async selectBook(bookId) {
      const detail = await getWordBookDetail(bookId)
      this.current = detail
      // 同步持久化到后端
      await useSettingsStore().setCurrentBook(bookId)
      return detail
    },
    /** 根据 settings.currentBookId 恢复 current 对象 */
    restoreCurrent(bookId) {
      if (!bookId) return
      const match = this.books.find(b => b.id === bookId)
      if (match) this.current = match
    }
  }
})