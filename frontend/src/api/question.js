import request from './index'

export function getQuestions(params) {
  return request.get('/questions', { params })
}

export function getQuestion(id) {
  return request.get(`/questions/${id}`)
}

export function createQuestion(data) {
  return request.post('/questions', data)
}

export function updateQuestion(id, data) {
  return request.put(`/questions/${id}`, data)
}

export function deleteQuestion(id) {
  return request.delete(`/questions/${id}`)
}

export function getSubjects() {
  return request.get('/questions/subjects')
}
