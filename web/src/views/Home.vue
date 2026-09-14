<template>
  <div class="page-container home">
    <!-- Hero 欢迎区 -->
    <section class="hero">
      <div class="hero-left">
        <h1 class="hello">
          欢迎回来，
          <span class="name">{{ userStore.user?.username || '同学' }}</span>
        </h1>
        <p class="sub">坚持每天学习，让记忆更持久 🌱</p>
        <div class="cta">
          <el-button type="primary" size="large" round @click="toLearning">
            🚀 开始今日学习
          </el-button>
        </div>
      </div>
      <div class="hero-right">
        <StreakBadge :days="streak.current_streak_days" />
        <div class="hero-note">最长连续 {{ streak.max_streak_days }} 天</div>
      </div>
    </section>

    <!-- 当前单词书 -->
    <CurrentBookCard
      v-if="wordBook.current"
      :name="wordBook.current.name"
      :category="wordBook.current.category"
      :count="wordBook.current.word_count"
      action-text="更换词书"
      @action="toBooks"
    />
    <el-card v-else class="book-card book-card-empty" body-class="book-body">
      <div class="book-icon">📚</div>
      <div class="book-info">
        <div class="book-name">还未选择单词书</div>
        <div class="book-meta"><span class="book-count">选择一个词书开始学习吧</span></div>
      </div>
      <div class="book-actions">
        <el-button type="primary" round size="small" @click="toBooks">去选择</el-button>
      </div>
    </el-card>

    <!-- 学习概览 -->
    <section class="stat-grid">
      <StatCard icon="📈" title="已学 / 所选词书总词数" :value="totalStats.learned">
        <template #suffix> / {{ totalStats.total }}</template>
      </StatCard>
      <StatCard icon="📖" title="今日学习" :value="todayStats.reviewed" />
      <StatCard icon="🗓️" title="累计学习天数" :value="totalStats.daysTotal" />
    </section>

    <!-- 签到日历（每周 7 天） -->
    <el-card class="record-panel" body-class="record-body">
      <div class="record-head">
        <span class="prog-title">📅 签到日历</span>
        <el-date-picker
          v-model="range"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          :clearable="false"
          size="small"
          @change="onRangeChange"
        />
      </div>

      <div class="weekday-row">
        <div v-for="w in weekdayNames" :key="w" class="weekday">{{ w }}</div>
      </div>
      <div class="day-row">
        <div
          v-for="d in calendarDays"
          :key="d.date"
          class="day-cell"
          :class="{ active: d.reviewed > 0, today: d.isToday }"
        >
          <div class="day-circle">
            <template v-if="d.isToday">今</template>
            <template v-else>{{ d.day }}</template>
          </div>
          <div v-if="d.reviewed > 0" class="day-round">{{ d.reviewed }}</div>
        </div>
      </div>

      <div v-if="weekReviewed > 0 || weekLearned > 0" class="week-summary">
        本周累计：学习 {{ weekReviewed }} 词 · 新学 {{ weekLearned }} 词
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useWordBookStore } from '@/stores/wordBook'
import { useSettingsStore } from '@/stores/settings'
import StreakBadge from '@/components/common/StreakBadge.vue'
import { useNavigate } from '@/router'
import { getDashboardStats } from '@/api/stats'

const { toBooks, toLearning } = useNavigate()
const userStore = useUserStore()
const wordBook = useWordBookStore()
const settingsStore = useSettingsStore()

const streak = ref({ current_streak_days: 0, max_streak_days: 0 })
const todayStats = ref({ reviewed: 0 })
const totalStats = ref({ learned: 0, total: 0, daysTotal: 0 })
const days = ref([])

const weekdayNames = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

function thisWeekRange() {
  const today = new Date()
  const dow = today.getDay()
  const diffToMon = (dow + 6) % 7
  const mon = new Date(today)
  mon.setDate(today.getDate() - diffToMon)
  const sun = new Date(mon)
  sun.setDate(mon.getDate() + 6)
  return [mon, sun]
}
const range = ref(thisWeekRange())

