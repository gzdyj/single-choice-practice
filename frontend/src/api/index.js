import axios from 'axios'
import { Message } from 'element-ui'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Request interceptor - inject token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error),
)

// Response interceptor - handle errors
request.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || '请求失败'

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      // Redirect to login if not already there
      if (window.location.hash !== '#/login') {
        Message.error('登录已过期，请重新登录')
        window.location.hash = '#/login'
      }
    } else if (status === 403) {
      Message.error('权限不足')
    } else if (status === 422) {
      Message.error(error.response?.data?.detail?.[0]?.msg || '参数错误')
    } else if (status >= 500) {
      Message.error('服务器错误')
    } else if (detail) {
      Message.error(detail)
    }

    return Promise.reject(error)
  },
)

export default request
