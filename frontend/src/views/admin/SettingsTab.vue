<template>
    <v-card flat>
        <v-card-title>System Settings</v-card-title>
        <v-card-text>
            <div v-if="loading" class="d-flex justify-center my-4">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
            
            <v-form v-else @submit.prevent="saveSettings">
                <v-row>
                    <v-col cols="12" md="6">
                        <v-select
                            v-model="settings.current_semester_id"
                            :items="semesters"
                            item-title="name"
                            item-value="id"
                            label="Current Semester"
                            variant="outlined"
                            hint="Select the active semester for the system"
                            persistent-hint
                        ></v-select>
                    </v-col>
                </v-row>
                
                <v-divider class="my-4"></v-divider>
                
                <div class="text-subtitle-1 mb-2">Deadlines</div>
                <div class="text-caption text-medium-emphasis mb-4">
                    Teachers cannot edit grades after these dates.
                </div>
                
                <v-row>
                    <v-col cols="12" md="6">
                        <v-text-field
                            v-model="settings.grade_submission_deadline"
                            label="Grade Submission Deadline"
                            type="date"
                            variant="outlined"
                            :rules="[validateDeadline]"
                        ></v-text-field>
                    </v-col>
                    
                    <v-col cols="12" md="6">
                        <v-text-field
                            v-model="settings.compartment_submission_deadline"
                            label="Compartment Grade Submission Deadline"
                            type="date"
                            variant="outlined"
                            :rules="[validateDeadline]"
                        ></v-text-field>
                    </v-col>
                </v-row>
                
                <v-alert v-if="error" type="error" class="mt-4" closable>{{ error }}</v-alert>
                <v-alert v-if="success" type="success" class="mt-4" closable>Settings saved successfully</v-alert>
                
                <div class="d-flex justify-end mt-4">
                    <v-btn color="primary" type="submit" :loading="saving">Save Settings</v-btn>
                </div>
            </v-form>
        </v-card-text>
    </v-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const success = ref(false)

const semesters = ref([])
const settings = ref({
    current_semester_id: null,
    grade_submission_deadline: null,
    compartment_submission_deadline: null
})

const currentSemester = computed(() => {
    if (!settings.value.current_semester_id) return null
    return semesters.value.find(s => s.id === settings.value.current_semester_id)
})

const fetchSemesters = async () => {
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch(e) { console.error(e) }
}

const fetchSettings = async () => {
    try {
        const res = await axios.get('http://localhost:8000/api/v1/settings/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        // Map response to our state
        const data = res.data
        if (data.current_semester_id) settings.value.current_semester_id = parseInt(data.current_semester_id)
        if (data.grade_submission_deadline) settings.value.grade_submission_deadline = data.grade_submission_deadline
        if (data.compartment_submission_deadline) settings.value.compartment_submission_deadline = data.compartment_submission_deadline
        
    } catch(e) { 
        console.error(e) 
    }
}

const validateDeadline = (val) => {
    if (!val) return true
    if (!currentSemester.value) return true
    
    // Check if date is within semester or at least before end?
    // User requested: "choose dates before the end of current semester as the last dates"
    
    if (currentSemester.value.end_date) {
        const deadline = new Date(val)
        const end = new Date(currentSemester.value.end_date)
        if (deadline > end) {
            return `Date must be before semester end date (${currentSemester.value.end_date})`
        }
    }
    return true
}

const saveSettings = async () => {
    saving.value = true
    error.value = null
    success.value = false
    
    try {
        const payload = []
        if (settings.value.current_semester_id) {
            payload.push({ key: 'current_semester_id', value: String(settings.value.current_semester_id) })
        }
        if (settings.value.grade_submission_deadline) {
             payload.push({ key: 'grade_submission_deadline', value: settings.value.grade_submission_deadline })
        }
        if (settings.value.compartment_submission_deadline) {
             payload.push({ key: 'compartment_submission_deadline', value: settings.value.compartment_submission_deadline })
        }
        
        await axios.put('http://localhost:8000/api/v1/settings/', payload, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        success.value = true
    } catch (e) {
        error.value = 'Failed to save: ' + (e.response?.data?.detail || e.message)
    } finally {
        saving.value = false
    }
}

onMounted(async () => {
    loading.value = true
    await fetchSemesters()
    await fetchSettings()
    loading.value = false
})
</script>