function fmt(d) {
  if (!d) return ''
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

async function loadDashboard() {
  try {
    const stats = await getDashboardStats({
      start_date: fmt(range.value?.[0]),
      end_date: fmt(range.value?.[1])
    })
    if (stats?.streak) streak.value = stats.streak
    if (stats?.today) todayStats.value = stats.today
    if (stats?.total) {
      totalStats.value = {
        learned: stats.total.words_learned || 0,
        total: stats.total.words_total || 0,
        daysTotal: stats.total.days_total || 0
      }
    }
    days.value = stats?.days || []
  } catch (e) {
    /* 静默处理 */
  }
}

function onRangeChange() {
  loadDashboard()
}

const calendarDays = computed(() => {
  const [start, end] = range.value || thisWeekRange()
  const dateMap = {}
  for (const d of days.value) dateMap[d.date] = d
  const result = []
  const todayStr = fmt(new Date())
  let cur = new Date(start)
  while (cur <= end) {
    const key = fmt(cur)
    const info = dateMap[key] || { reviewed: 0, learned: 0 }
    result.push({
      date: key,
      day: cur.getDate(),
      reviewed: info.reviewed || 0,
      learned: info.learned || 0,
      isToday: key === todayStr
    })
    cur.setDate(cur.getDate() + 1)
  }
  return result
})

const weekReviewed = computed(() => calendarDays.value.reduce((s, d) => s + d.reviewed, 0))
const weekLearned = computed(() => calendarDays.value.reduce((s, d) => s + d.learned, 0))

onMounted(async () => {
  await settingsStore.init()
  await wordBook.fetchBooks()
  if (settingsStore.currentBookId) wordBook.restoreCurrent(settingsStore.currentBookId)
  await loadDashboard()
})
</script>

<style scoped>
.home {
  max-width: 960px;
}
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  background: linear-gradient(135deg, var(--app-primary-bg, #eef0ff) 0%, var(--app-primary-soft, #f5f3ff) 50%, var(--app-primary-bg2, #eef7ff) 100%);
  border: 1px solid var(--app-border-accent, #e3e6ff);
  border-radius: 16px;
  padding: 26px 32px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.hello {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 800;
  color: var(--app-text, #1f2430);
}
.hello .name {
  color: var(--app-primary, #4f46e5);
}
.sub {
  margin: 0 0 16px;
  color: var(--app-text-secondary, #6b7280);
  font-size: 14px;
}
.cta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.hero-right {
  text-align: center;
  flex-shrink: 0;
}
.hero-note {
  margin-top: 8px;
  color: var(--app-text-muted, #8a93a6);
  font-size: 13px;
}

/* 统计卡片栅格布局 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
/* 空态当前词书行 */
.book-card {
  border-radius: 14px;
  border: 1px solid var(--app-border, #eef1f6);
  margin-bottom: 16px;
}
.book-card :deep(.el-card__body.book-body) {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
}
.book-icon {
  font-size: 26px;
  width: 46px;
  height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--app-bg, #f5f7fa);
  flex-shrink: 0;
}
.book-info {
  flex: 1;
  min-width: 0;
}
.book-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
}
.book-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.book-count {
  color: var(--app-text-secondary, #8a93a6);
  font-size: 13px;
}
.book-actions {
  flex-shrink: 0;
}

/* 签到日历 */
.record-panel {
  border-radius: 14px;
  border: 1px solid var(--app-border, #eef1f6);
}
.record-panel :deep(.el-card__body.record-body) {
  padding: 20px 24px;
}
.record-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.prog-title {
  font-weight: 700;
  font-size: 16px;
  color: var(--app-text, #1f2430);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  margin-bottom: 8px;
}
.weekday {
  text-align: center;
  color: var(--app-text-muted, #9aa3b2);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.day-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}
.day-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 0;
}
/* 学习日历：圆圈大小 40px，配色换回主题靛蓝/紫渐变 */
.day-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
  background: var(--app-bg, #f5f7fa);
  transition: all 0.2s;
}
.day-cell.active .day-circle {
  background: linear-gradient(135deg, var(--app-primary, #6366f1), var(--app-accent, #8b5cf6));
  color: #fff;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}
.day-cell.today .day-circle {
  border: 2px solid var(--app-primary, #4f46e5);
  color: var(--app-primary, #4f46e5);
  font-weight: 800;
}
.day-cell.active.today .day-circle {
  border: none;
}
.day-round {
  margin-top: 3px;
  font-size: 10px;
  color: var(--app-primary, #6366f1);
  font-weight: 600;
}
.week-summary {
  text-align: center;
  color: var(--app-text-secondary, #6b7280);
  font-size: 13px;
  padding-top: 10px;
  margin-top: 8px;
  border-top: 1px dashed var(--app-border, #eef1f6);
}

@media (max-width: 720px) {
  .hero { flex-direction: column; align-items: flex-start; }
  .stat-grid { grid-template-columns: 1fr; }
  .day-circle { width: 34px; height: 34px; font-size: 13px; }
}
</style>