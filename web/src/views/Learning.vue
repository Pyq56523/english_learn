<template>
  <div class="page-container learning">
    <PageHeader>
      <template #title>
        <div class="mode-tabs">
          <button
            class="tab"
            :class="{ active: learning.mode === 'learn' }"
            @click="switchMode('learn')"
          >
            学习
            <span class="tab-count">{{ learning.summary.learn_count }}</span>
          </button>
          <button
            class="tab"
            :class="{ active: learning.mode === 'review' }"
            @click="switchMode('review')"
          >
            复习
            <span class="tab-count">{{ learning.summary.total_due }}</span>
          </button>
        </div>
      </template>
      <WordProgress :total="learning.queue.length" :done="learning.queueIndex" />
    </PageHeader>

    <div class="mode-switch">
      <el-segmented
        v-model="mode"
        :options="[
          { label: '🂡 卡片学习', value: 'card' },
          { label: '⌨️ 键盘拼写', value: 'spell' }
        ]"
        size="large"
      />
    </div>

    <!-- A. 卡片学习（不背单词风格） -->
    <template v-if="mode === 'card'">
      <div v-if="learning.current" class="stage">
        <div class="meta">
          <el-tag size="large" round :type="chipType">{{ chipText }}</el-tag>
          <span class="count">第 {{ learning.queueIndex + 1 }} / {{ learning.queue.length }} 词</span>
        </div>

        <div class="card-glows">
          <span class="glow glow-a"></span>
          <span class="glow glow-b"></span>
        </div>

        <WordCard :card="learning.current" :flipped="flipped" @flip="flipped = !flipped" />

        <transition name="fade">
          <div v-if="flipped" class="stage-bottom">
            <ReviewRating @rate="onRate" />
          </div>
          <div v-else class="tip">👆 点击卡片翻面，回忆它的释义</div>
        </transition>
      </div>

      <div v-else class="done empty-wrap">
        <el-empty :description="emptyTip">
          <el-button type="primary" round size="large" @click="toHome">
            返回首页
          </el-button>
        </el-empty>
      </div>
    </template>

    <!-- B. 键盘拼写：学习拼今日已学新词，复习拼到期复习卡 -->
    <template v-else>
      <SpellingPractice :queue="spellQueue" :empty-text="spellEmptyText" />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import WordCard from '@/components/word/WordCard.vue'
import ReviewRating from '@/components/word/ReviewRating.vue'
import WordProgress from '@/components/word/WordProgress.vue'
import SpellingPractice from '@/components/word/SpellingPractice.vue'
import { useLearningStore } from '@/stores/learning'
import { useNavigate } from '@/router'
import { initTTS, speak } from '@/utils/tts'

const learning = useLearningStore()
const { toHome } = useNavigate()
const flipped = ref(false)
const mode = ref('card') // card | spell

const chipText = computed(() => (learning.mode === 'review' ? '🔁 复习' : '🌟 新词'))
const chipType = computed(() => (learning.mode === 'review' ? 'primary' : 'warning'))
const emptyTip = computed(() => {
  if (learning.queue.length) {
    return learning.mode === 'review' ? '今日复习已完成' : '今日新词已全部学完'
  }
  return learning.mode === 'review' ? '今天没有到期复习的词' : '今天没有待学的新词'
})

// 拼写队列与模式对应：学习→今日已学新词，复习→到期复习卡
const spellQueue = computed(() =>
  learning.mode === 'review' ? learning.dueCards : learning.learnedCards
)
const spellEmptyText = computed(() =>
  learning.mode === 'review'
    ? '今天没有到期复习的词，先去卡片学习吧'
    : '今天还没有学过的词，先去卡片学习吧'
)

function switchMode(mode) {
  flipped.value = false
  learning.setMode(mode)
}

function speakWord() {
  speak(learning.current?.word)
}

async function onRate(quality) {
  await learning.rateCard(quality)
  flipped.value = false
}

// 换到新卡片时自动朗读一次英语单词
watch(
  () => learning.current,
  (card) => {
    if (card) speakWord()
  },
  { immediate: true }
)

onMounted(async () => {
  initTTS() // 预加载语音引擎，降低首次朗读延迟
  if (!learning.loaded) await learning.fetchTodayCards()
})
</script>

<style scoped>
.learning {
  max-width: 720px;
  margin: 0 auto;
}
/* 学习/复习 模式切换器 */
.mode-tabs {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px;
  border-radius: 999px;
  background: var(--app-fill-soft, #eceef7);
}
.tab {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 22px;
  border: none;
  border-radius: 999px;
  background: transparent;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 3px;
  color: var(--app-text-secondary, #7c87a0);
  cursor: pointer;
  transition: all 0.25s ease;
}
.tab:hover {
  color: var(--app-primary, #4f46e5);
}
.tab.active {
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
}
.tab-count {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0;
  padding: 1px 9px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.08);
  transition: background 0.25s ease;
}
.tab.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
}
.mode-switch {
  display: flex;
  justify-content: center;
  margin-bottom: 26px;
}
.mode-switch :deep(.el-segmented) {
  background: var(--app-fill-soft, #eceef7);
  border-radius: 999px;
  padding: 4px;
}
.mode-switch :deep(.el-segmented__item) {
  font-weight: 600;
  border-radius: 999px;
}
.mode-switch :deep(.el-segmented__item-selected) {
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.24);
}
.card-glows {
  position: relative;
  width: 100%;
  max-width: 460px;
  height: 0;
  display: flex;
  justify-content: center;
}
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  pointer-events: none;
}
.glow-a {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #a5a4ff, transparent 65%);
  top: -40px;
  left: 12%;
}
.glow-b {
  width: 170px;
  height: 170px;
  background: radial-gradient(circle, #c7b8ff, transparent 65%);
  top: 30px;
  right: 14%;
  opacity: 0.4;
}
.meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 10px 0 18px;
}
.count {
  color: #aeb6c4;
  letter-spacing: 0.5px;
  font-size: 14px;
}
.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.tip {
  margin-top: 20px;
  padding: 10px 20px;
  border-radius: 999px;
  background: var(--app-fill-soft, #f4f5ff);
  color: var(--app-text-secondary, #7c87a0);
  font-size: 14px;
  border: 1px solid var(--app-fill-soft-border, #e6e5ff);
}
.stage-bottom {
  width: 100%;
}
.done {
  display: flex;
  justify-content: center;
  padding-top: 48px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>