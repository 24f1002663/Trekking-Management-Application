import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRole } from './api.js'

import Login from './views/Login.vue'
import Register from './views/Register.vue'

const routes = [
  { path: '/', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },

  // Unknown paths fall back to login.
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory('/'),
  routes,
})

// Role-based access control (mirrors the backend JWT role checks).
router.beforeEach((to) => {
  if (to.meta.public) return true

  const token = getToken()
  if (!token) return '/'

  const role = getRole()
  if (to.meta.role && to.meta.role !== role) {
    // Signed in but wrong role — send to their own dashboard.
    if (role === 'admin') return '/admindashboard'
    if (role === 'staff') return '/staffdashboard'
    if (role === 'user') return '/userdashboard'
    return '/'
  }
  return true
})

export default router
