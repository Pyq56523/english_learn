<template>
  <div class="heatmap">
    <div class="day" v-for="(d, i) in cells" :key="i" :style="{ background: color(d) }" />
    <div class="legend">
      <span>少</span>
      <div class="sample" :style="{ background: color(0) }" />
      <div class="sample" :style="{ background: color(2) }" />
      <div class="sample" :style="{ background: color(5) }" />
      <div class="sample" :style="{ background: color(10) }" />
      <span>多</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  dates: { type: Array, default: () => [] },
  counts: { type: Array, default: () => [] }
})

function color(count) {
  if (!count) return '#ebedf0'
  if (count < 3) return '#9be9a8'
  if (count < 6) return '#40c463'
  if (count < 10) return '#30a14e'
  return '#216e39'
}

const cells = computed(() =>
  props.dates.map((date, i) => ({ date, count: props.counts[i] || 0 }))
)
</script>

<style scoped>
.heatmap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 14px;
  background: #fafbff;
  border-radius: 12px;
  border: 1px solid #f0f1fa;
}
.day {
  width: 13px;
  height: 13px;
  border-radius: 3px;
  transition: transform 0.15s ease;
}
.day:hover {
  transform: scale(1.3);
}
.legend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}
.sample {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}
</style>