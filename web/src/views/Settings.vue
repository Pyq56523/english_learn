<template>
  <div class="page-container settings">
    <PageHeader title="学习设置" />

    <!-- 每日学习目标 -->
    <SettingItem
      icon="🎯"
      name="每日学习目标"
      desc="设置每天固定学习多少个单词，作为今日学习进度的目标参考。"
    >
      <el-input-number
        v-model="daily"
        :min="1"
        :max="200"
        :step="5"
        :precision="0"
        size="large"
        @change="onDailyChange"
      />
      <span class="unit">个 / 天</span>
      <el-button round type="primary" @click="saveDaily">保存目标</el-button>
    </SettingItem>

    <!-- 页面模式 -->
    <SettingItem
      icon="🌗"
      name="页面模式"
      desc="切换白天 / 夜晚模式，切换后即时生效并自动保存。"
    >
      <el-radio-group v-model="theme" size="large" @change="onThemeChange">
        <el-radio-button value="light">☀️ 白天模式</el-radio-button>
        <el-radio-button value="dark">🌙 夜晚模式</el-radio-button>
      </el-radio-group>
    </SettingItem>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'

const settings = useSettingsStore()
const daily = ref(settings.dailyTarget)
const theme = ref(settings.theme)

onMounted(async () => {
  // 从后端加载已持久化的每日目标
  await settings.init()
  daily.value = settings.dailyTarget
})

function saveDaily() {
  settings.setDailyTarget(daily.value)
  ElMessage.success(`每日学习目标已设为 ${settings.dailyTarget} 个`)
}

function onDailyChange() {
  // 输入变化即保存，保证刷新后仍沿用
  settings.setDailyTarget(daily.value)
}

function onThemeChange() {
  settings.setTheme(theme.value)
  ElMessage.success(theme.value === 'dark' ? '已切换到夜晚模式' : '已切换到白天模式')
}
</script>

<style scoped>
.settings {
  max-width: 760px;
  margin: 0 auto;
}
.unit {
  font-size: 14px;
  color: var(--app-text-secondary, #8a93a6);
}
</style>