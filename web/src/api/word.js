import request from './request'

export function getWords(params = {}) {
  return request.get('/words', { params })
}

export function getWord(id) {
  return request.get(`/words/${id}`)
}