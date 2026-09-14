import request from './request'

export function getTodayCards() {
  return request.get('/learning/today')
}

export function startLearning(bookId) {
  return request.post('/learning/start', { book_id: bookId })
}

export function submitReview(payload) {
  return request.post('/learning/review', payload)
}

export function getProgress(bookId) {
  return request.get(`/learning/progress/${bookId}`)
}