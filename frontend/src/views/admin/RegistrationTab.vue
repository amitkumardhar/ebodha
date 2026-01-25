<template>
    <v-card border flat class="pa-4 mb-4">
        <div class="text-h6 mb-4">Course Registration Management</div>

        <!-- Filters -->
        <v-row class="mb-4">
            <v-col cols="12" md="4">
                <v-select
                    v-model="selectedSemester"
                    :items="semesters"
                    item-title="name"
                    item-value="id"
                    label="Filter by Semester"
                    variant="outlined"
                    density="compact"
                    hide-details
                    @update:model-value="fetchCourses"
                >
                    <template v-slot:item="{ props, item }">
                        <v-list-item v-bind="props" :title="item.raw.name || `Semester ${item.raw.id}`"></v-list-item>
                    </template>
                    <template v-slot:selection="{ item }">
                        {{ item.raw.name || `Semester ${item.raw.id}` }}
                    </template>
                </v-select>
            </v-col>
            <v-col cols="12" md="4">
                <v-select
                    v-model="selectedCourse"
                    :items="courses"
                    :item-title="item => item.course?.name || item.course_code"
                    item-value="course_code"
                    label="Filter by Course"
                    variant="outlined"
                    density="compact"
                    hide-details
                    :disabled="!selectedSemester"
                    @update:model-value="fetchDetails"
                    return-object
                ></v-select>
            </v-col>
            <v-col cols="12" md="4" class="text-right">
                <v-menu v-if="selectedCourse">
                    <template v-slot:activator="{ props }">
                        <v-btn color="primary" prepend-icon="mdi-upload" v-bind="props">
                            Bulk Actions
                        </v-btn>
                    </template>
                    <v-list>
                        <v-list-item @click="openUploadDialog('marks')">
                            <v-list-item-title>Upload Marks</v-list-item-title>
                        </v-list-item>
                        <v-list-item @click="openUploadDialog('grades')">
                            <v-list-item-title>Upload Grades</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </v-col>
        </v-row>

        <!-- Search -->
        <v-text-field
            v-if="selectedCourse"
            v-model="searchStudents"
            prepend-inner-icon="mdi-magnify"
            label="Search Students"
            variant="outlined"
            density="compact"
            hide-details
            class="mb-4"
            clearable
        ></v-text-field>

        <!-- Data Table -->
        <v-data-table
            v-if="selectedCourse"
            :headers="studentHeaders"
            :items="courseDetails"
            :loading="loadingDetails"
            :search="searchStudents"
            density="compact"
        >
            <template v-slot:item.grade="{ item }">
                <div class="d-flex align-center">
                    <span class="mr-2">{{ item.grade || '-' }}</span>
                    <v-btn 
                        icon="mdi-pencil" 
                        size="x-small" 
                        variant="text" 
                        density="compact"
                        color="primary"
                        @click="openEditGradeDialog(item)"
                    ></v-btn>
                </div>
            </template>
            <template v-slot:item.marks="{ item }">
                <div v-for="mark in item.marks" :key="mark.exam_name" class="d-flex align-center text-caption mb-1">
                    <span style="min-width: 120px">{{ mark.exam_name }}: {{ mark.marks_obtained }}/{{ mark.max_marks }}</span>
                    <v-btn 
                        icon="mdi-pencil" 
                        size="x-small" 
                        variant="text" 
                        density="compact" 
                        class="ml-1 text-medium-emphasis" 
                        @click="openEditMarkDialog(item, mark)"
                    ></v-btn>
                </div>
                <div v-if="!item.marks?.length" class="text-caption text-medium-emphasis">No marks recorded</div>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteRegistration(item)"></v-btn>
            </template>
        </v-data-table>
        
        <div v-else-if="selectedSemester" class="text-center py-10 text-medium-emphasis">
            Please select a course to view students
        </div>
        <div v-else class="text-center py-10 text-medium-emphasis">
            Please select a semester and course
        </div>
    </v-card>

    <!-- Global Bulk Upload -->
    <v-card border flat class="pa-4">
        <div class="text-h6 mb-4">Bulk Upload Registrations</div>
        <v-file-input
            v-model="registrationFile"
            label="Registration CSV"
            accept=".csv"
            variant="outlined"
            density="compact"
            hide-details
            class="mb-4"
        ></v-file-input>
        <div class="text-caption mb-4">
            Required Columns: student_id, course_code, semester_id
        </div>
        <v-btn color="primary" @click="uploadRegistrations" :loading="uploadingRegistrations" :disabled="!registrationFile">
            Upload Registrations
        </v-btn>
    </v-card>

    <!-- Dialogs -->
    
    <!-- Bulk Upload Dialog -->
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
                <v-btn color="primary" @click="handleCourseUpload" :loading="uploading">Upload</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Edit Grade Dialog -->
    <v-dialog v-model="editGradeDialog" max-width="400">
        <v-card>
            <v-card-title>Edit Grade</v-card-title>
            <v-card-text>
                <div class="text-subtitle-1 mb-2">{{ editGradeData.student_name }}</div>
                <v-text-field
                    v-model="editGradeData.grade"
                    label="Grade"
                    variant="outlined"
                    autofocus
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="editGradeDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveGrade" :loading="savingGrade">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Edit Mark Dialog -->
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



    <!-- Bulk Upload Result Dialog -->
    <v-dialog v-model="resultDialog" max-width="600">
        <v-card>
            <v-card-title :class="['text-h6', resultStats.errors?.length ? 'text-warning' : 'text-success']">
                {{ resultStats.errors?.length ? 'Upload Completed with Errors' : 'Upload Successful' }}
            </v-card-title>
            <v-card-text>
                <div class="text-subtitle-1 mb-2">
                    {{ resultStats.message }}
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

