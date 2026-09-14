import { createRouter, createWebHistory, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { meApi } from '@/api/auth'

/**
 * 全局路由集中配置：新增页面只需在此登记，导航统一走 useNavigate，
 * 各组件无需写死路径字符串。
 */
export const APP_ROUTES = {
  home: { path: '/', name: 'Home' },
  books: { path: '/books', name: 'WordBooks' },
  learning: { path: '/learning', name: 'Learning' },
  settings: { path: '/settings', name: 'Settings' },
  profile: { path: '/profile', name: 'Profile' },
  login: { path: '/login', name: 'Login' },
  register: { path: '/register', name: 'Register' },
  forgot: { path: '/forgot', name: 'ForgotPassword' }
}

/** 跳转目标白名单，便于类型提示与集中管理 */
const ROUTE_KEYS = Object.keys(APP_ROUTES)

/**
 * 统一跳转封装。返回按 key 命名的方法：
 *   const { toHome, toBooks } = useNavigate()
 *   toHome()
 * 也支持通用 to('books') 或直接传对象。
 */
export function useNavigate() {
  const router = useRouter()

  function to(key, params) {
    const route = APP_ROUTES[key]
    if (!route) {
      console.warn(`[useNavigate] 未知路由 key: ${key}`)
      return
    }
    router.push({ path: route.path, query: params })
  }

  const named = {}
  for (const key of ROUTE_KEYS) {
    named['to' + key[0].toUpperCase() + key.slice(1)] = (params) => to(key, params)
  }

  return { to, ...named }
}

// 本次会话内的 token 校验结果缓存（只向后端校验一次，避免每次跳转都请求）
let validatedToken = null

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { public: true }
  },
  {
    path: '/forgot',
    name: 'ForgotPassword',
    component: () => import('@/views/ForgotPassword.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/Home.vue') },
      { path: 'books', name: 'WordBooks', component: () => import('@/views/WordBooks.vue') },
      { path: 'learning', name: 'Learning', component: () => import('@/views/Learning.vue') },
      { path: 'settings', name: 'Settings', component: () => import('@/views/Settings.vue') },
      { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫：未登录访问受保护页 → 跳转登录
router.beforeEach(async (to) => {
  if (to.meta.public) return true
  const userStore = useUserStore()

  // 无 token → 登出并回登录页
  if (!userStore.token) {
    userStore.logout()
    return { name: 'Login' }
  }

  // 本会话内未校验过该 token，则向后端 /auth/me 校验其有效性
  if (validatedToken !== userStore.token) {
    try {
      const user = await meApi()
      userStore.user = user
      localStorage.setItem('el_user', JSON.stringify(user))
      validatedToken = userStore.token
    } catch (e) {
      validatedToken = null
      userStore.logout()
      return { name: 'Login' }
    }
  }
  return true
})

export default router