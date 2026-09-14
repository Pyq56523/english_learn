<template>
  <el-card class="current-book" body-class="book-body">
    <div class="book-icon">📚</div>
    <div class="book-info">
      <div class="book-name">{{ name }}</div>
      <div class="book-meta">
        <el-tag v-if="category" size="small" effect="light">{{ category }}</el-tag>
        <span class="book-count">{{ count }} 词</span>
      </div>
    </div>
    <div class="book-actions">
      <slot name="actions"><el-button type="primary" round size="small" @click="$emit('action')">{{ actionText }}</el-button></slot>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  category: { type: String, default: '' },
  count: { type: [Number, String], default: 0 },
  actionText: { type: String, default: '更换词书' }
})
defineEmits(['action'])
</script>

<style scoped>
.current-book {
  border-radius: 14px;
  border: 1px solid var(--app-border, #eef1f6);
  margin-bottom: 16px;
}
.current-book :deep(.el-card__body.book-body) {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
}
.book-icon {
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
.book-info {
  flex: 1;
  min-width: 0;
}
.book-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.book-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.book-count {
  color: var(--app-text-secondary, #8a93a6);
  font-size: 13px;
}
.book-actions {
  flex-shrink: 0;
}
</style>