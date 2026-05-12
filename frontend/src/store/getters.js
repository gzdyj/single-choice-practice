export default {
  sidebarCollapsed: state => state.app.sidebarCollapsed,
  loading: state => state.app.loading,
  token: state => state.user.token,
  userInfo: state => state.user.userInfo,
  isLoggedIn: state => state.user.isLoggedIn,
  isAdmin: state => state.user.isAdmin,
  isTeacher: state => state.user.isTeacher,
  isStudent: state => state.user.isStudent,
  roleName: state => state.user.roleName,
}
