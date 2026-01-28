<template>
    <v-dialog v-model="dialog" max-width="400">
        <v-card>
            <v-card-title>Change Password</v-card-title>
            <v-card-text>
                <v-form @submit.prevent="changePassword" ref="form">
                    <v-text-field
                        v-model="currentPassword"
                        label="Current Password"
                        type="password"
                        variant="outlined"
                        :rules="[v => !!v || 'Required']"
                        class="mb-2"
                    ></v-text-field>
                    <v-text-field
                        v-model="newPassword"
                        label="New Password"
                        type="password"
                        variant="outlined"
                        :rules="[v => !!v || 'Required', v => v.length >= 6 || 'Min 6 chars']"
                        class="mb-2"
                    ></v-text-field>
                    <v-text-field
                        v-model="confirmPassword"
                        label="Confirm New Password"
                        type="password"
                        variant="outlined"
                        :rules="[v => !!v || 'Required', v => v === newPassword || 'Passwords do not match']"
                    ></v-text-field>
                </v-form>
                <div v-if="error" class="text-caption text-error">{{ error }}</div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="dialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="changePassword" :loading="loading">Change</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const props = defineProps({
    modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const auth = useAuthStore()
const router = useRouter()

const dialog = ref(props.modelValue)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const form = ref(null)

watch(() => props.modelValue, (val) => {
    dialog.value = val
    if (val) {
        currentPassword.value = ''
        newPassword.value = ''
        confirmPassword.value = ''
        error.value = ''
    }
})

watch(dialog, (val) => {
    emit('update:modelValue', val)
})

const changePassword = async () => {
    const { valid } = await form.value.validate()
    if (!valid) return

    loading.value = true
    error.value = ''
    try {
        await axios.put('http://localhost:8000/api/v1/users/me/password', {
            current_password: currentPassword.value,
            new_password: newPassword.value
        }, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        // Success - Logout
        auth.logout()
        router.push('/login')
        dialog.value = false
        
    } catch (e) {
        console.error(e)
        error.value = 'Failed: ' + (e.response?.data?.detail || e.message)
    } finally {
        loading.value = false
    }
}
</script>
