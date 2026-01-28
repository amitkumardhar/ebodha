<template>
    <v-card flat>
        <v-card-title class="d-flex align-center">
            Reports
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search by Name, ID, or Email"
                single-line
                hide-details
                density="compact"
                style="max-width: 300px"
                @update:model-value="fetchStudents"
                clearable
            ></v-text-field>
        </v-card-title>
        
        <v-card-text>
            <div class="d-flex mb-4">
                <v-btn
                    color="primary"
                    prepend-icon="mdi-card-account-details-outline"
                    class="mr-2"
                    :disabled="selected.length === 0"
                    @click="openDialog('grade_card')"
                >
                    Download Semester Grade Card ({{ selected.length }})
                </v-btn>
                <v-btn
                    color="secondary"
                    prepend-icon="mdi-file-document-outline"
                    :disabled="selected.length === 0"
                    @click="openDialog('transcript')"
                >
                    Download Transcript ({{ selected.length }})
                </v-btn>
            </div>
            
            <v-data-table-server
                v-model:items-per-page="itemsPerPage"
                :headers="headers"
                :items="serverItems"
                :items-length="totalItems"
                :loading="loading"
                :search="search"
                item-value="id"
                show-select
                v-model="selected"
                return-object
                @update:options="fetchStudents"
                class="elevation-1"
                density="compact"
            >
                <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                </template>
                <template v-slot:item.roles="{ item }">
                    <v-chip size="x-small" v-for="role in item.roles" :key="role.id" class="mr-1">
                        {{ role.role }}
                    </v-chip>
                </template>
            </v-data-table-server>
        </v-card-text>
        
        <ReportGenerationDialog 
            v-model="showDialog"
            :mode="dialogMode"
            :selected-students="selected"
        />
    </v-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'
import ReportGenerationDialog from '../../components/ReportGenerationDialog.vue'

const auth = useAuthStore()

const itemsPerPage = ref(10)
const headers = [
    { title: 'Student ID', key: 'id', sortable: true },
    { title: 'Name', key: 'name', sortable: true },
    { title: 'Roles', key: 'roles', sortable: false },
    { title: 'Discipline', key: 'discipline_code', sortable: true },
    { title: 'Profile Created', key: 'created_at', sortable: true },
]
const serverItems = ref([])
const totalItems = ref(0)
const loading = ref(true)
const search = ref('')
const selected = ref([])

const showDialog = ref(false)
const dialogMode = ref('grade_card')

const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const fetchStudents = async ({ page, itemsPerPage, sortBy } = { page: 1, itemsPerPage: 10, sortBy: [] }) => {
    loading.value = true
    try {
        let sortField = 'id'
        let sortDesc = false
        
        if (sortBy && sortBy.length) {
            sortField = sortBy[0].key
            sortDesc = sortBy[0].order === 'desc'
        }
        
        const res = await axios.get('http://localhost:8000/api/v1/reports/students', {
            params: {
                skip: (page - 1) * itemsPerPage,
                limit: itemsPerPage,
                search: search.value,
                sort_by: sortField,
                sort_desc: sortDesc
            },
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        
        serverItems.value = res.data.items
        totalItems.value = res.data.total
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const openDialog = (mode) => {
    dialogMode.value = mode
    showDialog.value = true
}
</script>
