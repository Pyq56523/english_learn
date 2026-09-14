<template>
  <el-aside width="232px" class="sidebar">
    <div class="logo">
      <span class="logo-badge">
        <el-icon><Reading /></el-icon>
      </span>
      <span class="logo-text">English Learner</span>
    </div>
    <div class="menu-title">MENU 学习导航</div>
    <el-menu :default-active="$route.path" router class="menu">
      <el-menu-item index="/">
        <el-icon><HomeFilled /></el-icon>
        <span>学习仪表盘</span>
      </el-menu-item>
      <el-menu-item index="/books">
        <el-icon><Notebook /></el-icon>
        <span>选择单词书</span>
      </el-menu-item>
      <el-menu-item index="/learning">
        <el-icon><Reading /></el-icon>
        <span>开始学习</span>
      </el-menu-item>
      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <span>学习设置</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import {
  HomeFilled,
  Notebook,
  Reading,
  Setting
} from '@element-plus/icons-vue'
</script>

<style scoped>
.sidebar {
  background: var(--app-card, #fff);
  border-right: 1px solid var(--app-border, #eef1f6);
  display: flex;
  flex-direction: column;
  position: relative;
}
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 22px;
  border-bottom: 1px solid var(--app-border, #f2f4f9);
  flex-shrink: 0;
}
.logo-badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  font-size: 17px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
}
.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.menu-title {
  padding: 18px 24px 8px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  color: #b3bac7;
}
.menu {
  border-right: none;
  padding: 4px 14px 20px;
  flex: 1;
}
.menu :deep(.el-menu-item) {
  border-radius: 12px;
  margin-bottom: 6px;
  height: 48px;
  color: var(--app-text-secondary, #5b6172);
  transition: background 0.2s, color 0.2s, transform 0.2s;
}
.menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
}
.menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, var(--app-primary-bg, #f0efff), var(--app-primary-bg2, #e9e7ff));
  color: var(--app-primary, #4f46e5);
  font-weight: 700;
  box-shadow: inset 0 0 0 1px var(--app-fill-soft-border, #dfdbff);
}
.menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: -14px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  border-radius: 0 4px 4px 0;
  background: linear-gradient(180deg, #6366f1, #4338ca);
}
.menu :deep(.el-menu-item:not(.is-active):hover) {
  background: var(--app-row-hover, #f4f5ff);
  color: var(--app-primary, #4f46e5);
}
</style>