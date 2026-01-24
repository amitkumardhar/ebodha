<template>
    <v-card border flat>
        <v-card-title>My Courses</v-card-title>
        <v-list selectable>
            <v-list-item
                v-for="course in courses"
                :key="course.id"
                :value="course"
                @click="$emit('select', course)"
                :active="selectedCourseId === course.id"
                color="primary"
            >
                <v-list-item-title class="font-weight-bold">{{ course.course?.name || course.course_code }}</v-list-item-title>
                <v-list-item-subtitle>{{ course.course_code }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="courses.length === 0">No courses found</v-list-item>
        </v-list>
    </v-card>
</template>

<script setup>
defineProps({
    courses: Array,
    selectedCourseId: [Number, String]
})
defineEmits(['select'])
</script>
