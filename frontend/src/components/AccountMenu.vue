<template>
  <v-menu offset-y v-if="auth.isAuthenticated">
    <template v-slot:activator="{ props }">
      <v-btn
        icon
        v-bind="props"
        variant="text"
      >
        <v-icon>mdi-account-circle-outline</v-icon>
      </v-btn>
    </template>
    <v-list density="compact" elevation="2">
        <v-list-item>
            <v-list-item-title class="text-subtitle-2 font-weight-bold">
                {{ auth.user?.name }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
                {{ auth.currentRole?.toUpperCase() }}
            </v-list-item-subtitle>
        </v-list-item>
      <template v-if="availableRoles.length > 0">
        <v-divider class="my-1"></v-divider>
        <v-list-subheader class="text-caption text-uppercase">Switch Role</v-list-subheader>
        <v-list-item
          v-for="role in availableRoles"
          :key="role"
          @click="switchRole(role)"
          link
        >
          <v-list-item-title class="text-body-2">{{ role.toUpperCase() }}</v-list-item-title>
        </v-list-item>
      </template>

      <v-divider class="my-1"></v-divider>
      <v-list-item @click="logout" link>
        <v-list-item-title class="text-body-2 text-error">Log Out</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const availableRoles = computed(() => {
    return auth.roles.filter(r => r !== auth.currentRole)
})

const switchRole = async (role) => {
    try {
        await auth.switchRole(role)
        // Redirect will happen in router guard or manually here
        if (role === 'student') router.push('/student')
        else if (role === 'teacher') router.push('/teacher')
        else if (role === 'administrator') router.push('/admin')
    } catch (e) {
        // error handled in store
    }
}

const logout = () => {
    auth.logout()
    router.push('/login')
}
</script>
