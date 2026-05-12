import { login, register, getCurrentUser } from '@/api/auth'

const rolesMap = {
  admin: '管理员',
  teacher: '教师',
  student: '学生',
}

export default {
  namespaced: true,
  state: {
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      localStorage.setItem('token', token)
    },
    SET_USER_INFO(state, info) {
      state.userInfo = info
      localStorage.setItem('userInfo', JSON.stringify(info))
    },
    CLEAR_USER(state) {
      state.token = ''
      state.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
  },
  actions: {
    async login({ commit }, credentials) {
      const res = await login(credentials)
      commit('SET_TOKEN', res.data.access_token)
      // Fetch user info
      const userRes = await getCurrentUser()
      commit('SET_USER_INFO', userRes.data)
      return userRes.data
    },
    async register({ commit }, data) {
      const res = await register(data)
      return res.data
    },
    async fetchUserInfo({ commit }) {
      const res = await getCurrentUser()
      commit('SET_USER_INFO', res.data)
      return res.data
    },
    logout({ commit }) {
      commit('CLEAR_USER')
    },
  },
  getters: {
    isLoggedIn: state => !!state.token,
    roleName: state => {
      if (!state.userInfo) return ''
      return rolesMap[state.userInfo.role] || state.userInfo.role
    },
    isAdmin: state => state.userInfo?.role === 'admin',
    isTeacher: state => state.userInfo?.role === 'teacher' || state.userInfo?.role === 'admin',
    isStudent: state => state.userInfo?.role === 'student',
  },
}
