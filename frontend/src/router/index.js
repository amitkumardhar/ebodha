import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import Login from '../views/Login.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    redirect: (to) => {
      // Redirect based on role
      const auth = useAuthStore()
      if (!auth.isAuthenticated) return '/login'
      if (auth.isStudent) return '/student'
      if (auth.isTeacher) return '/teacher'
      if (auth.isAdmin) return '/admin'
      if (auth.isAlumni) return '/student' // Alumni sees student view?
      return '/login'
    }
  },
  {
    path: '/student',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, roles: ['student', 'alumni'] }
  },
  {
    path: '/teacher',
    name: 'TeacherDashboard',
    component: TeacherDashboard,
    meta: { requiresAuth: true, roles: ['teacher'] }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, roles: ['administrator'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Initialize auth if token exists but user not loaded
  if (auth.token && !auth.user) {
    await auth.fetchUser()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(auth.currentRole)) {
    // Role mismatch, redirect to correct dashboard or login
    if (auth.isStudent) next('/student')
    else if (auth.isTeacher) next('/teacher')
    else if (auth.isAdmin) next('/admin')
    else next('/login')
  } else {
    next()
  }
})

export default router
