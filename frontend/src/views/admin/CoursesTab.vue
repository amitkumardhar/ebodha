<template>
    <v-card border flat class="pa-4">
        <div class="d-flex justify-space-between align-center mb-4">
            <div class="text-h6">Courses</div>
            <div>
                <v-btn color="primary" variant="text" prepend-icon="mdi-download" class="mr-2" @click="downloadCourses">Download CSV</v-btn>
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openCourseDialog()">Add Course</v-btn>
            </div>
        </div>

        <v-text-field
            v-model="searchCourses"
            prepend-inner-icon="mdi-magnify"
            label="Search Courses"
            variant="outlined"
            density="compact"
            hide-details
            class="mb-4"
            clearable
        ></v-text-field>
        
        <v-data-table
            :headers="courseHeaders"
            :items="courses"
            :loading="loadingCourses"
            :search="searchCourses"
            density="compact"
        >
            <template v-slot:item.credits="{ item }">
                {{ item.lecture_credits }}-{{ item.tutorial_credits }}-{{ item.practice_credits }}
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="small" variant="text" @click="openCourseDialog(item)"></v-btn>
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteCourse(item)"></v-btn>
            </template>
        </v-data-table>
    </v-card>

    <!-- Course Dialog -->
    <v-dialog v-model="courseDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingCourse ? 'Edit Course' : 'Add Course' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="courseData.code"
                    label="Course Code"
                    variant="outlined"
                    :disabled="editingCourse"
                ></v-text-field>
                <v-text-field
                    v-model="courseData.name"
                    label="Course Name"
                    variant="outlined"
                ></v-text-field>
                <v-select
                    v-model="courseData.category"
                    :items="['Core Course', 'Elective', 'MTech Thesis', 'MTech Project']"
                    label="Category"
                    variant="outlined"
                ></v-select>
                <v-row>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.lecture_credits"
                            label="Lecture"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.tutorial_credits"
                            label="Tutorial"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field
                            v-model.number="courseData.practice_credits"
                            label="Practice"
                            type="number"
                            variant="outlined"
                        ></v-text-field>
                    </v-col>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="courseDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveCourse" :loading="savingCourse">Save</v-btn>
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

const auth = useAuthStore()

// Courses
const courses = ref([])
const loadingCourses = ref(false)
const courseDialog = ref(false)
const courseData = ref({ code: '', name: '', category: 'Core Course', lecture_credits: 0, tutorial_credits: 0, practice_credits: 0 })
const editingCourse = ref(false)
const savingCourse = ref(false)
const searchCourses = ref('')
const snackbar = ref({ show: false, text: '', color: 'success' })

const courseHeaders = [
    { title: 'Code', key: 'code' },
    { title: 'Name', key: 'name' },
    { title: 'Category', key: 'category' },
    { title: 'Credits (L-T-P)', key: 'credits', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchCourses = async () => {
    loadingCourses.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/courses/', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        courses.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loadingCourses.value = false
    }
}

const openCourseDialog = (item = null) => {
    if (item) {
        courseData.value = { ...item }
        editingCourse.value = true
    } else {
        courseData.value = { code: '', name: '', category: 'Core Course', lecture_credits: 0, tutorial_credits: 0, practice_credits: 0 }
        editingCourse.value = false
    }
    courseDialog.value = true
}

const saveCourse = async () => {
    savingCourse.value = true
    try {
        if (editingCourse.value) {
            await axios.put(`http://localhost:8000/api/v1/courses/${courseData.value.code}`, courseData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/courses/', courseData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'Course saved successfully', color: 'success' }
        courseDialog.value = false
        fetchCourses()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save course: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingCourse.value = false
    }
}

const downloadCourses = () => {
    downloadDataAsCSV(courses.value, courseHeaders, 'Courses', auth.user?.name || 'User')
}

const deleteCourse = async (item) => {
    if (!confirm(`Are you sure you want to delete course ${item.code}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/courses/${item.code}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Course deleted', color: 'success' }
        fetchCourses()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to delete: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

onMounted(() => {
    fetchCourses()
})
</script>
