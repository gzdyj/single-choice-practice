import request from './index'

export function importQuestions(formData) {
  return request.post('/questions/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getImportFormats() {
  return request.get('/questions/import/formats')
}
