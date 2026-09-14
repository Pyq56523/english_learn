<template>
  <AuthCard title="欢迎回来 👋" subtitle="登录账号，继续今日的学习旅程">
    <template #form>
      <el-form :model="form" :rules="rules" ref="formRef" class="form" @submit.prevent="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="用户名或邮箱"
            :prefix-icon="User" :validate-event="false" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" size="large" type="password" placeholder="密码"
            show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" size="large" class="full" round :loading="loading" @click="onSubmit">
          登录
        </el-button>
      </el-form>
    </template>
    <template #footer>
      <span class="foot-links">
        <router-link to="/forgot">找回密码</router-link>
        <span class="divider">·</span>
        <router-link to="/register">立即注册</router-link>
      </span>
    </template>
  </AuthCard>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useNavigate } from '@/router'

const { toHome } = useNavigate()
const userStore = useUserStore()
const formRef = ref()
const form = reactive({ username: '', password: '' })
const loading = ref(false)

const rules = {
  username: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function onSubmit() {
  formRef.value?.validate(() => {})
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await userStore.login(form)
    toHome()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.foot-links {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.foot-links .divider {
  color: var(--app-text-muted, #a7b0c0);
}
.form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 14px;
}
.full {
  width: 100%;
  margin-top: 6px;
  height: 46px;
  font-weight: 600;
}
</style>