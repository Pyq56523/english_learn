<template>
  <div class="page-header">
    <h2 class="title"><slot name="title">{{ title }}</slot></h2>
    <div class="header-extra"><slot /></div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true }
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 12px;
  flex-wrap: wrap;
}
.title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
  letter-spacing: 0.3px;
}
.header-extra {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
</style>