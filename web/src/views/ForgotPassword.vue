<template>
  <AuthCard title="找回密码 🔑" subtitle="通过邮箱和验证码重置你的密码">
    <template #form>
      <el-form :model="form" :rules="rules" ref="formRef" class="form" @submit.prevent="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="用户名"
            :prefix-icon="User" :validate-event="false" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" size="large" placeholder="注册邮箱"
            :prefix-icon="Message" :validate-event="false" />
        </el-form-item>
        <el-form-item prop="new_password">
          <el-input v-model="form.new_password" size="large" type="password" placeholder="新密码（至少 6 位）"
            show-password :prefix-icon="Lock" :validate-event="false" />
        </el-form-item>
        <el-form-item prop="captcha_code">
          <div class="captcha-row">
            <el-input v-model="form.captcha_code" size="large" placeholder="验证码"
              :prefix-icon="Key" @keyup.enter="onSubmit" />
            <img v-if="captcha.image" :src="captcha.image" class="captcha-img" alt="验证码"
              title="点击刷新" @click="loadCaptcha" />
            <div v-else class="captcha-img placeholder">加载中…</div>
          </div>
        </el-form-item>
        <el-button type="primary" size="large" class="full" round :loading="loading" @click="onSubmit">
          重置密码
        </el-button>
      </el-form>
    </template>
    <template #footer>
      想起密码了？
      <router-link to="/login">返回登录</router-link>
    </template>
  </AuthCard>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Message, Lock, Key } from '@element-plus/icons-vue'
import { getCaptcha } from '@/api/captcha'
import { resetPasswordApi } from '@/api/auth'
import { useNavigate } from '@/router'

const { toLogin } = useNavigate()
const formRef = ref()
const loading = ref(false)
const captcha = ref({})

const form = reactive({
  username: '',
  email: '',
  new_password: '',
  captcha_code: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入注册邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  captcha_code: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

async function loadCaptcha() {
  try {
    captcha.value = await getCaptcha()
  } catch (e) {
    captcha.value = {}
  }
}

async function onSubmit() {
  if (!form.username || !form.email || !form.new_password || !form.captcha_code) {
    ElMessage.warning('请填写完整信息')
    return
  }
  loading.value = true
  try {
    await resetPasswordApi({
      username: form.username,
      email: form.email,
      new_password: form.new_password,
      captcha_id: captcha.value.captcha_id,
      captcha_code: form.captcha_code
    })
    ElMessage.success('密码重置成功，请重新登录')
    toLogin()
  } catch (e) {
    // 验证码往往已失效，刷新一张
    loadCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
</script>

<style scoped>
.captcha-row {
  display: flex;
  gap: 12px;
  width: 100%;
  align-items: center;
}
.captcha-row :deep(.el-input) {
  flex: 1;
}
.captcha-img {
  width: 120px;
  height: 42px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid var(--app-border, #e0e3f0);
  object-fit: cover;
  flex-shrink: 0;
}
.captcha-img.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--app-text-muted, #9aa3b2);
  background: var(--app-fill-soft, #f2f3f8);
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