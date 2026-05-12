export default {
  namespaced: true,
  state: {
    sidebarCollapsed: false,
    loading: false,
  },
  mutations: {
    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    },
    SET_LOADING(state, val) {
      state.loading = val
    },
  },
  actions: {
    toggleSidebar({ commit }) {
      commit('TOGGLE_SIDEBAR')
    },
  },
}
