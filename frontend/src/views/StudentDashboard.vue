<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">My Academic Record</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">
                Welcome, {{ auth.user?.name }} 
                <span v-if="auth.user?.discipline_code" class="text-caption font-weight-medium ml-2 text-uppercase border px-2 rounded">
                    {{ disciplineName || auth.user.discipline_code }}
                </span>
            </div>
        </div>
        <v-card class="px-4 py-2 bg-primary text-white" elevation="2">
            <div class="text-caption text-uppercase">CGPA: </div>
            <div class="text-h4 font-weight-bold">{{ cgpa }}</div>
        </v-card>
        <v-btn color="primary" prepend-icon="mdi-download" @click="downloadReport" :disabled="!report.length">
            Download Record
        </v-btn>
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
            <div class="d-flex justify-space-between w-100 align-center pr-4">
                <span>{{ getSemesterName(semester.id) }}</span>
                <span v-if="semester.sgpa" class="text-subtitle-1 font-weight-bold text-primary bg-blue-lighten-5 px-3 py-1 rounded">
                    SGPA: {{ semester.sgpa }}
                </span>
            </div>
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
                                <span v-if="getEffectiveGrade(item).grade" class="px-2 py-1 border rounded">
                                    Grade: {{ getEffectiveGrade(item).grade }} ({{ getEffectiveGrade(item).points }})
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
                        <div class="mt-2 text-caption d-flex justify-space-between">
                            <span>Credits: {{ item.course.credits }}</span>
                            <span>
                                <span v-if="item.grade" class="mr-2">Original: {{ item.grade }} ({{ item.grade_point }})</span>
                                <span v-if="item.compartment_grade">Compartment: {{ item.compartment_grade }} ({{ item.compartment_grade_point }})</span>
                            </span>
                        </div>
                    </v-expansion-panel-text>
                </v-expansion-panel>
            </v-expansion-panels>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { downloadDataAsCSV } from '../utils/csv'

const auth = useAuthStore()
const loading = ref(true)
const report = ref([])
const disciplineName = ref('')
const semesters = ref([])

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

const fetchDiscipline = async () => {
    if (!auth.user?.discipline_code) return
    try {
        const response = await axios.get(`http://localhost:8000/api/v1/disciplines/${auth.user.discipline_code}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        disciplineName.value = response.data.name
    } catch (e) {
        console.error('Failed to fetch discipline name', e)
    }
}

const fetchSemesters = async () => {
    try {
        const response = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = response.data
    } catch (e) {
        console.error('Failed to fetch semesters', e)
    }
}

const getSemesterName = (id) => {
    const sem = semesters.value.find(s => s.id === id)
    // Assuming semester object has a name field, or we construct it from type/year/dates
    // Let's check what the semester object looks like. 
    // Usually it has id, type, year, start_date, end_date.
    // If it doesn't have a name, we might need to construct it.
    // But the user said "All semester name with semester id can be obtained".
    // So I assume there is a 'name' field or similar.
    // If not, I'll fallback to ID.
    return sem ? (sem.name || `Semester ${sem.id}`) : `Semester ${id}`
}

const calculateCredit = (course) => {
    return course.lecture_credits + course.tutorial_credits + (course.practice_credits / 2)
}

const getEffectiveGrade = (item) => {
    let grade = item.grade
    let points = item.grade_point
    
    if (item.compartment_grade && item.compartment_grade_point !== null) {
        if (points === null || item.compartment_grade_point > points) {
            grade = item.compartment_grade
            points = item.compartment_grade_point
        }
    }
    return { grade, points }
}

const calculateSGPA = (courses) => {
    let totalPoints = 0
    let totalCredits = 0
    
    courses.forEach(item => {
        const { points } = getEffectiveGrade(item)
        if (points !== null && points !== undefined) {
             const credit = calculateCredit(item.course)
             totalPoints += (points * credit)
             totalCredits += credit
        }
    })
    
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : null
}

const cgpa = computed(() => {
    if (!report.value.length) return null
    
    let totalPoints = 0
    let totalCredits = 0
    
    report.value.forEach(item => {
        const { points } = getEffectiveGrade(item)
        if (points !== null && points !== undefined) {
             const credit = calculateCredit(item.course)
             totalPoints += (points * credit)
             totalCredits += credit
        }
    })
    
    return totalCredits > 0 ? (totalPoints / totalCredits).toFixed(2) : null
})

const groupedData = computed(() => {
    const groups = {}
    report.value.forEach(item => {
        const semId = item.course.semester_id
        if (!groups[semId]) {
            groups[semId] = {
                id: semId,
                courses: [],
                sgpa: null
            }
        }
        groups[semId].courses.push(item)
    })
    
    // Calculate SGPA for each semester
    Object.values(groups).forEach(group => {
        group.sgpa = calculateSGPA(group.courses)
    })

    // Convert to array and sort by semester id descending
    return Object.values(groups).sort((a, b) => b.id - a.id)
})

onMounted(() => {
    fetchReport()
    fetchDiscipline()
    fetchSemesters()
})

// Watch for user changes (e.g. on refresh/late load)
watch(() => auth.user, () => {
    fetchDiscipline()
})

const downloadReport = () => {
    // Flatten the report for CSV
    const flatData = []
    report.value.forEach(item => {
        // If no marks, add one row for course
        if (!item.marks || item.marks.length === 0) {
            flatData.push({
                semester: getSemesterName(item.course.semester_id),
                course_code: item.course.code,
                course_name: item.course.name,
                credits: item.course.credits,
                grade: item.grade || 'N/A',
                grade_point: item.grade_point || '',
                exam_name: '',
                marks_obtained: '',
                max_marks: ''
            })
        } else {
            item.marks.forEach(mark => {
                flatData.push({
                    semester: getSemesterName(item.course.semester_id),
                    course_code: item.course.code,
                    course_name: item.course.name,
                    credits: item.course.credits,
                    grade: item.grade || 'N/A',
                    grade_point: item.grade_point || '',
                    exam_name: mark.exam_name,
                    marks_obtained: mark.marks_obtained,
                    max_marks: mark.max_marks
                })
            })
        }
    })
    
    const headers = [
        { title: 'Semester', key: 'semester' },
        { title: 'Course Code', key: 'course_code' },
        { title: 'Course Name', key: 'course_name' },
        { title: 'Credits', key: 'credits' },
        { title: 'Grade', key: 'grade' },
        { title: 'Grade Point', key: 'grade_point' },
        { title: 'Exam', key: 'exam_name' },
        { title: 'Obtained', key: 'marks_obtained' },
        { title: 'Max Marks', key: 'max_marks' }
    ]
    
    downloadDataAsCSV(flatData, headers, 'Academic_Record', auth.user?.name || 'Student')
}
</script>
