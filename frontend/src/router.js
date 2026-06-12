import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRole } from './api.js'

import Login from './views/Login.vue'
import Register from './views/Register.vue'

import AdminDashboard from './views/admin/AdminDashboard.vue'
import AdminStaff from './views/admin/AdminStaff.vue'
import AdminTreks from './views/admin/AdminTreks.vue'
import AdminUsers from './views/admin/AdminUsers.vue'
import AdminBookings from './views/admin/AdminBookings.vue'
import AdminReports from './views/admin/AdminReports.vue'
import AdminNotifications from './views/admin/AdminNotifications.vue'

const routes = [
  { path: '/', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },

  { path: '/admindashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/adminstaff', component: AdminStaff, meta: { role: 'admin' } },
  { path: '/admintreks', component: AdminTreks, meta: { role: 'admin' } },
  { path: '/adminusers', component: AdminUsers, meta: { role: 'admin' } },
  { path: '/adminbookings', component: AdminBookings, meta: { role: 'admin' } },
  { path: '/adminreports', component: AdminReports, meta: { role: 'admin' } },
  { path: '/adminnotifications', component: AdminNotifications, meta: { role: 'admin' } },

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
