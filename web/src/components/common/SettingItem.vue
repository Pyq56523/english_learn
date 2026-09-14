<template>
  <el-card shadow="never" class="set-card">
    <div class="set-head">
      <div class="set-icon">{{ icon }}</div>
      <div class="set-meta">
        <div class="set-name">{{ name }}</div>
        <div class="set-desc">{{ desc }}</div>
      </div>
    </div>
    <div class="set-control"><slot /></div>
  </el-card>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  name: { type: String, required: true },
  desc: { type: String, default: '' }
})
</script>

<style scoped>
.set-card {
  border-radius: 16px;
  border: 1px solid #eef1f6;
  margin-bottom: 20px;
  background: var(--app-card, #fff);
}
.set-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 22px 26px;
}
.set-head {
  display: flex;
  align-items: center;
  gap: 16px;
}
.set-icon {
  width: 48px;
  height: 48px;
  border-radius: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: var(--app-fill-soft, #f4f5ff);
  flex-shrink: 0;
}
.set-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.set-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.set-desc {
  font-size: 13px;
  color: var(--app-text-secondary, #8a93a6);
}
.set-control {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
</style>