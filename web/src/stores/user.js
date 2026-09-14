import { defineStore } from 'pinia'
import { loginApi, registerApi, meApi } from '@/api/auth'

const TOKEN_KEY = 'el_token'
const USER_KEY = 'el_user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  }),
  getters: {
    isLoggedIn: (state) => !!state.token
  },
  actions: {
    async login(payload) {
      const res = await loginApi(payload)
      this.token = res.access_token
      this.user = res.user
      localStorage.setItem(TOKEN_KEY, res.access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(res.user))
    },
    async register(payload) {
      await registerApi(payload)
    },
    async fetchMe() {
      const user = await meApi()
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    }
  }
})