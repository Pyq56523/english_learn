<template>
  <div class="streak" :class="{ zero: !days }">
    <span class="fire">{{ days ? '🔥' : '🧊' }}</span>
    <span class="num">{{ days }}</span>
    <span class="unit">天</span>
  </div>
</template>

<script setup>
defineProps({
  days: { type: Number, default: 0 }
})
</script>

<style scoped>
.streak {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 20px;
  border-radius: 999px;
  background: linear-gradient(135deg, #fff7ed, #fff1e6);
  border: 1px solid #fed7aa;
  color: #ea580c;
  font-weight: 700;
  box-shadow: 0 6px 16px rgba(234, 88, 12, 0.14);
}
.streak.zero {
  background: #f4f6fa;
  border-color: #e5e9f0;
  color: #8a93a6;
  box-shadow: none;
}
.fire {
  font-size: 18px;
}
.num {
  font-size: 20px;
}
.unit {
  font-size: 13px;
  opacity: 0.8;
}
</style>