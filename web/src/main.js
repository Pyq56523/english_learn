import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import { useSettingsStore } from './stores/settings'
import { initTTS } from './utils/tts'
import PageHeader from './components/common/PageHeader.vue'
import StatCard from './components/common/StatCard.vue'
import SettingItem from './components/common/SettingItem.vue'
import BookCard from './components/common/BookCard.vue'
import CurrentBookCard from './components/common/CurrentBookCard.vue'
import AuthCard from './components/common/AuthCard.vue'
import ForgotPassword from './views/ForgotPassword.vue'
import './assets/styles/main.scss'

// 全局注册通用 UI 组件：在组件标签中直接可用，无需每个页面 import
const GLOBAL_COMPONENTS = {
  PageHeader,
  StatCard,
  SettingItem,
  BookCard,
  CurrentBookCard,
  AuthCard,
  ForgotPassword
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
Object.entries(GLOBAL_COMPONENTS).forEach(([name, comp]) => app.component(name, comp))
app.mount('#app')

// 应用加载完成即预热语音引擎，进学习页时发音无需等待
initTTS()

// 挂载后应用持久化的主题，保证刷新后深色/白天模式立即生效
useSettingsStore().applyTheme()