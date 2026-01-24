<template>
    <v-card border flat class="pa-4">
        <div class="d-flex justify-space-between align-center mb-4">
            <div class="text-h6">Semesters</div>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openSemesterDialog()">Add Semester</v-btn>
        </div>

        <v-data-table
            :headers="semesterHeaders"
            :items="semesters"
            :loading="loadingSemesters"
            density="compact"
        >
            <template v-slot:item.calendar_events="{ item }">
                <div v-for="event in item.calendar_events" :key="event.id" class="text-caption">
                    {{ event.name }} ({{ event.start_date }} - {{ event.end_date }})
                </div>
                <span v-if="!item.calendar_events?.length" class="text-caption text-medium-emphasis">No events</span>
            </template>
            <template v-slot:item.actions="{ item }">
                <v-btn icon="mdi-pencil" size="small" variant="text" @click="openSemesterDialog(item)"></v-btn>
                <v-btn icon="mdi-delete" size="small" variant="text" color="error" @click="deleteSemester(item)"></v-btn>
            </template>
        </v-data-table>
    </v-card>

    <!-- Semester Dialog -->
    <v-dialog v-model="semesterDialog" max-width="500">
        <v-card>
            <v-card-title>{{ editingSemester ? 'Edit Semester' : 'Add Semester' }}</v-card-title>
            <v-card-text>
                <v-row>
                    <v-col cols="6">
                        <v-text-field
                            v-if="!editingSemester"
                            v-model.number="semesterData.id"
                            label="Semester ID"
                            type="number"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.name"
                            label="Semester Name"
                            variant="outlined"
                            density="compact"
                            placeholder="e.g. Autumn 2025"
                        ></v-text-field>
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.start_date"
                            label="Start Date"
                            type="date"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                    <v-col cols="6">
                        <v-text-field
                            v-model="semesterData.end_date"
                            label="End Date"
                            type="date"
                            variant="outlined"
                            density="compact"
                        ></v-text-field>
                    </v-col>
                </v-row>
                <v-switch
                    v-model="semesterData.is_active"
                    label="Current Semester"
                    color="primary"
                    density="compact"
                ></v-switch>

                <div class="mt-4">
                    <div class="d-flex justify-space-between align-center mb-2">
                        <div class="text-subtitle-2">Academic Events</div>
                        <v-btn size="x-small" color="primary" variant="text" prepend-icon="mdi-plus" @click="openEventDialog()">Add Event</v-btn>
                    </div>
                    <v-divider class="mb-2"></v-divider>
                    <v-list density="compact" class="pa-0">
                        <v-list-item v-for="(event, index) in semesterData.calendar_events" :key="index" border class="mb-1 rounded">
                            <v-list-item-title class="text-body-2">{{ event.name }}</v-list-item-title>
                            <v-list-item-subtitle class="text-caption">{{ event.start_date }} to {{ event.end_date }}</v-list-item-subtitle>
                            <template v-slot:append>
                                <v-btn icon="mdi-pencil" size="x-small" variant="text" @click="openEventDialog(event, index)"></v-btn>
                                <v-btn icon="mdi-delete" size="x-small" variant="text" color="error" @click="deleteEvent(event, index)"></v-btn>
                            </template>
                        </v-list-item>
                        <div v-if="!semesterData.calendar_events?.length" class="text-center py-2 text-caption text-medium-emphasis border rounded border-dashed">
                            No academic events added yet
                        </div>
                    </v-list>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="semesterDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveSemester" :loading="savingSemester">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>

    <!-- Event Dialog -->
    <v-dialog v-model="eventDialog" max-width="400">
        <v-card>
            <v-card-title>{{ editingEvent ? 'Edit Event' : 'Add Academic Event' }}</v-card-title>
            <v-card-text>
                <v-text-field
                    v-model="eventData.name"
                    label="Event Name"
                    variant="outlined"
                    density="compact"
                    placeholder="e.g. Registration, Mid-Sem Break"
                ></v-text-field>
                <v-text-field
                    v-model="eventData.start_date"
                    label="Start Date"
                    type="date"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
                <v-text-field
                    v-model="eventData.end_date"
                    label="End Date"
                    type="date"
                    variant="outlined"
                    density="compact"
                ></v-text-field>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn variant="text" @click="eventDialog = false">Cancel</v-btn>
                <v-btn color="primary" @click="saveEvent" :loading="savingEvent">Save Event</v-btn>
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

// Semesters
const semesters = ref([])
const loadingSemesters = ref(false)
const semesterDialog = ref(false)
const semesterData = ref({ id: null, name: '', start_date: '', end_date: '', is_active: false, calendar_events: [] })
const editingSemester = ref(false)
const savingSemester = ref(false)
const snackbar = ref({ show: false, text: '', color: 'success' })

