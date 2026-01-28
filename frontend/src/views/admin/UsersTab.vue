<template>
    <v-card border flat class="pa-4">
        <div class="d-flex justify-space-between align-center mb-4">
            <div class="text-h6">Users</div>
            <div>
                <v-btn color="primary" variant="text" prepend-icon="mdi-download" class="mr-2" @click="downloadUsers">Download CSV</v-btn>
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openUserDialog()">Add User</v-btn>
            </div>
        </div>

        <v-text-field
            v-model="searchUsers"
            prepend-inner-icon="mdi-magnify"
            label="Search Users"
            variant="outlined"
            density="compact"
            hide-details
            class="mb-4"
            clearable
        ></v-text-field>

        <v-data-table
            :headers="userHeaders"
            :items="users"
            :loading="loadingUsers"
            :search="searchUsers"
            density="compact"
            class="mb-6"
        >
            <template v-slot:item.id="{ item }">
                <a 
                    v-if="isStudentOrAlumni(item)" 
                    href="#" 
                    @click.prevent="openHistoryDialog(item.id)"
                    class="text-decoration-underline text-primary"
                    style="cursor: pointer;"
                >
                    {{ item.id }}
                </a>
                <span v-else>{{ item.id }}</span>
            </template>
            <template v-slot:item.roles="{ item }">
                <v-chip
                    v-for="roleEntry in item.roles"
                    :key="roleEntry.role"
                    size="x-small"
                    class="mr-1 text-uppercase"
                    color="secondary"
                    variant="tonal"
                >
                    {{ roleEntry.role }}
                </v-chip>
            </template>
            <template v-slot:item.is_active="{ item }">
                <v-chip size="x-small" :color="item.is_active ? 'success' : 'error'">
                    {{ item.is_active ? 'Active' : 'Inactive' }}
                </v-chip>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="small" variant="text" @click="openUserDialog(item)"></v-btn>
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deactivateUser(item)"></v-btn>
            </template>
        </v-data-table>

        <v-divider class="mb-4"></v-divider>

        <div class="text-h6 mb-4">Bulk Upload Users</div>
        <v-file-input
            v-model="userFile"
            label="User CSV"
            accept=".csv"
            variant="outlined"
            density="compact"
        ></v-file-input>
        <v-btn color="primary" @click="uploadUsers" :loading="uploadingUsers" :disabled="!userFile">Upload Users</v-btn>
    </v-card>

    <!-- User Dialog -->
    <v-dialog v-model="userDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingUser ? 'Edit User' : 'Add User' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="userData.id"
                    label="User ID"
                    variant="outlined"
                    :disabled="editingUser"
                ></v-text-field>
                <v-text-field
                    v-model="userData.name"
                    label="Name"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-model="userData.email"
                    label="Email"
                    variant="outlined"
                ></v-text-field>
                <v-text-field
                    v-if="!editingUser"
                    v-model="userData.password"
                    label="Password"
                    variant="outlined"
                    type="password"
                ></v-text-field>
                <v-select
                    v-model="userData.roles"
                    :items="['student', 'teacher', 'administrator', 'alumni']"
                    label="Roles"
                    variant="outlined"
                    multiple
                ></v-select>
                <v-text-field
                    v-if="userData.role === 'student'"
                    v-model="userData.discipline_code"
                    label="Discipline Code"
                    variant="outlined"
                ></v-text-field>
                <v-switch
                    v-model="userData.is_active"
                    label="Active"
                    color="primary"
                ></v-switch>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="userDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveUser" :loading="savingUser">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <AcademicHistoryDialog v-model="historyDialog" :user-id="historyUserId" />

    <v-dialog v-model="resultDialog" max-width="600">
        <v-card>
            <v-card-title :class="['text-h6', resultStats.errors?.length ? 'text-warning' : 'text-success']">
                {{ resultStats.errors?.length ? 'Upload Completed with Errors' : 'Upload Successful' }}
            </v-card-title>
            <v-card-text>
                <div class="text-subtitle-1 mb-2">
                    Successfully Created: {{ resultStats.created }}
                </div>
                
                <div v-if="resultStats.errors?.length">
                    <div class="text-subtitle-2 text-error mb-1">Errors ({{ resultStats.errors.length }}):</div>
                    <v-sheet border class="pa-2 overflow-y-auto" max-height="300" color="grey-lighten-4">
                        <div v-for="(error, i) in resultStats.errors" :key="i" class="text-caption text-error mb-1">
                            {{ error }}
                        </div>
                    </v-sheet>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="resultDialog = false">Close</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color">
        {{ snackbar.text }}
    </v-snackbar>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'
