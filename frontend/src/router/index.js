import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/practice',
    children: [
      {
        path: 'practice',
        name: 'Practice',
        component: () => import('@/views/Practice.vue'),
        meta: { title: '刷题练习', icon: 'edit' },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '练习记录', icon: 'time' },
      },
      {
        path: 'questions',
        name: 'Questions',
        component: () => import('@/views/Questions.vue'),
        meta: { title: '题库管理', icon: 'document', roles: ['admin', 'teacher'] },
      },
      {
        path: 'questions/create',
        name: 'CreateQuestion',
        component: () => import('@/views/QuestionEdit.vue'),
        meta: { title: '新增题目', icon: 'plus', roles: ['admin', 'teacher'] },
      },
      {
        path: 'questions/edit/:id',
        name: 'EditQuestion',
        component: () => import('@/views/QuestionEdit.vue'),
        meta: { title: '编辑题目', icon: 'edit', roles: ['admin', 'teacher'] },
      },
      {
        path: 'import',
        name: 'Import',
        component: () => import('@/views/ImportQuestions.vue'),
        meta: { title: '题库导入', icon: 'upload', roles: ['admin', 'teacher'] },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'user', roles: ['admin'] },
      },
    ],
  },
]

const router = new VueRouter({
  routes,
  scrollBehavior: () => ({ y: 0 }),
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isLoggedIn = !!store.state.user.token

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (!to.meta.requiresAuth && isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Practice' })
    return
  }

  // Role-based access
  if (to.meta.roles) {
    const userRole = store.state.user.userInfo?.role
    if (!to.meta.roles.includes(userRole)) {
      next({ name: 'Practice' })
      return
    }
  }

  next()
})

export default router
