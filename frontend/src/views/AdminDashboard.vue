<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-6">
        <div>
            <div class="text-h4 font-weight-light">Admin Dashboard</div>
            <div class="text-subtitle-1 text-medium-emphasis mt-1">Welcome, {{ auth.user?.name }}</div>
        </div>
    </div>
    
    <v-tabs v-model="tab" color="primary">
        <v-tab value="users">Users</v-tab>
        <v-tab value="disciplines">Disciplines</v-tab>
        <v-tab value="semesters">Semesters</v-tab>
        <v-tab value="courses">Courses</v-tab>
        <v-tab value="offerings">Course Offerings</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="mt-4">
        <v-window-item value="users">
            <UsersTab />
        </v-window-item>

        <v-window-item value="disciplines">
            <DisciplinesTab />
        </v-window-item>

        <v-window-item value="semesters">
            <SemestersTab />
        </v-window-item>

        <v-window-item value="courses">
            <CoursesTab />
        </v-window-item>

        <v-window-item value="offerings">
            <OfferingsTab />
        </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import UsersTab from './admin/UsersTab.vue'
import DisciplinesTab from './admin/DisciplinesTab.vue'
import SemestersTab from './admin/SemestersTab.vue'
import CoursesTab from './admin/CoursesTab.vue'
import OfferingsTab from './admin/OfferingsTab.vue'

const auth = useAuthStore()
const tab = ref('users')
</script>