import { downloadDataAsCSV } from '../../utils/csv'
import AcademicHistoryDialog from './AcademicHistoryDialog.vue'

const auth = useAuthStore()

// Users
const users = ref([])
const loadingUsers = ref(false)
const userDialog = ref(false)
const userData = ref({ id: '', name: '', email: '', roles: ['student'], discipline_code: null, is_active: true })
const editingUser = ref(false)
const savingUser = ref(false)
const searchUsers = ref('')
const userFile = ref(null)
const uploadingUsers = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })
const resultDialog = ref(false)
const resultStats = ref({ created: 0, errors: [] })

const userHeaders = [
    { title: 'ID', key: 'id' },
    { title: 'Name', key: 'name' },
    { title: 'Email', key: 'email' },
    { title: 'Roles', key: 'roles', sortable: false },
    { title: 'Status', key: 'is_active' },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchUsers = async () => {
    loadingUsers.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/users/', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        users.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loadingUsers.value = false
    }
}

const openUserDialog = (item = null) => {
    if (item) {
        userData.value = {
            ...item,
            roles: item.roles ? item.roles.map(r => r.role) : []
        }
        editingUser.value = true
    } else {
        userData.value = { id: '', name: '', email: '', password: '', roles: ['student'], discipline_code: null, is_active: true }
        editingUser.value = false
    }
    userDialog.value = true
}

const saveUser = async () => {
    savingUser.value = true
    try {
        const data = { ...userData.value }
        if (editingUser.value) {
            await axios.put(`http://localhost:8000/api/v1/users/${userData.value.id}`, data, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/users/', data, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'User saved successfully', color: 'success' }
        userDialog.value = false
        fetchUsers()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save user: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingUser.value = false
    }
}

const deactivateUser = async (item) => {
    if (!confirm(`Are you sure you want to deactivate user ${item.name}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/users/${item.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'User deactivated', color: 'success' }
        fetchUsers()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to deactivate: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

const uploadUsers = async () => {
    uploadingUsers.value = true
    const formData = new FormData()
    formData.append('file', userFile.value)

    try {
        const res = await axios.post('http://localhost:8000/api/v1/users/bulk-upload', formData, {
            headers: {
                Authorization: `Bearer ${auth.token}`,
                'Content-Type': 'multipart/form-data'
            }
        })
        const count = res.data.users_created
        const errors = res.data.errors
        
        resultStats.value = { created: count, errors: errors }
        resultDialog.value = true
        
        userFile.value = null
        fetchUsers()
    } catch (e) {
        snackbar.value = { show: true, text: 'Upload failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        uploadingUsers.value = false
    }
}


const downloadUsers = () => {
    downloadDataAsCSV(users.value, userHeaders, 'Users', auth.user?.name || 'User')
}

// Academic History
const historyDialog = ref(false)
const historyUserId = ref(null)

const openHistoryDialog = (userId) => {
    historyUserId.value = userId
    historyDialog.value = true
}

const isStudentOrAlumni = (user) => {
    if (!user.roles) return false
    // Handle both array of objects and array of strings if structure varies, 
    // though backend seems to return obj with role enum.
    // user.roles is list of {role: "student", ...}
    const roles = user.roles.map(r => r.role)
    return roles.includes('student') || roles.includes('alumni')
}

onMounted(() => {
    fetchUsers()
})
</script>
