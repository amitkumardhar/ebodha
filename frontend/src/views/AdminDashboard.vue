<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">Admin Dashboard</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">Welcome, {{ auth.user?.name }}</div>
        </div>
    </div>
    
    <v-tabs v-model="tab" color="primary">
        <v-tab value="users">Users</v-tab>
        <v-tab value="semesters">Semesters</v-tab>
        <v-tab value="offerings">Course Offerings</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-4">
        <v-window-item value="users">
            <v-card border flat class="pa-4">
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
        </v-window-item>

        <v-window-item value="semesters">
             <v-card border flat class="pa-4">alter table public.user modify discipline_id discipline_code integer;
                <div class="d-flex justify-space-between align-center mb-4">
                     <div class="text-h6">Semesters</div>
                     <v-btn size="small" variant="outlined">Create (Not Implemented)</v-btn>
                </div>
                <v-list density="compact" border>
                     <v-list-item v-for="sem in semesters" :key="sem.id">
                         <v-list-item-title>Semester {{ sem.id }}</v-list-item-title>
                         <v-list-item-subtitle>{{ sem.start_date }} - {{ sem.end_date }}</v-list-item-subtitle>
                     </v-list-item>
                </v-list>
            </v-card>
        </v-window-item>

        <v-window-item value="offerings">
             <v-card border flat class="pa-4">
                <div class="text-h6 mb-4">Bulk Upload Course Offerings</div>
                <v-file-input
                    v-model="offeringFile"
                    label="Offerings CSV"
                    accept=".csv"
                    variant="outlined"
                    density="compact"
                ></v-file-input>
                <div class="text-caption mb-4">
                    Columns: course_code, semester_id, course_name, category, credits (L-T-P), teacher_ids (semicolon sep), [exam_names]...
                </div>
                <v-btn color="primary" @click="uploadOfferings" :loading="uploadingOfferings" :disabled="!offeringFile">Upload Offerings</v-btn>
            </v-card>
        </v-window-item>
    </v-window>

     <v-snackbar v-model="snackbar.show" :color="snackbar.color">
        {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const tab = ref('users')
const semesters = ref([])

const userFile = ref(null)
const uploadingUsers = ref(false)

const offeringFile = ref(null)
const uploadingOfferings = ref(false)

const snackbar = ref({ show: false, text: '', color: 'success' })

const fetchSemesters = async () => {
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch(e) { console.error(e) }
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
        const errors = res.data.errors.length
        snackbar.value = { show: true, text: `Created ${count} users. Errors: ${errors}`, color: errors > 0 ? 'warning' : 'success' }
        userFile.value = null
    } catch (e) {
         snackbar.value = { show: true, text: 'Upload failed', color: 'error' }
    } finally {
        uploadingUsers.value = false
    }
}

const uploadOfferings = async () => {
    uploadingOfferings.value = true
    const formData = new FormData()
    formData.append('file', offeringFile.value)
    
    try {
        const res = await axios.post('http://localhost:8000/api/v1/courses/offerings/bulk-upload', formData, {
             headers: { 
                 Authorization: `Bearer ${auth.token}`,
                 'Content-Type': 'multipart/form-data'
             }
        })
         const count = res.data.offerings_created
        const errors = res.data.errors.length
        snackbar.value = { show: true, text: `Created ${count} offerings. Errors: ${errors}`, color: errors > 0 ? 'warning' : 'success' }
        offeringFile.value = null
    } catch (e) {
         snackbar.value = { show: true, text: 'Upload failed: ' + e.message, color: 'error' }
    } finally {
        uploadingOfferings.value = false
    }
}

onMounted(() => {
    fetchSemesters()
})
</script>
