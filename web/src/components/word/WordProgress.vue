<template>
  <div class="word-progress">
    <span class="label">{{ done }} / {{ total }}</span>
    <el-progress :percentage="percentage" :stroke-width="10" :show-text="false" class="bar" />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, default: 0 },
  done: { type: Number, default: 0 }
})

const percentage = computed(() =>
  props.total > 0 ? Math.round((props.done / props.total) * 100) : 0
)
</script>

<style scoped>
.word-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}
.label {
  font-size: 13px;
  color: #8a93a6;
  font-weight: 600;
}
.bar {
  width: 140px;
}
.bar :deep(.el-progress-bar__outer) {
  background: #eef1f6;
}
</style>