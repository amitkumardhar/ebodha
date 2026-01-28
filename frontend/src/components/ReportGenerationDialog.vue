<template>
    <v-dialog v-model="dialog" max-width="500" persistent>
        <v-card>
            <v-card-title>{{ title }}</v-card-title>
            <v-card-text>
                <div v-if="loading || taskId">
                    <div class="mb-2">Processing... {{ progress }}%</div>
                    <v-progress-linear v-model="progress" color="primary" height="20" striped></v-progress-linear>
                </div>
                
                <div v-else>
                    <div v-if="mode === 'grade_card'">
                        <v-select
                            v-model="selectedSemester"
                            :items="semesters"
                            item-title="name"
                            item-value="id"
                            label="Select Semester"
                            variant="outlined"
                            :rules="[v => !!v || 'Required']"
                        ></v-select>
                    </div>
                    <div class="text-body-2 mt-2">
                        Selected Students: {{ selectedStudents.length }}
                    </div>
                </div>
                
                <div v-if="error" class="text-error mt-2">{{ error }}</div>
                
                <div v-if="downloadUrl" class="mt-4 text-center">
                    <v-btn color="success" @click="downloadFile" prepend-icon="mdi-download" :loading="downloading">
                        Download ZIP
                    </v-btn>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="close" :disabled="loading && !downloadUrl">Close</v-btn>
                <v-btn 
                    v-if="!taskId && !downloadUrl" 
                    color="primary" 
                    @click="startGeneration" 
                    :disabled="mode === 'grade_card' && !selectedSemester"
                >
                    Generate
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
    modelValue: Boolean,
    mode: { type: String, default: 'grade_card' }, // 'grade_card' or 'transcript'
    selectedStudents: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const auth = useAuthStore()
const dialog = ref(props.modelValue)
const semesters = ref([])
const selectedSemester = ref(null)

const loading = ref(false)
const progress = ref(0)
const taskId = ref(null)
const downloadUrl = ref(null)
const error = ref(null)
const title = ref('')

watch(() => props.modelValue, (val) => {
    dialog.value = val
    if (val) {
        reset()
        title.value = props.mode === 'grade_card' ? 'Download Semester Grade Card' : 'Download Transcript'
    }
})

watch(dialog, (val) => {
    emit('update:modelValue', val)
})

const reset = () => {
    loading.value = false
    progress.value = 0
    taskId.value = null
    downloadUrl.value = null
    error.value = null
    selectedSemester.value = null
}

const fetchSemesters = async () => {
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch(e) { console.error(e) }
}

const startGeneration = async () => {
    loading.value = true
    error.value = null
    try {
        const endpoint = props.mode === 'grade_card' 
            ? 'http://localhost:8000/api/v1/reports/generate-grade-cards'
            : 'http://localhost:8000/api/v1/reports/generate-transcripts'
            
        const payload = {
            student_ids: props.selectedStudents.map(s => s.id)
        }
        
        if (props.mode === 'grade_card') {
            payload.semester_id = selectedSemester.value
        }
        
        const res = await axios.post(endpoint, payload, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        taskId.value = res.data.task_id
        pollStatus()
        
    } catch (e) {
        error.value = 'Failed to start: ' + (e.response?.data?.detail || e.message)
        loading.value = false
    }
}

const pollStatus = async () => {
    if (!taskId.value) return
    
    const interval = setInterval(async () => {
        try {
            const res = await axios.get(`http://localhost:8000/api/v1/reports/tasks/${taskId.value}`, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            
            progress.value = res.data.progress
            if (res.data.status === 'completed') {
                clearInterval(interval)
                loading.value = false
                downloadUrl.value = `http://localhost:8000/api/v1/reports/tasks/${taskId.value}/download`
            } else if (res.data.status === 'failed') {
                clearInterval(interval)
                loading.value = false
                error.value = 'Generation failed: ' + res.data.error
                taskId.value = null
            }
        } catch (e) {
            clearInterval(interval)
            loading.value = false
            error.value = 'Polling failed'
        }
    }, 1000)
}

const downloading = ref(false)

const downloadFile = async () => {
    if (!downloadUrl.value) return
    downloading.value = true
    try {
        const res = await axios.get(downloadUrl.value, {
            headers: { Authorization: `Bearer ${auth.token}` },
            responseType: 'blob'
        })
        
        // Create blob link to download
        const url = window.URL.createObjectURL(new Blob([res.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `report_${taskId.value}.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
    } catch (e) {
        error.value = 'Download failed'
        console.error(e)
    } finally {
        downloading.value = false
    }
}

const close = () => {
    dialog.value = false
}

onMounted(() => {
    fetchSemesters()
})
</script>
