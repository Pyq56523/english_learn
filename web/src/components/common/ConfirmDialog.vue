<template>
  <el-dialog :model-value="modelValue" :title="title" width="360px" @update:model-value="$emit('update:modelValue', $event)">
    <p>{{ message }}</p>
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="$emit('confirm')">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '提示' },
  message: { type: String, default: '' }
})
defineEmits(['update:modelValue', 'confirm'])
</script>