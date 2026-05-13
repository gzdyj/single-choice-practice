import request from './index'

export function getRandomQuestion(params) {
  return request.get('/practice/random', { params })
}

export function submitAnswer(data) {
  return request.post('/practice/submit', data)
}

export function getHistory(params) {
  return request.get('/practice/history', { params })
}

export function getStats() {
  return request.get('/practice/stats')
}
