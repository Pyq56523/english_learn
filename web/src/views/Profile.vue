<template>
  <div class="page-container profile">
    <PageHeader title="个人中心" />

    <el-card shadow="never" class="info-card">
      <!-- ========== 展示模式 ========== -->
      <template v-if="!editMode">
        <div class="info-head">
          <div class="avatar-big">
            <img v-if="userStore.user?.avatar" :src="userStore.user.avatar" alt="avatar" />
            <span v-else>{{ (userStore.user?.username || 'U').charAt(0).toUpperCase() }}</span>
          </div>
          <div class="head-meta">
            <div class="head-name">{{ userStore.user?.username || '—' }}</div>
            <div class="head-email">{{ userStore.user?.email || '—' }}</div>
          </div>
          <div class="head-actions">
            <el-button class="edit-btn" round type="primary" @click="startEdit('info')">修改信息</el-button>
            <el-button class="edit-btn" round @click="startEdit('password')">修改密码</el-button>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-row">
            <span class="info-lbl">年龄</span>
            <span class="info-val">{{ userStore.user?.age || '未设置' }}</span>
          </div>
          <div class="info-row">
            <span class="info-lbl">性别</span>
            <span class="info-val">{{ genderLabel }}</span>
          </div>
          <div class="info-row">
            <span class="info-lbl">注册时间</span>
            <span class="info-val">{{ formatDate(userStore.user?.created_at) }}</span>
          </div>
        </div>

        <div class="bio-block">
          <span class="info-lbl">个人简介</span>
          <p v-if="userStore.user?.bio" class="bio-text">{{ userStore.user.bio }}</p>
          <p v-else class="bio-empty">还没有填写个人简介～</p>
        </div>
      </template>

      <!-- ========== 修改信息 ========== -->
      <template v-else-if="editMode === 'info'">
        <div class="edit-head">
          <h3>修改个人信息</h3>
          <span class="edit-tip">修改后点击保存即可生效</span>
        </div>

        <el-form :model="form" label-position="top" class="edit-form">
          <div class="form-grid">
            <el-form-item label="用户名">
              <el-input v-model="form.username" maxlength="50" show-word-limit />
            </el-form-item>

            <el-form-item label="邮箱">
              <el-input v-model="form.email" placeholder="your@email.com" />
            </el-form-item>

            <el-form-item label="年龄">
              <el-input-number v-model="form.age" :min="1" :max="150" controls-position="right" />
            </el-form-item>

            <el-form-item label="性别">
              <el-radio-group v-model="form.gender">
                <el-radio value="male">男</el-radio>
                <el-radio value="female">女</el-radio>
                <el-radio value="other">保密</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="头像" class="full-width">
              <div class="avatar-upload">
                <div class="avatar-preview">
                  <img v-if="avatarPreview" :src="avatarPreview" alt="preview" />
                  <span v-else>{{ (form.username || 'U').charAt(0).toUpperCase() }}</span>
                </div>
                <div class="avatar-actions">
                  <el-upload
                    class="avatar-uploader"
                    :show-file-list="false"
                    :before-upload="beforeAvatarUpload"
                    :http-request="handleAvatarUpload"
                    accept="image/png,image/jpeg,image/jpg,image/gif,image/bmp,image/webp"
                  >
                    <el-button round :loading="uploading">选择图片</el-button>
                  </el-upload>
                  <span class="avatar-tip">支持 jpg/png/gif/bmp/webp，不超过 5MB</span>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="个人简介" class="full-width">
              <el-input
                v-model="form.bio"
                type="textarea"
                :rows="3"
                maxlength="500"
                show-word-limit
                placeholder="介绍一下自己吧～"
              />
            </el-form-item>
          </div>

          <div class="edit-actions">
            <el-button round type="primary" @click="submitUpdate" :loading="loading">保存</el-button>
            <el-button round @click="editMode = null">取消</el-button>
          </div>
        </el-form>
      </template>

      <!-- ========== 修改密码 ========== -->
      <template v-else-if="editMode === 'password'">
        <div class="edit-head">
          <h3>修改密码</h3>
          <span class="edit-tip">需要输入当前密码才能修改</span>
        </div>

        <el-form :model="pwdForm" label-position="top" class="edit-form pwd-form">
          <el-form-item label="当前密码">
            <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入当前密码" />
          </el-form-item>

          <el-form-item label="新密码">
            <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少 6 位" />
          </el-form-item>

          <el-form-item label="确认新密码">
            <el-input v-model="pwdForm.new_password_confirm" type="password" show-password placeholder="再次输入新密码" />
          </el-form-item>

          <div class="edit-actions">
            <el-button round type="primary" @click="submitPassword" :loading="pwdLoading">修改密码</el-button>
            <el-button round @click="editMode = null">取消</el-button>
          </div>
        </el-form>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateMeApi, changePasswordApi, uploadAvatarApi } from '@/api/auth'
import dayjs from 'dayjs'

const userStore = useUserStore()

// null = 展示, 'info' = 修改信息, 'password' = 修改密码
const editMode = ref(null)

