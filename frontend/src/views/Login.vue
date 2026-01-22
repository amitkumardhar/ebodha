<template>
  <v-container class="fill-height justify-center bg-background">
    <v-card width="400" flat border class="pa-4">
        <div class="text-center mb-6">
            <div class="text-h4 font-weight-bold mb-2">Login</div>
            <div class="text-caption text-medium-emphasis">Enter your credentials to access the system</div>
        </div>

      <v-form @submit.prevent="handleLogin">
        <v-text-field
          v-model="username"
          label="User ID"
          variant="outlined"
          density="comfortable"
          hide-details="auto"
          class="mb-4"
        ></v-text-field>

        <v-text-field
          v-model="password"
          label="Password"
          type="password"
          variant="outlined"
          density="comfortable"
          hide-details="auto"
          class="mb-4"
        ></v-text-field>

        <v-select
            v-model="selectedRole"
            :items="roles"
            label="Role (Optional)"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
            class="mb-6"
        ></v-select>

        <v-btn
          type="submit"
          block
          color="primary"
          height="48"
          variant="flat"
          :loading="loading"
        >
          Sign In
        </v-btn>
        
        <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-4"
        >
            {{ error }}
        </v-alert>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const username = ref('')
const password = ref('')
const selectedRole = ref(null)
const roles = ['student', 'teacher', 'administrator', 'alumni']
const loading = ref(false)
const error = ref('')

const auth = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
    loading.value = true
    error.value = ''
    try {
        await auth.login(username.value, password.value, selectedRole.value)
        // Router guard will handle redirection
        router.push('/')
    } catch (e) {
        error.value = 'Invalid credentials or role.'
    } finally {
        loading.value = false
    }
}
</script>
