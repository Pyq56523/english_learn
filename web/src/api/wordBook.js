import request from './request'

export function getWordBooks(params = {}) {
  return request.get('/word-books', { params })
}

export function getWordBookDetail(id) {
  return request.get(`/word-books/${id}`)
}