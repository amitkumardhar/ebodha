<template>
    <v-card border flat class="pa-4">
        <div class="d-flex justify-space-between align-center mb-4">
            <div class="text-h6">Disciplines</div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openDisciplineDialog()">Add Discipline</v-btn>
        </div>

        <v-data-table
            :headers="disciplineHeaders"
            :items="disciplines"
            :loading="loadingDisciplines"
            density="compact"
        >
            <template v-slot:item.is_active="{ item }">
                <v-chip size="x-small" :color="item.is_active ? 'success' : 'error'">
                    {{ item.is_active ? 'Active' : 'Inactive' }}
                </v-chip>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="small" variant="text" @click="openDisciplineDialog(item)"></v-btn>
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="confirmDeleteDiscipline(item)"></v-btn>
            </template>
        </v-data-table>
    </v-card>

    <!-- Discipline Dialog -->
    <v-dialog v-model="disciplineDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingDiscipline ? 'Edit Discipline' : 'Add Discipline' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="disciplineData.code"
                    label="Code"
                    variant="outlined"
                    :disabled="editingDiscipline"
                ></v-text-field>
                <v-text-field
                    v-model="disciplineData.name"
                    label="Name"
                    variant="outlined"
                ></v-text-field>
                <v-switch
                    v-model="disciplineData.is_active"
                    label="Active"
                    color="primary"
                ></v-switch>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="disciplineDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveDiscipline" :loading="savingDiscipline">Save</v-btn>
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

// Disciplines
const disciplines = ref([])
const loadingDisciplines = ref(false)
const disciplineDialog = ref(false)
const disciplineData = ref({ code: '', name: '', is_active: true })
const editingDiscipline = ref(false)
const savingDiscipline = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })

const disciplineHeaders = [
    { title: 'Code', key: 'code' },
    { title: 'Name', key: 'name' },
    { title: 'Status', key: 'is_active' },
    { title: 'Actions', key: 'actions', sortable: false }
]

const fetchDisciplines = async () => {
    loadingDisciplines.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/disciplines/', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        disciplines.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loadingDisciplines.value = false
    }
}

const openDisciplineDialog = (item = null) => {
    if (item) {
        disciplineData.value = { ...item }
        editingDiscipline.value = true
    } else {
        disciplineData.value = { code: '', name: '', is_active: true }
        editingDiscipline.value = false
    }
    disciplineDialog.value = true
}

const saveDiscipline = async () => {
    savingDiscipline.value = true
    try {
        if (editingDiscipline.value) {
            await axios.put(`http://localhost:8000/api/v1/disciplines/${disciplineData.value.code}`, disciplineData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            await axios.post('http://localhost:8000/api/v1/disciplines/', disciplineData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        }
        snackbar.value = { show: true, text: 'Discipline saved successfully', color: 'success' }
        disciplineDialog.value = false
        fetchDisciplines()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save discipline: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingDiscipline.value = false
    }
}

const confirmDeleteDiscipline = async (item) => {
    if (!confirm(`Are you sure you want to deactivate discipline ${item.name}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/disciplines/${item.code}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Discipline deactivated', color: 'success' }
        fetchDisciplines()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to deactivate: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

onMounted(() => {
    fetchDisciplines()
})
</script>
