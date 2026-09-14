<template>
  <AuthCard title="创建账号 ✨" subtitle="只需几秒，开启你的每日词汇旅程">
    <template #form>
      <el-form :model="form" :rules="rules" ref="formRef" class="form" @submit.prevent="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="用户名（至少 3 个字符）"
            :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" size="large" placeholder="邮箱 example@mail.com"
            :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" size="large" type="password" placeholder="密码（至少 6 位）"
            show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item prop="captcha">
          <div class="captcha-row">
            <el-input v-model="form.captcha_code" size="large" placeholder="图形验证码"
              class="captcha-input" :prefix-icon="Key" />
            <img v-if="captchaImg" :src="captchaImg" class="captcha-img" alt="验证码"
              title="点击刷新" @click="loadCaptcha" />
            <el-icon v-else class="captcha-loading"><Refresh @click="loadCaptcha" /></el-icon>
          </div>
        </el-form-item>
        <el-button type="primary" size="large" class="full" round :loading="loading" @click="onSubmit">
          注册
        </el-button>
      </el-form>
    </template>
    <template #footer>
      已有账号？
      <router-link to="/login">去登录</router-link>
    </template>
  </AuthCard>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Key } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useNavigate } from '@/router'
import { getCaptcha } from '@/api/captcha'

const { toLogin } = useNavigate()
const userStore = useUserStore()
const formRef = ref()
const form = reactive({ username: '', email: '', password: '', captcha_id: '', captcha_code: '' })
const captchaImg = ref('')
const loading = ref(false)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少 3 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ]
}

async function loadCaptcha() {
  try {
    const data = await getCaptcha()
    form.captcha_id = data.captcha_id
    captchaImg.value = data.image
  } catch (e) {
    ElMessage.error('图形验证码加载失败')
  }
}

async function onSubmit() {
  formRef.value?.validate(() => {})
  if (!form.username || !form.email || !form.password || !form.captcha_code) {
    ElMessage.warning('请填写完整信息')
    return
  }
  loading.value = true
  try {
    await userStore.register(form)
    ElMessage.success('注册成功，请登录')
    toLogin()
  } catch (e) {
    // 失败后刷新验证码
    loadCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(loadCaptcha)
</script>

<style scoped>
.form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 4px 14px;
}
.captcha-row {
  display: flex;
  gap: 10px;
  width: 100%;
}
.captcha-input {
  flex: 1;
}
.captcha-img {
  width: 120px;
  height: 42px;
  border-radius: 8px;
  border: 1px solid var(--app-border, #eef1f6);
  cursor: pointer;
  flex-shrink: 0;
}
.captcha-loading {
  width: 120px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  cursor: pointer;
  border: 1px dashed #d0d7e0;
  border-radius: 8px;
  font-size: 20px;
  flex-shrink: 0;
}
.full {
  width: 100%;
  margin-top: 6px;
  height: 46px;
  font-weight: 600;
}
</style>