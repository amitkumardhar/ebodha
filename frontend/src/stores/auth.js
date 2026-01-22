import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/v1'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    roles: [],
    currentRole: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isStudent: (state) => state.currentRole === 'student',
    isTeacher: (state) => state.currentRole === 'teacher',
    isAdmin: (state) => state.currentRole === 'administrator',
    isAlumni: (state) => state.currentRole === 'alumni',
  },
  actions: {
    async login(username, password, role) {
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)
      if (role) {
        params.append('role', role) // Initial role selection if supported by backend login form, though backend endpoint currently takes 'role' as query param? No, let's check.
        // endpoints/login.py: login_access_token(..., role: str = None)
        // It's a query param or form field? FastAPI OAuth2PasswordRequestForm is form-data.
        // Extra params in Depends need to be handled.
        // Actually, 'role' in login_access_token is a query parameter if not in form. 
        // Let's assume query param for 'role' or part of the form data if we append it.
        // BUT, `OAuth2PasswordRequestForm` is strict. `role` is a separate dependency.
        // So it should be a query param.
      }

      try {
        const response = await axios.post(`${API_URL}/login/access-token?role=${role || ''}`, params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })

        this.token = response.data.access_token
        localStorage.setItem('token', this.token)

        await this.fetchUser()

        // Ensure currentRole is set
        if (!this.currentRole && this.roles.length > 0) {
          this.currentRole = this.roles[0]
        }

        return true
      } catch (error) {
        console.error('Login failed', error)
        throw error
      }
    },
    async fetchUser() {
      if (!this.token) return
      try {
        const response = await axios.get(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.user = response.data
        // Extract roles from user object. 
        // User schema: id, name, ..., roles: [{role: '...'}, ...]
        this.roles = this.user.roles.map(r => r.role)

        // We need to know the *current* role. 
        // The backend /me returns the user, but does it return the current role from the token?
        // backend: user.current_role = token_data.role (runtime attribute)
        // Pydantic schema User (UserInDBBase) does NOT have current_role.
        // So /me returns the static user data.
        // We can decode the token to get the current role, OR we can store it in state on login/switch.

        // Let's parse the token to get the current role safely.
        const payload = JSON.parse(atob(this.token.split('.')[1]))
        this.currentRole = payload.role

      } catch (error) {
        console.error('Fetch user failed', error)
        this.logout()
      }
    },
    async switchRole(newRole) {
      try {
        const response = await axios.post(`${API_URL}/login/switch-role?new_role=${newRole}`, {}, {
          headers: { Authorization: `Bearer ${this.token}` }
        })

        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        this.currentRole = newRole

        // Reload user or just update state
        await this.fetchUser()

      } catch (error) {
        console.error('Switch role failed', error)
        throw error
      }
    },
    logout() {
      this.user = null
      this.token = null
      this.roles = []
      this.currentRole = null
      localStorage.removeItem('token')
      // router push login handled in component or interceptor
    }
  }
})
