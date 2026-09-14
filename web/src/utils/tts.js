
let cachedVoices = []
let _bound = false

// 直接基于语音名打分，优先"本地/自然"语音
function voiceScore(v) {
  const name = (v.name || '').toLowerCase()
  const lang = (v.lang || '').toLowerCase()
  let score = 0
  if (lang.startsWith('en-us')) score += 5
  else if (lang.startsWith('en')) score += 3
  // 在线合成依赖网络：延迟高 -> 降权
  if (name.includes('google')) score -= 4
  if (name.includes('online') || name.includes('enhanced')) score -= 2
  // 本地自然语音：几乎零延迟
  if (name.includes('microsoft')) score += 2
  if (name.includes('aria') || name.includes('jenny') || name.includes('anna'))
    score += 3
  return score
}

function loadVoices() {
  if (!('speechSynthesis' in window)) return
  cachedVoices = window.speechSynthesis.getVoices() || []
}

function ensureBound() {
  if (_bound || !('speechSynthesis' in window)) return
  _bound = true
  window.speechSynthesis.onvoiceschanged = loadVoices
}

// Chrome bug 兜底：长时间使用 speechSynthesis 会"卡死不出声"，定时 pause/resume 保活
let _keepAlive = null

/** 尽早调用以预热语音引擎 */
export function initTTS() {
  if (!('speechSynthesis' in window)) return
  ensureBound()
  loadVoices()
  if (_keepAlive) return
  _keepAlive = window.setInterval(() => {
    try {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause()
        window.speechSynthesis.resume()
      }
    } catch (e) {
      /* 忽略 */
    }
  }, 10000)
}

function pickVoice() {
  if (!cachedVoices.length) loadVoices()
  if (!cachedVoices.length) return null
  let best = cachedVoices[0]
  let bestScore = -Infinity
  for (const v of cachedVoices) {
    const s = voiceScore(v)
    if (s > bestScore) {
      bestScore = s
      best = v
    }
  }
  return best
}

/**
 * 朗读文本（即时播放，未指定语音时自动选本地自然美音）
 * 默认立即打断上一次朗读：快速切换卡片时只读最新一个，不会排队逐个读
 * @param {string} text 朗读内容
 * @param {object} [opts] { lang, rate, pitch, onend, immediate }
 */
export function speak(text, opts = {}) {
  if (!text || !('speechSynthesis' in window)) return
  const { lang = 'en-US', rate = 1, pitch = 1, onend, immediate = true } = opts
  ensureBound()
  // 先取消再朗读：消除排队延迟（cancel 是异步生效的，立即 speak 会接上最新文本）
  if (immediate) {
    try {
      window.speechSynthesis.cancel()
      window.speechSynthesis.resume() // 部分浏览器 cancel 后挂起，resume 恢复
    } catch (e) {
      /* 忽略 */
    }
  }
  try {
    const u = new SpeechSynthesisUtterance(text)
    u.lang = lang
    u.rate = rate
    u.pitch = pitch
    const voice = pickVoice()
    if (voice) u.voice = voice
    if (typeof onend === 'function') u.onend = onend
    window.speechSynthesis.speak(u)
  } catch (e) {
    /* 忽略发音失败 */
  }
}

/** 停止朗读 */
export function stopSpeak() {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
}