<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">My Academic Record</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">
                Welcome, {{ auth.user?.name }} 
                <span v-if="auth.user?.discipline_code" class="text-caption font-weight-medium ml-2 text-uppercase border px-2 rounded">
                    {{ auth.user.discipline_code }}
                </span>
            </div>
        </div>
    </div>
    
    <v-progress-linear v-if="loading" indeterminate color="primary"></v-progress-linear>

    <div v-else-if="groupedData.length === 0" class="text-center mt-10 text-medium-emphasis">
        No academic records found.
    </div>

    <v-expansion-panels v-else variant="accordion" multiple>
      <v-expansion-panel
        v-for="semester in groupedData"
        :key="semester.id"
      >
        <v-expansion-panel-title class="text-h6">
            Semester {{ semester.id }}
            <template v-slot:actions="{ expanded }">
                <v-icon :icon="expanded ? 'mdi-minus' : 'mdi-plus'"></v-icon>
            </template>
        </v-expansion-panel-title>
        
        <v-expansion-panel-text>
            <v-expansion-panels variant="popout" class="mt-2">
                <v-expansion-panel 
                    v-for="item in semester.courses" 
                    :key="item.course.code"
                >
                    <v-expansion-panel-title>
                        <v-row no-gutters align="center">
                            <v-col cols="8" class="font-weight-bold">
                                {{ item.course.code }}: {{ item.course.name }}
                            </v-col>
                            <v-col cols="4" class="text-right text-caption">
                                <span v-if="item.grade" class="px-2 py-1 border rounded">
                                    Grade: {{ item.grade }} ({{ item.grade_point }})
                                </span>
                                <span v-else class="text-disabled">Grade Pending</span>
                            </v-col>
                        </v-row>
                    </v-expansion-panel-title>
                    
                    <v-expansion-panel-text>
                        <v-table density="compact">
                            <thead>
                                <tr>
                                    <th class="text-left">Examination</th>
                                    <th class="text-right">Max Marks</th>
                                    <th class="text-right">Obtained</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="mark in item.marks" :key="mark.exam_name">
                                    <td>{{ mark.exam_name }}</td>
                                    <td class="text-right">{{ mark.max_marks }}</td>
                                    <td class="text-right">{{ mark.marks_obtained }}</td>
                                </tr>
                                <tr v-if="item.marks.length === 0">
                                    <td colspan="3" class="text-center text-disabled">No marks available</td>
                                </tr>
                            </tbody>
                        </v-table>
                        <div class="mt-2 text-caption">Credits: {{ item.course.credits }}</div>
                    </v-expansion-panel-text>
                </v-expansion-panel>
            </v-expansion-panels>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const loading = ref(true)
const report = ref([])

const fetchReport = async () => {
    loading.value = true
    try {
        const response = await axios.get('http://localhost:8000/api/v1/registrations/my-report', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        report.value = response.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const groupedData = computed(() => {
    const groups = {}
    report.value.forEach(item => {
        const semId = item.course.semester_id
        if (!groups[semId]) {
            groups[semId] = {
                id: semId,
                courses: []
            }
        }
        groups[semId].courses.push(item)
    })
    // Convert to array and sort by semester id descending
    return Object.values(groups).sort((a, b) => b.id - a.id)
})

onMounted(() => {
    fetchReport()
})
</script>
