import { defineStore } from 'pinia'
import { useUserStore } from './user'
import { useLearningStore } from './learning'
import { useWordBookStore } from './wordBook'

/**
 * 汇总入口：确保各 store 在布局初始化时可用
 */
export function useAppStore() {
  const userStore = useUserStore()
  const learningStore = useLearningStore()
  const wordBookStore = useWordBookStore()
  return { userStore, learningStore, wordBookStore }
}