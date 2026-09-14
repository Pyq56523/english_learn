<template>
  <div class="rating">
    <div class="title">这一张，你是怎么记住的？</div>
    <div class="options">
      <el-button
        v-for="opt in options"
        :key="opt.value"
        size="large"
        :class="['rate-btn', opt.type]"
        @click="$emit('rate', opt.value)"
      >
        {{ opt.label }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['rate'])

const options = [
  { value: 0, label: '忘记', type: 'again' },
  { value: 3, label: '模糊', type: 'hard' },
  { value: 5, label: '认识', type: 'easy' }
]
</script>

<style scoped>
.rating {
  text-align: center;
  margin-top: 24px;
}
.title {
  margin-bottom: 14px;
  color: #8a93a6;
  font-size: 14px;
}
.options {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.rate-btn {
  border-radius: 999px;
  font-weight: 600;
  min-width: 96px;
  border: 1px solid #eef1f6 !important;
  background: #fff !important;
}
.rate-btn.again { color: #ef4444; }
.rate-btn.again:hover { background: #fff1f1 !important; border-color: #fecaca !important; }
.rate-btn.hard { color: #f59e0b; }
.rate-btn.hard:hover { background: #fff8e8 !important; border-color: #fde68a !important; }
.rate-btn.good { color: #16a34a; }
.rate-btn.good:hover { background: #eefbf0 !important; border-color: #bbf7d0 !important; }
.rate-btn.easy { color: #4f46e5; }
.rate-btn.easy:hover { background: #eef0ff !important; border-color: #c7d2fe !important; }
</style>