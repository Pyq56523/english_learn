<template>
  <div class="spelling" @click="focusInput">
    <!-- 顶部统计 -->
    <div class="sp-top">
      <div class="stats">
        <div class="stat">
          <b>{{ queue.length }}</b>
          <span>本组词</span>
        </div>
        <div class="stat">
          <b class="ok">{{ correct }}</b>
          <span>已正确</span>
        </div>
        <div class="stat">
          <b>{{ accuracy }}%</b>
          <span>正确率</span>
        </div>
      </div>
      <WordProgress :total="queue.length" :done="correct" />
    </div>

    <!-- 空队列：引导返回首页或选书 -->
    <div v-if="!queue.length" class="empty-panel">
      <el-empty :description="emptyText">
        <el-button type="primary" round size="large" @click="$router.push('/')">
          返回首页
        </el-button>
      </el-empty>
    </div>

    <!-- 完成本轮 -->
    <div v-else-if="finished" class="done-panel">
      <div class="done-emoji">{{ correct === queue.length ? '🎉' : '💪' }}</div>
      <h3 class="done-title">本轮完成</h3>
      <p class="done-sub">
        本组 {{ queue.length }} 词，正确 {{ correct }} 词，正确率
        <b :class="accuracy >= 80 ? 'ok' : 'warn'">{{ accuracy }}%</b>
      </p>
      <div class="done-actions">
        <el-button round size="large" @click="$router.push('/')">返回首页</el-button>
        <el-button type="primary" round size="large" @click="restart">再来一轮</el-button>
      </div>
    </div>

    <!-- 拼写练习主体 -->
    <template v-else>
      <div class="sp-prompt">
        <div class="meaning">{{ card.meaning }}</div>
        <div v-if="card.phonetic" class="phonetic">/ {{ card.phonetic }} /</div>
      </div>

      <div class="chars" :class="{ shake }">
        <span
          v-for="(ch, i) in letters"
          :key="i"
          :class="['char', charClass(i)]"
        >{{ charText(i) }}</span>
      </div>

      <div class="actions">
        <el-button round @click="speakWord">🔊 发音</el-button>
        <el-button round @click="revealHint">💡 提示首字母</el-button>
        <el-button round type="warning" plain :icon="showAnswer ? '🗏' : undefined" @click="toggleAnswer">
          {{ showAnswer ? '隐藏单词' : '👁 显示单词' }}
        </el-button>
      </div>

      <input
        ref="inputRef"
        class="hidden-input"
        autocomplete="off"
        autocapitalize="off"
        :disabled="finished"
        @keydown="onKeydown"
        @input="onInput"
      />

      <p class="key-hint">
        看着释义用键盘拼出单词 · 打错会闪红提示 · <kbd>Backspace</kbd> 重输 ·
        拼对自动进入下一词
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import WordProgress from '@/components/word/WordProgress.vue'
import { initTTS, speak } from '@/utils/tts'

const props = defineProps({
  queue: { type: Array, default: () => [] },
  emptyText: { type: String, default: '当前没有可拼写的单词，先去首页选一本学吧' }
})

const index = ref(0)
const pendingIndex = ref(0) // 当前已正确输入的字母个数（即下一个待输入位置）
const correct = ref(0)
const wrong = ref(0)
const finished = ref(false)
const shake = ref(false)
const reveal = ref(false) // 是否展示当前待输入字母
const showAnswer = ref(false) // 是否展示完整单词（看答案）
const inputRef = ref(null)

const card = computed(() => props.queue[index.value] || null)
const letters = computed(() => (card.value?.word || '').split(''))
const accuracy = computed(() =>
  props.queue.length ? Math.round((correct.value / props.queue.length) * 100) : 0
)

function resetRound() {
  index.value = 0
  pendingIndex.value = 0
  correct.value = 0
  wrong.value = 0
  reveal.value = false
  showAnswer.value = false
  finished.value = false
}

function speakWord() {
  if (!card.value) return
  speak(card.value.word)
}

function revealHint() {
  if (!card.value || finished.value) return
  if (!reveal.value) {
    reveal.value = true
    speakWord()
  }
}

function toggleAnswer() {
  if (!card.value || finished.value) return
  showAnswer.value = !showAnswer.value
  if (showAnswer.value) speakWord()
}

function triggerShake() {
  shake.value = true
  clearTimeout(triggerShake._t)
  triggerShake._t = setTimeout(() => {
    shake.value = false
  }, 320)
}

function handleLetter(raw) {
  const expected = card.value?.word[pendingIndex.value]?.toLowerCase()
  const typed = (raw || '').toLowerCase()
  if (!expected) return

  // 开始拼写时收回看答案状态
  if (showAnswer.value && pendingIndex.value === 0) showAnswer.value = false

  if (typed === expected) {
    reveal.value = false
    pendingIndex.value += 1
    if (pendingIndex.value === letters.value.length) {
      correct.value += 1
      // 不在这里朗读：避免 850ms 后被 advance() 打断造成卡顿，进入下一词时统一朗读
      setTimeout(() => advance(), 850)
    }
  } else {
    wrong.value += 1
    triggerShake()
  }
}

function retype() {
  reveal.value = false
  pendingIndex.value = Math.max(0, pendingIndex.value - 1)
}

function advance() {
  index.value += 1
  pendingIndex.value = 0
  reveal.value = false
  showAnswer.value = false
  if (index.value >= props.queue.length) {
    finished.value = true
  } else {
    speakWord() // 进入下一个单词时先朗读一遍英语
    focusInput()
  }
}

function restart() {
  resetRound()
  speakWord()
  focusInput()
}