const auth = useAuthStore()

// State
const semesters = ref([])
const selectedSemester = ref(null)
const courses = ref([])
const selectedCourse = ref(null)
const courseDetails = ref([])
const loadingDetails = ref(false)
const searchStudents = ref('')

// Upload state
const uploadDialog = ref(false)
const uploadType = ref('marks')
const uploadFile = ref(null)
const uploading = ref(false)

const registrationFile = ref(null)
const uploadingRegistrations = ref(false)
const resultDialog = ref(false)
const resultStats = ref({ message: '', errors: [] })

// Edit State
const editGradeDialog = ref(false)
const editGradeData = ref({ registration_id: null, student_name: '', grade: '' })
const savingGrade = ref(false)

const editMarkDialog = ref(false)
const editMarkData = ref({ student_id: '', student_name: '', exam_name: '', marks: 0 })
const savingMark = ref(false)

const snackbar = ref({ show: false, text: '', color: 'success' })

const studentHeaders = [
    { title: 'Student ID', key: 'student_id' },
    { title: 'Name', key: 'student_name' },
    { title: 'Grade', key: 'grade' },
    { title: 'Marks', key: 'marks', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false },
]

// Data Fetching
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
    courseDetails.value = []
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/courses/semester-courses?semester_id=${selectedSemester.value}`, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        courses.value = res.data
    } catch(e) { console.error(e) }
}

const fetchDetails = async () => {
    if (!selectedCourse.value || !selectedSemester.value) return
    loadingDetails.value = true
    try {
        const res = await axios.get(`http://localhost:8000/api/v1/courses/semester-course-details?semester_id=${selectedSemester.value}&course_code=${selectedCourse.value.course_code}`, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        courseDetails.value = res.data
    } catch(e) { console.error(e) }
    finally { loadingDetails.value = false }
}

// Upload Handlers
const openUploadDialog = (type) => {
    uploadType.value = type
    uploadFile.value = null
    uploadDialog.value = true
}

const handleCourseUpload = async () => {
    if (!uploadFile.value) return
    uploading.value = true
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    
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
        
        // Handle response depending on upload type
        const errors = res.data.errors
        const count = uploadType.value === 'marks' ? res.data.marks_updated : res.data.grades_updated
        const msg = uploadType.value === 'marks' 
            ? `Successfully updated ${count} marks.` 
            : `Successfully updated ${count} grades.`
            
        resultStats.value = { message: msg, errors: errors }
        resultDialog.value = true

        uploadDialog.value = false
        fetchDetails()
    } catch (e) {
        snackbar.value = { show: true, text: 'Upload failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        uploading.value = false
    }
}

const uploadRegistrations = async () => {
    if (!registrationFile.value) return
    uploadingRegistrations.value = true
    const formData = new FormData()
    formData.append('file', registrationFile.value)

    try {
        const res = await axios.post('http://localhost:8000/api/v1/registrations/bulk-upload', formData, {
            headers: {
                Authorization: `Bearer ${auth.token}`,
                'Content-Type': 'multipart/form-data'
            }
        })
        const count = res.data.registrations_created
        const errors = res.data.errors
        
        resultStats.value = { message: `Successfully created ${count} registrations.`, errors: errors }
        resultDialog.value = true
        
        registrationFile.value = null
        if (selectedCourse.value) fetchDetails()
    } catch (e) {
        snackbar.value = { show: true, text: 'Upload failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        uploadingRegistrations.value = false
    }
}

// Edit Handlers
const openEditGradeDialog = (item) => {
    editGradeData.value = {
        registration_id: item.registration_id,
        student_name: item.student_name,
        grade: item.grade
    }
    editGradeDialog.value = true
}

const saveGrade = async () => {
    savingGrade.value = true
    try {
        await axios.put(`http://localhost:8000/api/v1/registrations/${editGradeData.value.registration_id}/grade`, {
            grade: editGradeData.value.grade
        }, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Grade updated', color: 'success' }
        editGradeDialog.value = false
        fetchDetails()
    } catch (e) {
        snackbar.value = { show: true, text: 'Update failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingGrade.value = false
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
        snackbar.value = { show: true, text: 'Mark updated', color: 'success' }
        editMarkDialog.value = false
        fetchDetails()
    } catch (e) {
        snackbar.value = { show: true, text: 'Update failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingMark.value = false
    }
}

const deleteRegistration = async (item) => {
    if (!confirm(`Are you sure you want to delete registration for ${item.student_name}? This will also delete all associated marks.`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/registrations/${item.registration_id}`, {
             headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Registration deleted', color: 'success' }
        fetchDetails()
    } catch (e) {
        snackbar.value = { show: true, text: 'Deletion failed: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

onMounted(() => {
    fetchSemesters()
})
</script>