const semesterHeaders = [
    { title: 'Semester ID', key: 'id' },
    { title: 'Name', key: 'name' },
    { title: 'Start Date', key: 'start_date' },
    { title: 'End Date', key: 'end_date' },
    { title: 'Events', key: 'calendar_events', sortable: false },
    { title: 'Actions', key: 'actions', sortable: false }
]

// Academic Events Management (Nested)
const eventDialog = ref(false)
const eventData = ref({ name: '', start_date: '', end_date: '' })
const editingEvent = ref(false)
const savingEvent = ref(false)
const currentEventIndex = ref(-1)

const fetchSemesters = async () => {
    loadingSemesters.value = true
    try {
        const res = await axios.get('http://localhost:8000/api/v1/academic/semesters/', {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        semesters.value = res.data
    } catch (e) {
        console.error(e)
    } finally {
        loadingSemesters.value = false
    }
}

const openSemesterDialog = (item = null) => {
    if (item) {
        semesterData.value = JSON.parse(JSON.stringify(item))
        editingSemester.value = true
    } else {
        semesterData.value = { id: null, name: '', start_date: '', end_date: '', is_active: false, calendar_events: [] }
        editingSemester.value = false
    }
    semesterDialog.value = true
}

const saveSemester = async () => {
    savingSemester.value = true
    try {
        if (editingSemester.value) {
            await axios.put(`http://localhost:8000/api/v1/academic/semesters/${semesterData.value.id}`, semesterData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
        } else {
            const res = await axios.post('http://localhost:8000/api/v1/academic/semesters/', semesterData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            const semesterId = res.data.id
            for (const event of semesterData.value.calendar_events) {
                await axios.post('http://localhost:8000/api/v1/academic/events/', { ...event, semester_id: semesterId }, {
                    headers: { Authorization: `Bearer ${auth.token}` }
                })
            }
        }
        snackbar.value = { show: true, text: 'Semester saved successfully', color: 'success' }
        semesterDialog.value = false
        fetchSemesters()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to save semester: ' + (e.response?.data?.detail || e.message), color: 'error' }
    } finally {
        savingSemester.value = false
    }
}

const deleteSemester = async (item) => {
    if (!confirm(`Are you sure you want to delete semester ${item.id}?`)) return
    try {
        await axios.delete(`http://localhost:8000/api/v1/academic/semesters/${item.id}`, {
            headers: { Authorization: `Bearer ${auth.token}` }
        })
        snackbar.value = { show: true, text: 'Semester deleted', color: 'success' }
        fetchSemesters()
    } catch (e) {
        snackbar.value = { show: true, text: 'Failed to delete: ' + (e.response?.data?.detail || e.message), color: 'error' }
    }
}

const openEventDialog = (item = null, index = -1) => {
    if (item) {
        eventData.value = { ...item }
        editingEvent.value = true
        currentEventIndex.value = index
    } else {
        eventData.value = { name: '', start_date: '', end_date: '' }
        editingEvent.value = false
        currentEventIndex.value = -1
    }
    eventDialog.value = true
}

const saveEvent = async () => {
    if (editingSemester.value && eventData.value.id) {
        savingEvent.value = true
        try {
            await axios.put(`http://localhost:8000/api/v1/academic/events/${eventData.value.id}`, eventData.value, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            const idx = semesterData.value.calendar_events.findIndex(e => e.id === eventData.value.id)
            if (idx !== -1) semesterData.value.calendar_events[idx] = { ...eventData.value }
            eventDialog.value = false
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to save event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingEvent.value = false
        }
    } else if (editingSemester.value && !eventData.value.id) {
        savingEvent.value = true
        try {
            const res = await axios.post('http://localhost:8000/api/v1/academic/events/', {
                ...eventData.value,
                semester_id: semesterData.value.id
            }, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            semesterData.value.calendar_events.push(res.data)
            eventDialog.value = false
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to create event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        } finally {
            savingEvent.value = false
        }
    } else {
        if (currentEventIndex.value !== -1) {
            semesterData.value.calendar_events[currentEventIndex.value] = { ...eventData.value }
        } else {
            semesterData.value.calendar_events.push({ ...eventData.value })
        }
        eventDialog.value = false
    }
}

const deleteEvent = async (item, index) => {
    if (!confirm(`Are you sure you want to delete event ${item.name}?`)) return
    if (editingSemester.value && item.id) {
        try {
            await axios.delete(`http://localhost:8000/api/v1/academic/events/${item.id}`, {
                headers: { Authorization: `Bearer ${auth.token}` }
            })
            semesterData.value.calendar_events.splice(index, 1)
        } catch (e) {
            snackbar.value = { show: true, text: 'Failed to delete event: ' + (e.response?.data?.detail || e.message), color: 'error' }
        }
    } else {
        semesterData.value.calendar_events.splice(index, 1)
    }
}

onMounted(() => {
    fetchSemesters()
})
</script>