const form = reactive({
  username: '',
  email: '',
  avatar: '',
  age: null,
  gender: '',
  bio: ''
})

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const loading = ref(false)
const pwdLoading = ref(false)
const uploading = ref(false)

// 头像预览：有值就展示，没有就用用户 store 里的（展示模式也需要）
const avatarPreview = computed(() => form.avatar || userStore.user?.avatar || '')

const genderLabel = computed(() => {
  const map = { male: '男', female: '女', other: '保密', '': '未设置', null: '未设置' }
  return map[userStore.user?.gender] || '未设置'
})

function formatDate(iso) {
  if (!iso) return '—'
  return dayjs(iso).format('YYYY-MM-DD')
}

function loadForm() {
  const u = userStore.user || {}
  form.username = u.username || ''
  form.email = u.email || ''
  form.avatar = u.avatar || ''
  form.age = u.age ?? null
  form.gender = u.gender || ''
  form.bio = u.bio || ''
}

onMounted(loadForm)

// ---------- 头像上传 ----------
const allowedExts = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp']
const MAX_SIZE = 5 * 1024 * 1024

function beforeAvatarUpload(file) {
  if (!allowedExts.includes(file.type)) {
    ElMessage.warning('只能上传 jpg/png/gif/bmp/webp 格式的图片')
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.warning('图片大小不能超过 5MB')
    return false
  }
  return true
}

async function handleAvatarUpload({ file }) {
  uploading.value = true
  try {
    const res = await uploadAvatarApi(file)
    form.avatar = res.avatar
    ElMessage.success('头像上传成功 ✅（记得点保存生效）')
  } catch (e) {
    // request.js 已统一弹错误提示
  } finally {
    uploading.value = false
  }
}

function startEdit(mode) {
  if (mode === 'info') loadForm()
  if (mode === 'password') {
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.new_password_confirm = ''
  }
  editMode.value = mode
}

async function submitUpdate() {
  loading.value = true
  try {
    const res = await updateMeApi({ ...form })
    userStore.user = res
    localStorage.setItem('el_user', JSON.stringify(res))
    ElMessage.success('个人信息已更新 ✅')
    editMode.value = null
  } catch (e) {
    // request.js 已统一弹错误提示
  } finally {
    loading.value = false
  }
}

async function submitPassword() {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (pwdForm.new_password.length < 6) {
    ElMessage.warning('密码长度至少 6 位')
    return
  }
  if (pwdForm.new_password !== pwdForm.new_password_confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdLoading.value = true
  try {
    await changePasswordApi({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    ElMessage.success('密码修改成功 ✅')
    editMode.value = null
  } catch (e) {
    // request.js 已统一弹错误提示
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.profile {
  max-width: 760px;
  margin: 0 auto;
}

.info-card {
  border-radius: 16px;
  border: 1px solid var(--app-border, #eef1f6);
  background: var(--app-card, #fff);
}
.info-card :deep(.el-card__body) {
  padding: 28px;
}

/* ---------- 展示模式 ---------- */
.info-head {
  display: flex;
  align-items: center;
  gap: 18px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--app-border, #eef1f6);
}

.avatar-big {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  font-size: 30px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}
.avatar-big img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.head-meta {
  flex: 1;
  min-width: 0;
}
.head-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
  margin-bottom: 4px;
}
.head-email {
  font-size: 13px;
  color: var(--app-text-secondary, #8a93a6);
}

.head-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 32px;
  padding: 20px 0 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--app-border, #eef1f6);
}

.info-lbl {
  font-size: 14px;
  color: var(--app-text-muted, #9aa3b2);
}

.info-val {
  font-size: 14px;
  color: var(--app-text, #1f2430);
  font-weight: 500;
  max-width: 60%;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 未填写地区高亮提示 */
.region-missing {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #f59e0b !important;
  cursor: pointer;
  font-weight: 500;
  transition: opacity .2s;
}
.region-missing:hover {
  opacity: .75;
}
.region-missing :deep(.el-icon) {
  font-size: 16px;
}

.bio-block {
  padding-top: 16px;
}
.bio-block .info-lbl {
  display: block;
  margin-bottom: 8px;
}
.bio-text {
  margin: 0;
  font-size: 14px;
  color: var(--app-text, #1f2430);
  line-height: 1.7;
}
.bio-empty {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-muted, #9aa3b2);
  font-style: italic;
}

/* ---------- 编辑模式 ---------- */
.edit-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--app-border, #eef1f6);
  margin-bottom: 12px;
}
.edit-head h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.edit-tip {
  font-size: 13px;
  color: var(--app-text-muted, #9aa3b2);
}

.edit-form {
  padding-top: 8px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 24px;
}
.form-grid .full-width {
  grid-column: 1 / -1;
}

.edit-actions {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}

.pwd-form {
  max-width: 480px;
}

/* ---------- 头像上传 ---------- */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 20px;
}
.avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  font-size: 30px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid var(--app-border, #eef1f6);
}
.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.avatar-tip {
  font-size: 12px;
  color: var(--app-text-muted, #9aa3b2);
}
.avatar-uploader :deep(.el-upload) {
  display: inline-block;
}

@media (max-width: 640px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .info-head {
    flex-wrap: wrap;
  }
  .head-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
