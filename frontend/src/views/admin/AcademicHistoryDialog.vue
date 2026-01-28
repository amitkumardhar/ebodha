<template>
    <v-dialog v-model="dialog" max-width="900" scrollable>
        <v-card>
            <v-toolbar color="primary" density="compact">
                <v-toolbar-title>Academic History</v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn icon @click="dialog = false">
                    <v-icon>mdi-close</v-icon>
                </v-btn>
            </v-toolbar>

            <v-card-text v-if="loading" class="text-center pa-4">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-card-text>

            <v-card-text v-else-if="error" class="text-center pa-4 text-error">
                {{ error }}
            </v-card-text>

            <v-card-text v-else class="pa-4">
                <div class="d-flex justify-space-between align-start mb-4">
                    <div>
                        <div class="text-h5">{{ history.student_name }}</div>
                        <div class="text-subtitle-1 text-medium-emphasis">{{ history.student_id }}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-subtitle-2 text-medium-emphasis">Discipline</div>
                        <div class="text-body-1">{{ history.discipline_name || history.discipline_code || 'N/A' }}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-subtitle-2 text-medium-emphasis">CGPA</div>
                        <div class="text-h4 font-weight-bold text-primary">{{ history.cgpa }}</div>
                    </div>
                </div>

                <v-divider class="mb-4"></v-divider>

                <div v-if="!history.semesters || history.semesters.length === 0" class="text-center text-medium-emphasis my-4">
                    No academic history found.
                </div>

                <div v-for="semester in history.semesters" :key="semester.semester_id" class="mb-6">
                    <div class="d-flex justify-space-between align-center mb-2 bg-grey-lighten-4 pa-2 rounded">
                        <div class="text-h6">{{ semester.semester_name }}</div>
                        <div class="d-flex align-center">
                            <span class="text-body-2 mr-2">SGPA:</span>
                            <span class="font-weight-bold">{{ semester.sgpa !== null ? semester.sgpa : 'N/A' }}</span>
                        </div>
                    </div>

                    <v-table density="compact" class="border rounded">
                        <thead>
                            <tr>
                                <th class="text-left">Code</th>
                                <th class="text-left">Course Name</th>
                                <th class="text-center">Credits</th>
                                <th class="text-center">Original Grade</th>
                                <th class="text-center">Compartment</th>
                                <th class="text-center">Final Grade</th>
                                <th class="text-center">Points</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="course in semester.courses" :key="course.code">
                                <td>{{ course.code }}</td>
                                <td>{{ course.name }}</td>
                                <td class="text-center">{{ course.credits }}</td>
                                <td class="text-center">{{ course.original_grade || '-' }}</td>
                                <td class="text-center">{{ course.compartment_grade || '-' }}</td>
                                <td class="text-center font-weight-bold">{{ course.course_grade || '-' }}</td>
                                <td class="text-center">{{ course.grade_point !== null ? course.grade_point : '-' }}</td>
                            </tr>
                        </tbody>
                    </v-table>
                </div>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
    modelValue: Boolean,
    userId: String
})

const emit = defineEmits(['update:modelValue'])

const auth = useAuthStore()
const dialog = ref(props.modelValue)
const loading = ref(false)
const error = ref(null)
const history = ref({})

watch(() => props.modelValue, (val) => {
    dialog.value = val
    if (val && props.userId) {
        fetchHistory()
    }
})

watch(dialog, (val) => {
    emit('update:modelValue', val)
})

const fetchHistory = async () => {
    loading.value = true
    error.value = null
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/users/${props.userId}/academic-history`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        history.value = res.data
    } catch (e) {
        console.error(e)
        error.value = 'Failed to load academic history: ' + (e.response?.data?.detail || e.message)
    } finally {
        loading.value = false
    }
}
</script>
