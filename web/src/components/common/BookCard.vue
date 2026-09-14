<template>
  <div class="book" :class="{ picked }" tabindex="0" @click="$emit('select', book)" @keydown.enter="$emit('select', book)">
    <div class="book-top">
      <el-tag size="small" effect="light" class="cat">{{ book.category }}</el-tag>
      <el-icon v-if="picked" class="check"><CircleCheckFilled /></el-icon>
    </div>
    <div class="name">{{ book.name }}</div>
    <div class="desc">{{ book.description || '精选高频单词，助你高效学习' }}</div>
    <div class="foot">
      <span class="count"><el-icon><Notebook /></el-icon> {{ book.word_count }} 词</span>
      <el-button v-if="picked" type="primary" size="small" round plain>
        <slot name="picked-label">当前使用</slot>
      </el-button>
      <span v-else class="hover-cta">选择 →</span>
    </div>
  </div>
</template>

<script setup>
import { Notebook, CircleCheckFilled } from '@element-plus/icons-vue'

defineProps({
  book: { type: Object, required: true },
  picked: { type: Boolean, default: false }
})
defineEmits(['select'])
</script>

<style scoped>
.book {
  background: var(--app-card, #fff);
  border: 1px solid var(--app-border, #eef1f6);
  border-radius: 16px;
  padding: 22px;
  cursor: pointer;
  min-height: 158px;
  display: flex;
  flex-direction: column;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  box-shadow: 0 2px 8px rgba(30, 41, 59, 0.04);
}
.book:hover {
  transform: translateY(-4px);
  border-color: var(--app-border-accent, #c7d2fe);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.12);
}
.book.picked {
  border-color: var(--app-primary, #6366f1);
  box-shadow: 0 8px 26px rgba(99, 102, 241, 0.18);
}
.book-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.cat {
  border-radius: 999px;
}
.check {
  color: var(--app-primary, #4f46e5);
  font-size: 20px;
}
.name {
  font-size: 20px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.desc {
  margin-top: 6px;
  font-size: 13px;
  color: var(--app-text-secondary, #8a93a6);
  line-height: 1.5;
  flex: 1;
}
.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 14px;
}
.count {
  color: var(--app-text-muted, #9aa3b2);
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.hover-cta {
  color: var(--app-primary, #6366f1);
  font-size: 13px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s;
}
.book:hover .hover-cta {
  opacity: 1;
}
</style>