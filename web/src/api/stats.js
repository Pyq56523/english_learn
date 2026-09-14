import request from './request'

export function getDashboardStats(params) {
  return request.get('/stats/dashboard', { params })
}

export function getHeatmap() {
  return request.get('/stats/heatmap')
}

export function getStreak() {
  return request.get('/stats/streak')
}