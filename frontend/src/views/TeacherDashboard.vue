<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">Teacher Dashboard</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">Welcome, {{ auth.user?.name }}</div>
        </div>
    </div>
    
    <v-select
        v-model="selectedSemester"
        :items="semesters"
        item-title="name"
        item-value="id"
        label="Select Semester"
        variant="outlined"
        @update:model-value="fetchCourses"
        class="mb-6"
    >
        <template v-slot:item="{ props, item }">
            <v-list-item v-bind="props" :title="item.raw.name || `Semester ${item.raw.id}`"></v-list-item>
        </template>
        <template v-slot:selection="{ item }">
             {{ item.raw.name || `Semester ${item.raw.id}` }}
        </template>
    </v-select>

    <v-row v-if="selectedSemester">
        <v-col cols="12" md="4">
            <v-card border flat>
                <v-card-title>My Courses</v-card-title>
                <v-list selectable>
                    <v-list-item
                        v-for="course in courses"
                        :key="course.id"
                        :value="course"
                        @click="selectCourse(course)"
                        :active="selectedCourse?.id === course.id"
                        color="primary"
                    >
                        <v-list-item-title class="font-weight-bold">{{ course.course?.name || course.course_code }}</v-list-item-title>
                        <v-list-item-subtitle>{{ course.course_code }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item v-if="courses.length === 0">No courses found</v-list-item>
                </v-list>
            </v-card>
        </v-col>

        <v-col cols="12" md="8">
            <v-card border flat v-if="selectedCourse">
                <v-toolbar flat density="compact" class="border-b">
                    <v-toolbar-title class="text-body-1 font-weight-bold">
                        {{ selectedCourse.course?.name || selectedCourse.course_code }} Details
                    </v-toolbar-title>
                    <v-spacer></v-spacer>
                    <v-menu>
                        <template v-slot:activator="{ props }">
                            <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
                        </template>
                        <v-list>
                            <v-list-item @click="openUploadDialog('marks')">
                                <v-list-item-title>Bulk Upload Marks</v-list-item-title>
                            </v-list-item>
                            <v-list-item @click="openUploadDialog('grades')">
                                <v-list-item-title>Bulk Upload Grades</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </v-toolbar>

                <v-data-table
                    :headers="studentHeaders"
                    :items="courseDetails"
                    :loading="loadingDetails"
                    density="compact"
                >
                    <template v-slot:item.marks="{ item }">
                        <div v-for="mark in item.marks" :key="mark.exam_name" class="d-flex align-center text-caption mb-1">
                            <span>{{ mark.exam_name }}: {{ mark.marks_obtained }}/{{ mark.max_marks }}</span>
                            <v-btn 
                                icon="mdi-pencil" 
                                size="x-small" 
                                variant="text" 
                                density="compact" 
                                class="ml-1 text-medium-emphasis" 
                                @click="openEditMarkDialog(item, mark)"
                            ></v-btn>
                        </div>
                    </template>
                </v-data-table>
            </v-card>
            <div v-else class="text-center mt-10 text-medium-emphasis">
                Select a course to view details
            </div>
        </v-col>
    </v-row>

    <!-- Upload Dialog -->
    <v-dialog v-model="uploadDialog" max-width="500">
        <v-card>
            <v-card-title>Upload {{ uploadType === 'marks' ? 'Marks' : 'Grades' }}</v-card-title>
            <v-card-text>
                <v-file-input
                    v-model="uploadFile"
                    accept=".csv"
                    label="Select CSV File"
                    variant="outlined"
                ></v-file-input>
                <div class="text-caption mt-2">
                    <div v-if="uploadType==='marks'">Required Columns: student_id, [exam_name]...</div>
                    <div v-else>Required Columns: student_id, grade</div>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="uploadDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="handleUpload" :loading="uploading">Upload</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <v-dialog v-model="editMarkDialog" max-width="400">
        <v-card>
            <v-card-title>Edit Mark</v-card-title>
            <v-card-text>
                <div class="text-subtitle-1 mb-2">{{ editMarkData.student_name }} - {{ editMarkData.exam_name }}</div>
                <v-text-field
                    v-model.number="editMarkData.marks"
                    label="Marks Obtained"
                    type="number"
                    variant="outlined"
                    autofocus
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="editMarkDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveMark" :loading="savingMark">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

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
const semesters = ref([])
const selectedSemester = ref(null)
const courses = ref([])
const selectedCourse = ref(null)
const courseDetails = ref([])
const loadingDetails = ref(false)

const uploadDialog = ref(false)
const uploadType = ref('marks')
const uploadFile = ref(null)
const uploading = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })

const editMarkDialog = ref(false)
const editMarkData = ref({
    student_id: '',
    student_name: '',
    exam_name: '',
    marks: 0
})
const savingMark = ref(false)

const studentHeaders = [
    { title: 'Student ID', key: 'student_id' },
    { title: 'Name', key: 'student_name' },
    { title: 'Grade', key: 'grade' },
    { title: 'Marks', key: 'marks' },
]

const fetchSemesters = async () => {
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch(e) { console.error(e) }
}

const fetchCourses = async () => {
    if (!selectedSemester.value) return
    selectedCourse.value = null
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/courses/semester-courses?semester_id=${selectedSemester.value}`, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        courses.value = res.data
    } catch(e) { console.error(e) }
}

const selectCourse = async (course) => {
    selectedCourse.value = course
    loadingDetails.value = true
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/courses/semester-course-details?semester_id=${selectedSemester.value}&course_code=${course.course_code}`, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        courseDetails.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingDetails.value = false }
}

const openUploadDialog = (type) => {
    uploadType.value = type
    uploadFile.value = null
    uploadDialog.value = true
}

const handleUpload = async () => {
    if (!uploadFile.value) return
    uploading.value = true
    
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    
    // Additional params
    // Marks: course_code, semester_id
    // Grades: course_code, semester_id
    const params = `course_code=${selectedCourse.value.course_code}&semester_id=${selectedSemester.value}`
    
    const endpoint = uploadType.value === 'marks' 
        ? `http://localhost:8000/api/v1/examinations/bulk-upload-marks?${params}`
        : `http://localhost:8000/api/v1/registrations/bulk-upload-grades?${params}`
        
    try {
        await axios.post(endpoint, formData, {
            headers: { 
                Authorization: `Bearer ${auth.token}`,
                'Content-Type': 'multipart/form-data'
            }
        })
        snackbar.value = { show: true, text: 'Upload successful', color: 'success' }
        uploadDialog.value = false
        // Refresh details
        selectCourse(selectedCourse.value)
    } catch (e) {
        snackbar.value = { show: true, text: 'Upload failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        uploading.value = false
    }
}

const openEditMarkDialog = (item, mark) => {
    editMarkData.value = {
        student_id: item.student_id,
        student_name: item.student_name,
        exam_name: mark.exam_name,
        marks: mark.marks_obtained
    }
    editMarkDialog.value = true
}

const saveMark = async () => {
    savingMark.value = true
    try {
        await axios.put('http://localhost:8000/api/v1/examinations/marks', {
            course_code: selectedCourse.value.course_code,
            semester_id: selectedSemester.value,
            student_id: editMarkData.value.student_id,
            exam_name: editMarkData.value.exam_name,
            marks: editMarkData.value.marks
        }, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        snackbar.value = { show: true, text: 'Mark updated successfully', color: 'success' }
        editMarkDialog.value = false
        // Refresh details
        selectCourse(selectedCourse.value)
    } catch (e) {
        snackbar.value = { show: true, text: 'Update failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingMark.value = false
    }
}

onMounted(() => {
    fetchSemesters()
})
</script>
