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
            <CourseList 
                :courses="courses" 
                :selectedCourseId="selectedCourse?.id"
                @select="selectedCourse = $event"
            />
        </v-col>

        <v-col cols="12" md="8">
            <CourseDetails 
                v-if="selectedCourse" 
                :course="selectedCourse" 
                :semesterId="selectedSemester" 
            />
            <div v-else class="text-center mt-10 text-medium-emphasis">
                Select a course to view details
            </div>
        </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import CourseList from './teacher/CourseList.vue'
import CourseDetails from './teacher/CourseDetails.vue'

const auth = useAuthStore()
const semesters = ref([])
const selectedSemester = ref(null)
const courses = ref([])
const selectedCourse = ref(null)

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

onMounted(() => {
    fetchSemesters()
})
</script>