function onKeydown(e) {
  if (finished.value) return
  const k = e.key
  if (k === 'Backspace') {
    e.preventDefault()
    retype()
    return
  }
  if (k === 'Enter') {
    e.preventDefault()
    if (pendingIndex.value >= letters.value.length) advance()
    return
  }
  if (k.length === 1) {
    // 可打印字符，吞掉默认输入，手动处理
    e.preventDefault()
    handleLetter(k)
  }
}

function onInput(e) {
  // 安全兜底：输入框本身不保留任何文本
  if (e.target) e.target.value = ''
}

function focusInput() {
  if (finished.value) return
  nextTick(() => inputRef.value && inputRef.value.focus())
}

function charClass(i) {
  if (showAnswer.value) return 'answer'
  return {
    ok: i < pendingIndex.value,
    cur: i === pendingIndex.value && !reveal.value,
    hit: i === pendingIndex.value && reveal.value
  }
}

function charText(i) {
  if (showAnswer.value) return letters.value[i] // 看答案：展示完整单词
  if (i < pendingIndex.value) return letters.value[i] // 已正确 -> 绿色
  if (i === pendingIndex.value && reveal.value) return letters.value[i] // 提示展示
  return '' // 占位
}

onMounted(() => {
  initTTS() // 尽早预加载语音引擎
  focusInput()
  speakWord() // 首个单词自动朗读一遍英语
})
watch(
  () => props.queue,
  () => resetRound(),
  { immediate: true }
)
watch(
  () => index.value,
  () => focusInput()
)
</script>

<style scoped>
.spelling {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 640px;
  margin: 0 auto;
  min-height: 420px;
  cursor: text;
  user-select: none;
}

/* 顶部统计 */
.sp-top {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-bottom: 40px;
}
.stats {
  display: flex;
  gap: 36px;
}
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.stat b {
  font-size: 24px;
  font-weight: 800;
  color: var(--app-text, #1f2430);
  letter-spacing: 0.5px;
}
.stat b.ok {
  color: var(--app-ok, #16a34a);
}
.stat span {
  font-size: 12px;
  color: var(--app-text-muted, #9aa3b2);
  letter-spacing: 1px;
}

/* 中文提示（中大字号，居中） */
.sp-prompt {
  margin-bottom: 36px;
  text-align: center;
  animation: rise 0.35s ease;
}
.meaning {
  font-size: 28px;
  font-weight: 700;
  color: var(--app-text, #1f2430);
  letter-spacing: 1px;
  line-height: 1.4;
}
.phonetic {
  margin-top: 10px;
  font-size: 16px;
  color: var(--app-text-muted, #98a1b3);
  letter-spacing: 1px;
}

/* 字母槽（大小适中） */
.chars {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  min-height: 76px;
  margin-bottom: 36px;
}
.char {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 62px;
  font-size: 32px;
  font-weight: 700;
  border-radius: 12px;
  border-bottom: 4px solid var(--app-border-accent, #e2e6ee);
  background: var(--app-fill-soft, rgba(255, 255, 255, 0.7));
  color: transparent;
  transition: all 0.18s ease;
}
.char.ok {
  color: var(--app-ok, #16a34a);
  border-bottom-color: var(--app-accent, #22c55e);
  background: var(--app-ok-bg, #f2fcf4);
}
.char.cur {
  color: var(--app-cursor, #4f46e5);
  border-bottom-color: var(--app-cursor, #6366f1);
  background: var(--app-cur-bg, #eef0ff);
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.16);
  transform: translateY(-2px);
}
.char.hit {
  color: var(--app-warn-strong, #f59e0b);
  border-bottom-color: var(--app-warn-strong, #f59e0b);
  background: var(--app-warn-bg, #fff8e8);
}
/* 看答案：完整展示单词 */
.char.answer {
  color: var(--app-cursor, #4f46e5);
  border-bottom-color: var(--app-accent, #6366f1);
  background: var(--app-cur-bg, #eef0ff);
}
.shake .char {
  animation: shake 0.3s;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 26px;
}
.key-hint {
  font-size: 12px;
  color: var(--app-text-muted, #a7b0c0);
  text-align: center;
  line-height: 1.8;
}
.key-hint kbd {
  padding: 1px 6px;
  border-radius: 6px;
  background: var(--app-fill-soft, #eef1f6);
  border: 1px solid var(--app-border, #dde2ec);
  color: var(--app-text-secondary, #7c87a0);
  font-family: inherit;
}

/* 隐藏输入框：始终聚焦但不可见 */
.hidden-input {
  position: absolute;
  left: -9999px;
  top: 0;
  width: 1px;
  height: 1px;
  opacity: 0;
}

/* 空 / 完成 */
.empty-panel {
  padding-top: 40px;
}
.done-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 40px;
  text-align: center;
}
.done-emoji {
  font-size: 56px;
  margin-bottom: 16px;
}
.done-title {
  margin: 0 0 10px;
  font-size: 24px;
  color: var(--app-text, #1f2430);
}
.done-sub {
  margin: 0 0 28px;
  font-size: 15px;
  color: var(--app-text-secondary, #8a93a6);
}
.done-sub b.ok {
  color: var(--app-ok, #16a34a);
}
.done-sub b.warn {
  color: var(--app-warn-strong, #f59e0b);
}
.done-actions {
  display: flex;
  gap: 12px;
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-6px);
  }
  50% {
    transform: translateX(6px);
  }
  75% {
    transform: translateX(-4px);
  }
}

@media (max-width: 520px) {
  .meaning {
    font-size: 23px;
  }
  .char {
    width: 34px;
    height: 52px;
    font-size: 26px;
  }
  .sp-prompt {
    margin-bottom: 28px;
  }
}
</style>