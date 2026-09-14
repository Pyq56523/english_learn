import dayjs from 'dayjs'

/** 日期格式化（默认 YYYY-MM-DD） */
export function formatDate(date, fmt = 'YYYY-MM-DD') {
  if (!date) return ''
  return dayjs(date).format(fmt)
}

/** 千分位数字 */
export function formatNumber(n) {
  return (n || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/** 百分比（0-1 → xx%） */
export function formatPercent(rate) {
  return `${Math.round((rate || 0) * 100)}%`
}