import request from './request'

export function getSettings() {
  return request.get('/settings')
}

export function updateSettings(payload) {
  return request.put('/settings', payload)
}