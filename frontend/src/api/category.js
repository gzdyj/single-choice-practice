import request from './index'

export function getAllCategories() {
  return request.get('/categories/all')
}

export function getCategories(params) {
  return request.get('/categories', { params })
}

export function getCategory(id) {
  return request.get(`/categories/${id}`)
}

export function createCategory(data) {
  return request.post('/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/categories/${id}`)
}
