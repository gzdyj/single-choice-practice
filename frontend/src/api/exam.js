import request from './index'

export function getExams(params) {
  return request.get('/exams', { params })
}

export function getExam(id) {
  return request.get(`/exams/${id}`)
}

export function createExam(data) {
  return request.post('/exams', data)
}

export function updateExam(id, data) {
  return request.put(`/exams/${id}`, data)
}

export function deleteExam(id) {
  return request.delete(`/exams/${id}`)
}

export function getExamQuestions(id) {
  return request.get(`/exams/${id}/questions`)
}

export function startExam(id) {
  return request.post(`/exams/${id}/start`)
}

export function submitExam(examId, answers) {
  return request.post(`/exams/${examId}/submit`, { answers })
}

export function getExamResult(attemptId) {
  return request.get(`/exams/attempt/${attemptId}/result`)
}

export function getMyExamAttempts(params) {
  return request.get('/exams/attempts/mine', { params })
}
