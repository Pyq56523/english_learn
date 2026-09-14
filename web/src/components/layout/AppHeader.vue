<template>
  <el-header class="header">
    <div class="left">
      <div class="day-chip">
        <span class="lbl">今日</span>
        <span class="val">{{ today }}</span>
      </div>
    </div>
    <div class="spacer" />
    <el-dropdown @command="onCommand">
      <span class="user">
        <span class="avatar">{{ (userStore.user?.username || 'U').charAt(0).toUpperCase() }}</span>
        <span class="name">{{ userStore.user?.username || '未登录' }}</span>
        <el-icon class="arrow"><ArrowDown /></el-icon>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="profile">👤 个人中心</el-dropdown-item>
          <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </el-header>
</template>

<script setup>
import { ArrowDown } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const week = ['日', '一', '二', '三', '四', '五', '六']
const today = dayjs().format(`M月D日 · 周${week[dayjs().day()]}`)

function onCommand(cmd) {
  if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--app-header-bg, rgba(255, 255, 255, 0.82));
  backdrop-filter: saturate(180%) blur(10px);
  border-bottom: 1px solid var(--app-border, #eef1f6);
  height: 64px;
  padding: 0 28px;
  flex-shrink: 0;
}
.left {
  display: flex;
  align-items: center;
}
.day-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 999px;
  background: var(--app-fill-soft, #f4f5ff);
  border: 1px solid var(--app-fill-soft-border, #e6e5ff);
}
.day-chip .lbl {
  font-size: 12px;
  color: var(--app-text-muted, #9aa3b2);
}
.day-chip .val {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-primary, #4f46e5);
}
.user {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 999px;
  transition: background 0.2s;
}
@media (max-width: 640px) {
  .day-chip { display: none; }
}
.user:hover {
  background: #f4f5ff;
}
.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.name {
  font-size: 14px;
  font-weight: 500;
  color: var(--app-text, #1f2430);
}
.arrow {
  color: #9aa3b2;
  font-size: 12px;
}
</style>