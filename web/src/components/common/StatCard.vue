<template>
  <el-card shadow="hover" class="stat-card" body-class="stat-body">
    <div class="stat-icon">{{ icon }}</div>
    <el-statistic :title="title" :value="value">
      <template v-if="suffix || $slots.suffix" #suffix>
        <span class="suffix"><slot name="suffix">{{ suffix }}</slot></span>
      </template>
    </el-statistic>
  </el-card>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  title: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  suffix: { type: String, default: '' }
})
</script>

<style scoped>
.stat-card {
  border-radius: 14px;
  border: 1px solid var(--app-border, #eef1f6);
}
.stat-card :deep(.el-card__body.stat-body) {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
}
.stat-icon {
  font-size: 26px;
  width: 46px;
  height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--app-primary-bg, #eef0ff);
  flex-shrink: 0;
}
.stat-card :deep(.el-statistic__head) {
  color: var(--app-text-secondary, #8a93a6);
  font-size: 13px;
  margin-bottom: 2px;
}
.stat-card :deep(.el-statistic__content) {
  font-size: 26px;
  font-weight: 800;
  color: var(--app-text, #1f2430);
}
.stat-card :deep(.el-statistic__content .suffix) {
  font-size: 14px;
  color: var(--app-text-secondary, #8a93a6);
  font-weight: 600;
  margin-left: 2px;
}
</style>